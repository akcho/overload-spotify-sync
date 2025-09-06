#!/usr/bin/env python3
"""
Overload Spotify Sync
Fetches music posts from r/theoverload and adds them to a Spotify playlist
"""

import praw
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import time
from dotenv import load_dotenv
from config import Config
import yt_dlp
import requests
from bs4 import BeautifulSoup
import json

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('overload_spotify_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OverloadSpotifySync:
    def __init__(self, debug=False):
        self.config = Config()
        self.debug = debug or os.getenv('DEBUG') == '1'
        
        if self.debug:
            logger.setLevel(logging.DEBUG)
        
        # Reddit API setup
        self.reddit = praw.Reddit(
            client_id=self.config.reddit_client_id,
            client_secret=self.config.reddit_client_secret,
            user_agent='overload-spotify-sync/1.0'
        )
        
        # Spotify API setup
        self.spotify = self.setup_spotify_client()
        
    def setup_spotify_client(self):
        """Setup Spotify client with refresh token support for GitHub Actions"""
        refresh_token = os.getenv('SPOTIFY_REFRESH_TOKEN')
        
        if refresh_token and refresh_token.strip():
            logger.info("Using refresh token for headless authentication")
            
            try:
                # Create auth manager
                auth_manager = SpotifyOAuth(
                    client_id=self.config.spotify_client_id,
                    client_secret=self.config.spotify_client_secret,
                    redirect_uri=self.config.spotify_redirect_uri,
                    scope='playlist-modify-public playlist-modify-private'
                )
                
                # Use the refresh token to get a fresh access token
                import requests
                token_url = "https://accounts.spotify.com/api/token"
                
                data = {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': self.config.spotify_client_id,
                    'client_secret': self.config.spotify_client_secret
                }
                
                response = requests.post(token_url, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    logger.info("Successfully refreshed access token")
                    
                    # Create the token info structure that spotipy expects
                    token_info = {
                        'access_token': token_data['access_token'],
                        'token_type': token_data['token_type'],
                        'expires_in': token_data['expires_in'],
                        'expires_at': int(time.time()) + token_data['expires_in'],
                        'scope': token_data.get('scope', 'playlist-modify-public playlist-modify-private'),
                        'refresh_token': token_data.get('refresh_token', refresh_token)  # Use new refresh token if provided
                    }
                    
                    # Set the token info on the auth manager
                    auth_manager.token_info = token_info
                    
                    # Create Spotify client
                    spotify_client = spotipy.Spotify(auth_manager=auth_manager)
                    
                    # Test the connection
                    try:
                        user_info = spotify_client.current_user()
                        logger.info(f"Successfully authenticated as: {user_info.get('display_name', user_info.get('id', 'Unknown'))}")
                        return spotify_client
                    except Exception as test_error:
                        logger.error(f"Token is valid but API test failed: {test_error}")
                        if os.getenv('GITHUB_ACTIONS'):
                            raise Exception(f"Spotify API test failed in GitHub Actions: {test_error}")
                        # In local development, fall back to interactive auth
                else:
                    logger.error(f"Token refresh failed with status {response.status_code}: {response.text}")
                    if os.getenv('GITHUB_ACTIONS'):
                        raise Exception(f"Token refresh failed in GitHub Actions: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"Refresh token authentication failed: {e}")
                # In GitHub Actions, we should fail here rather than falling back to interactive
                if os.getenv('GITHUB_ACTIONS'):
                    raise Exception(f"Authentication failed in GitHub Actions environment: {e}")
        
        logger.info("Using interactive authentication (local development only)")
        # Use standard OAuth flow for local development
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.config.spotify_client_id,
            client_secret=self.config.spotify_client_secret,
            redirect_uri=self.config.spotify_redirect_uri,
            scope='playlist-modify-public playlist-modify-private'
        ))
        
    def get_recent_posts(self) -> List[Dict]:
        """Fetch recent posts from r/theoverload with minimum upvotes"""
        posts = []
        subreddit = self.reddit.subreddit('theoverload')
        
        # Get posts from the last day (or week for testing)
        time_window = int(os.getenv('TIME_WINDOW_DAYS', '1'))
        cutoff_date = datetime.now() - timedelta(days=time_window)
        logger.info(f"Looking for posts from last {time_window} day(s)")
        
        for submission in subreddit.new(limit=100):
            created_time = datetime.fromtimestamp(submission.created_utc)
            
            if created_time < cutoff_date:
                continue
                
            if submission.score >= self.config.min_upvotes:
                posts.append({
                    'title': submission.title,
                    'url': submission.url,
                    'score': submission.score,
                    'id': submission.id,
                    'created': created_time,
                    'submission': submission  # Keep submission object for comment access
                })
                
        logger.info(f"Found {len(posts)} posts with {self.config.min_upvotes}+ upvotes")
        return posts
    
    def is_discussion_thread(self, submission) -> bool:
        """Check if a submission qualifies as a discussion thread based on 3 criteria:
        1. Comment count > 20
        2. Post upvotes > 5 
        3. Over 25% of comments contain URLs or dashes (track indicators)
        """
        # Criterion 1: Comment count > 20
        if submission.num_comments <= 20:
            return False
            
        # Criterion 2: Post upvotes > 5
        if submission.score <= 5:
            return False
            
        # Criterion 3: Calculate track sharing density
        try:
            track_density = self.calculate_track_sharing_density(submission)
            if track_density < 0.25:  # Less than 25%
                return False
                
            logger.info(f"  → Discussion thread detected: {submission.num_comments} comments, "
                       f"{submission.score} upvotes, {track_density:.1%} track sharing density")
            return True
            
        except Exception as e:
            logger.debug(f"  → Error checking track density: {e}")
            return False
    
    def calculate_track_sharing_density(self, submission) -> float:
        """Calculate percentage of comments containing URLs or dashes (track indicators)"""
        try:
            # Get a sample of comments efficiently (don't load all nested comments)
            submission.comments.replace_more(limit=5)  # Limited to avoid performance issues
            all_comments = submission.comments.list()
            
            if not all_comments:
                return 0.0
                
            track_indicating_comments = 0
            total_comments = len(all_comments)
            
            for comment in all_comments:
                if hasattr(comment, 'body') and comment.body:
                    comment_text = comment.body.lower()
                    # Check for URLs or dash patterns indicating track sharing
                    has_url = any(domain in comment_text for domain in [
                        'youtube.com', 'youtu.be', 'spotify.com', 'soundcloud.com', 
                        'bandcamp.com', 'http', 'www.'
                    ])
                    has_dash = ' - ' in comment_text
                    has_by = ' by ' in comment_text
                    
                    if has_url or has_dash or has_by:
                        track_indicating_comments += 1
            
            density = track_indicating_comments / total_comments if total_comments > 0 else 0.0
            logger.debug(f"  → Track sharing density: {track_indicating_comments}/{total_comments} = {density:.1%}")
            return density
            
        except Exception as e:
            logger.debug(f"  → Error calculating track density: {e}")
            return 0.0
    
    def get_comments_from_discussion_threads(self, posts: List[Dict]) -> List[Dict]:
        """Extract comments from posts that qualify as discussion threads"""
        comments_data = []
        
        for post in posts:
            submission = post['submission']
            
            if self.is_discussion_thread(submission):
                logger.info(f"Processing discussion thread: {post['title'][:50]}...")
                
                try:
                    # Get comments with limited depth for performance
                    submission.comments.replace_more(limit=10)
                    all_comments = submission.comments.list()
                    
                    # Filter comments by upvote threshold
                    min_comment_upvotes = int(os.getenv('MIN_COMMENT_UPVOTES', '3'))
                    qualifying_comments = [
                        comment for comment in all_comments 
                        if (hasattr(comment, 'score') and comment.score >= min_comment_upvotes and
                            hasattr(comment, 'body') and comment.body and 
                            len(comment.body.strip()) > 10)  # Avoid very short comments
                    ]
                    
                    logger.info(f"  → Found {len(qualifying_comments)} comments with {min_comment_upvotes}+ upvotes")
                    
                    for comment in qualifying_comments:
                        comments_data.append({
                            'body': comment.body,
                            'score': comment.score,
                            'id': comment.id,
                            'parent_post_title': post['title'],
                            'parent_post_id': post['id']
                        })
                        
                except Exception as e:
                    logger.error(f"  → Error processing comments: {e}")
                    continue
        
        logger.info(f"Total qualifying comments from discussion threads: {len(comments_data)}")
        return comments_data
    
    def extract_music_info_from_comment(self, comment: Dict) -> Optional[Dict]:
        """Extract artist and track info from comment text"""
        comment_text = comment['body']
        
        # Clean common comment prefixes/suffixes
        cleaned_text = self.process_comment_text(comment_text)
        
        # Try to extract URLs first
        url_match = re.search(r'(https?://[^\s\)]+)', cleaned_text)
        if url_match:
            url = url_match.group(1)
            # Use existing URL extraction logic
            fake_post = {'url': url, 'title': cleaned_text}
            music_info = self.extract_music_info(fake_post)
            if music_info:
                music_info['source'] = 'comment_url'
                music_info['comment_score'] = comment['score']
                return music_info
        
        # Try to extract from text using existing title parsing
        music_info = self.extract_from_title(cleaned_text)
        if music_info:
            music_info['source'] = 'comment_text'
            music_info['comment_score'] = comment['score']
            return music_info
        
        return None
    
    def process_comment_text(self, text: str) -> str:
        """Clean comment text for track extraction"""
        # Remove common prefixes
        prefixes_to_remove = [
            r'^check\s+out\s*:?\s*',
            r'^listening\s+to\s*:?\s*', 
            r'^currently\s+playing\s*:?\s*',
            r'^now\s+playing\s*:?\s*',
            r'^this\s+is\s+good\s*:?\s*',
            r'^recommend\s*:?\s*',
            r'^try\s+this\s*:?\s*'
        ]
        
        cleaned = text.strip()
        for pattern in prefixes_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove quotes and clean up
        cleaned = cleaned.strip('"\'')
        
        return cleaned
    
    def extract_music_info(self, post: Dict) -> Optional[Dict]:
        """Extract artist and track info from various music platforms"""
        url = post['url']
        title = post['title']
        
        # Skip posts that are clearly not about music
        if self.is_non_music_post(title):
            logger.info(f"  → Skipping non-music post")
            return None
        
        # YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            return self.extract_youtube_info(url, title)
        
        # Spotify
        elif 'spotify.com' in url:
            return self.extract_spotify_info(url)
        
        # SoundCloud
        elif 'soundcloud.com' in url:
            return self.extract_soundcloud_info(url, title)
        
        # Bandcamp
        elif 'bandcamp.com' in url:
            return self.extract_bandcamp_info(url, title)
        
        # Try to parse from title if no recognized URL
        else:
            return self.extract_from_title(title)
    
    def is_non_music_post(self, title: str) -> bool:
        """Check if post is clearly not about music"""
        title_lower = title.lower()
        
        # Common patterns that indicate non-music posts
        non_music_patterns = [
            # Questions and discussions
            r'\b(what|who|where|when|why|how|does|anyone|any\s+\w+\s+heads)\b',
            r'\b(question|help|looking\s+for|recommend|suggestion)\b',
            r'\b(thoughts|opinion|discussion|thread|post)\b',
            
            # Event announcements  
            r'\b(tonight|today|tomorrow|this\s+weekend|next\s+week)\b',
            r'\b(event|show|concert|festival|party|club|venue)\b',
            r'\b(tickets|sold\s+out|presale)\b',
            
            # Generic/vague titles
            r'\b(tracks?\s+that|music\s+that|songs?\s+that)\b',
            r'\b(playlist|mix|set)\s+(for|that|to)\b',
            
            # Meta/community posts
            r'\b(this\s+sub|subreddit|community|weekly|daily)\b',
            r'\b(rules|guidelines|announcement)\b',
            
            # Descriptive remix posts (not actual remix titles)
            r'^A\s+\w+[\w\-]*\s+remix\s+of\s+',  # "A house remix of...", "A trip-hop remix of..."
            r'^An\s+\w+[\w\-]*\s+remix\s+of\s+', # "An electronic remix of..."
        ]
        
        for pattern in non_music_patterns:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return True
                
        return False
    
    def extract_youtube_info(self, url: str, title: str) -> Optional[Dict]:
        """Extract info from YouTube URL using yt-dlp for accurate metadata"""
        
        # First try to get metadata directly from YouTube
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                yt_title = info.get('title', '').strip()
                uploader = info.get('uploader', '').strip()
                
                if yt_title:
                    if self.debug:
                        logger.debug(f"YouTube metadata - Title: {yt_title}, Uploader: {uploader}")
                    
                    # Use YouTube title for parsing instead of post title
                    title_to_parse = yt_title
                else:
                    # Fall back to post title
                    title_to_parse = title
                    
        except Exception as e:
            if self.debug:
                logger.debug(f"Failed to extract YouTube metadata: {e}")
            # Fall back to post title
            title_to_parse = title
        
        # Check for remix patterns and extract remix info
        remix_info = self.extract_remix_info(title_to_parse)
        
        # Clean title by removing remix information for main parsing
        clean_title = self.clean_title_for_parsing(title_to_parse)
        
        # Common patterns for artist - track in titles
        patterns = [
            r'^(.+?)\s*[-–—]\s*(.+)$',           # Artist - Track
            r'^(.+?)\s*:\s*(.+)$',               # Artist: Track  
            r'^(.+?)\s+by\s+(.+)$',              # Track by Artist
            r'^\[(.+?)\]\s*(.+)$',               # [Artist] Track
            r'^(.+?)\s*\|\s*(.+)$',              # Artist | Track
            r'^(.+?)\s*"(.+?)"',                 # Artist "Track"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, clean_title.strip(), re.IGNORECASE)
            if match:
                result = {
                    'artist': match.group(1).strip(),
                    'track': match.group(2).strip(),
                    'source': 'youtube'
                }
                # Add remix information
                result.update(remix_info)
                return result
        
        # Fallback: assume title is track name
        result = {
            'artist': '',
            'track': clean_title.strip(),
            'source': 'youtube'
        }
        result.update(remix_info)
        return result
    
    def extract_spotify_info(self, url: str) -> Optional[Dict]:
        """Extract info from Spotify URL"""
        try:
            # Extract Spotify track ID from URL
            match = re.search(r'spotify\.com/track/([a-zA-Z0-9]+)', url)
            if match:
                track_id = match.group(1)
                track = self.spotify.track(track_id)
                return {
                    'artist': track['artists'][0]['name'],
                    'track': track['name'],
                    'source': 'spotify',
                    'spotify_id': track_id
                }
        except Exception as e:
            logger.warning(f"Failed to extract Spotify info: {e}")
        
        return None
    
    def extract_soundcloud_info(self, url: str, title: str) -> Optional[Dict]:
        """Extract info from SoundCloud (similar to YouTube)"""
        return self.extract_youtube_info(url, title)
    
    def extract_bandcamp_info(self, url: str, title: str) -> Optional[Dict]:
        """Extract info from Bandcamp URL using web scraping for accurate metadata"""
        
        # First try to get metadata directly from Bandcamp
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for structured data in script tags
                script_tags = soup.find_all('script', type='application/ld+json')
                
                for script in script_tags:
                    try:
                        data = json.loads(script.string)
                        if '@type' in data and data['@type'] == 'MusicRecording':
                            track_name = data.get('name', '').strip()
                            artist_name = None
                            
                            # Look for artist in byArtist
                            if 'byArtist' in data:
                                if isinstance(data['byArtist'], dict):
                                    artist_name = data['byArtist'].get('name', '').strip()
                                elif isinstance(data['byArtist'], list) and len(data['byArtist']) > 0:
                                    artist_name = data['byArtist'][0].get('name', '').strip()
                            
                            if track_name:
                                if self.debug:
                                    logger.debug(f"Bandcamp metadata - Artist: {artist_name}, Track: {track_name}")
                                
                                # Check for remix info in track name
                                remix_info = self.extract_remix_info(track_name)
                                
                                result = {
                                    'artist': artist_name or '',
                                    'track': track_name,
                                    'source': 'bandcamp'
                                }
                                result.update(remix_info)
                                return result
                                
                    except json.JSONDecodeError:
                        continue
                
                # Fallback: try to extract from page title
                title_tag = soup.find('title')
                if title_tag:
                    page_title = title_tag.get_text().strip()
                    
                    # Bandcamp titles are often "Track | Artist"
                    if ' | ' in page_title:
                        parts = page_title.split(' | ')
                        if len(parts) >= 2:
                            track_name = parts[0].strip()
                            artist_name = parts[1].strip()
                            
                            if self.debug:
                                logger.debug(f"Bandcamp fallback - Artist: {artist_name}, Track: {track_name}")
                            
                            remix_info = self.extract_remix_info(track_name)
                            
                            result = {
                                'artist': artist_name,
                                'track': track_name,
                                'source': 'bandcamp'
                            }
                            result.update(remix_info)
                            return result
                            
        except Exception as e:
            if self.debug:
                logger.debug(f"Failed to extract Bandcamp metadata: {e}")
        
        # Fall back to parsing the post title like YouTube
        remix_info = self.extract_remix_info(title)
        clean_title = self.clean_title_for_parsing(title)
        
        # Try common patterns
        patterns = [
            r'^(.+?)\s*[-–—]\s*(.+)$',           # Artist - Track
            r'^(.+?)\s*:\s*(.+)$',               # Artist: Track  
            r'^(.+?)\s+by\s+(.+)$',              # Track by Artist
            r'^\[(.+?)\]\s*(.+)$',               # [Artist] Track
            r'^(.+?)\s*\|\s*(.+)$',              # Artist | Track
        ]
        
        for pattern in patterns:
            match = re.match(pattern, clean_title.strip(), re.IGNORECASE)
            if match:
                result = {
                    'artist': match.group(1).strip(),
                    'track': match.group(2).strip(),
                    'source': 'bandcamp'
                }
                result.update(remix_info)
                return result
        
        # Final fallback
        result = {
            'artist': '',
            'track': clean_title.strip(),
            'source': 'bandcamp'
        }
        result.update(remix_info)
        return result
    
    def extract_from_title(self, title: str) -> Optional[Dict]:
        """Try to extract artist/track from Reddit post title"""
        return self.extract_youtube_info('', title)
    
    def extract_remix_info(self, title: str) -> Dict:
        """Extract remix information from title"""
        remix_patterns = [
            # (Remixer Remix) - but not if remixer contains "not"
            r'\((.+?)\s+(remix|mix|edit|rework|vip|bootleg|flip)\)',
            # [Remixer Remix]
            r'\[(.+?)\s+(remix|mix|edit|rework|vip|bootleg|flip)\]',
            # feat./ft. patterns
            r'feat\.?\s+(.+?)\s*[\(\[](.+?)\s+(remix|mix|edit|rework|vip|bootleg|flip)[\)\]]',
            r'ft\.?\s+(.+?)\s*[\(\[](.+?)\s+(remix|mix|edit|rework|vip|bootleg|flip)[\)\]]',
        ]
        
        for pattern in remix_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Simple (Remixer Type) pattern
                    remixer = match.group(1).strip()
                    remix_type = match.group(2).strip()
                    
                    # Skip false positives
                    if self.is_false_positive_remix(remixer, remix_type):
                        continue
                    
                    return {
                        'is_remix': True,
                        'remixer': remixer,
                        'remix_type': remix_type.lower(),
                        'original_artist': None,
                        'original_track': None
                    }
                elif len(match.groups()) == 3:  # feat. pattern
                    featured_artist = match.group(1).strip()
                    remixer = match.group(2).strip()
                    remix_type = match.group(3).strip()
                    
                    # Skip false positives
                    if self.is_false_positive_remix(remixer, remix_type):
                        continue
                        
                    return {
                        'is_remix': True,
                        'remixer': remixer,
                        'remix_type': remix_type.lower(),
                        'featured_artist': featured_artist,
                        'original_artist': None,
                        'original_track': None
                    }
        
        return {
            'is_remix': False,
            'remixer': None,
            'remix_type': None,
            'featured_artist': None,
            'original_artist': None,
            'original_track': None
        }
    
    def is_false_positive_remix(self, remixer: str, remix_type: str) -> bool:
        """Check if this is a false positive remix detection"""
        remixer_lower = remixer.lower()
        remix_type_lower = remix_type.lower()
        
        # Skip if remixer contains negative words (but "Not" in artist names like "What So Not" is OK)
        negative_phrases = ['something not a', 'not a remix', 'not remix', 'no remix', 'never remix']
        if any(phrase in remixer_lower for phrase in negative_phrases):
            return True
            
        # Skip "Original Mix" - this is typically not a remix
        if remixer_lower == 'original' and remix_type_lower == 'mix':
            return True
            
        # Skip common false positives (exact matches only)
        false_positives = [
            'radio edit',
            'extended mix',
            'club mix',
            'original mix',
            'vocal mix',
            'instrumental mix',
        ]
        
        full_text = f"{remixer_lower} {remix_type_lower}"
        if full_text in false_positives:
            return True
            
        return False
    
    def clean_title_for_parsing(self, title: str) -> str:
        """Remove remix information and metadata to get clean artist - track"""
        # Remove remix patterns first
        remix_patterns = [
            r'\s*[\(\[].*?(remix|mix|edit|rework|vip|bootleg|flip).*?[\)\]]',
            r'\s*[\(\[].*?remix.*?[\)\]]',  # catch variations
        ]
        
        clean_title = title
        for pattern in remix_patterns:
            clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
        
        # Remove common metadata patterns
        metadata_patterns = [
            r'\s*\[.*?\d{4}.*?\]',  # [Label, 2000] or [2000]
            r'\s*\(.*?\d{4}.*?\)',  # (Label, 2000) or (2000)  
            r'\s*\[.*?Records.*?\]',  # [Some Records]
            r'\s*\(.*?Records.*?\)',  # (Some Records)
            r'\s*\[.*?Label.*?\]',   # [Some Label]
            r'\s*\(.*?Label.*?\)',   # (Some Label)
        ]
        
        for pattern in metadata_patterns:
            clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
        
        return clean_title.strip()
    
    def search_spotify(self, music_info: Dict) -> Optional[str]:
        """Search for track on Spotify and return track ID"""
        if music_info.get('spotify_id'):
            return music_info['spotify_id']
        
        artist = music_info.get('artist', '')
        track = music_info.get('track', '')
        is_remix = music_info.get('is_remix', False)
        remixer = music_info.get('remixer', '')
        remix_type = music_info.get('remix_type', '')
        
        if not track:
            return None
        
        # Build search queries with remix-aware strategy
        search_queries = self.build_search_queries(artist, track, is_remix, remixer, remix_type)
        
        for query in search_queries:
            try:
                results = self.spotify.search(q=query, type='track', limit=20)
                
                if results['tracks']['items']:
                    # For remixes, try to find the best match
                    if is_remix:
                        best_match = self.find_best_remix_match(results['tracks']['items'], 
                                                              artist, track, remixer, remix_type)
                        if best_match:
                            track_id = best_match['id']
                            found_artist = best_match['artists'][0]['name']
                            found_track = best_match['name']
                            
                            remix_info = f" ({remixer} {remix_type})" if remixer and remix_type else " (remix)"
                            logger.info(f"Found remix on Spotify: {found_artist} - {found_track}{remix_info}")
                            return track_id
                    else:
                        # Non-remix: validate result quality before accepting
                        best_match = self.find_best_track_match(results['tracks']['items'], artist, track)
                        if best_match:
                            track_id = best_match['id']
                            found_artist = best_match['artists'][0]['name']
                            found_track = best_match['name']
                            
                            logger.info(f"Found on Spotify: {found_artist} - {found_track}")
                            return track_id
                    
            except Exception as e:
                import traceback
                logger.warning(f"Spotify search failed for '{query}': {e}")
                if self.debug:
                    logger.debug(f"Full traceback: {traceback.format_exc()}")
                continue
        
        remix_info = f" ({remixer} {remix_type})" if is_remix and remixer and remix_type else ""
        logger.info(f"Could not find on Spotify: {artist} - {track}{remix_info}")
        return None
    
    def search_spotify_with_fallback(self, music_info: Dict, post: Dict) -> Optional[str]:
        """Search Spotify with fallback strategies when primary search fails"""
        
        # Try primary search first (extracted metadata)
        track_id = self.search_spotify(music_info)
        if track_id:
            return track_id
        
        # If no results, try fallback strategies
        source = music_info.get('source', '')
        original_artist = music_info.get('artist', '')
        original_track = music_info.get('track', '')
        
        if self.debug:
            logger.debug(f"Primary search failed for {original_artist} - {original_track}, trying fallbacks...")
        
        # Fallback 1: Try parsing the original post title instead of extracted metadata
        if source in ['youtube', 'bandcamp']:
            try:
                fallback_info = self.extract_from_title(post['title'])
                if fallback_info:
                    fallback_artist = fallback_info.get('artist', '')
                    fallback_track = fallback_info.get('track', '')
                    
                    # Only try fallback if it's different from what we already tried
                    if (fallback_artist != original_artist or fallback_track != original_track):
                        if self.debug:
                            logger.debug(f"Trying post title fallback: {fallback_artist} - {fallback_track}")
                        
                        track_id = self.search_spotify(fallback_info)
                        if track_id:
                            logger.info(f"✓ Found using post title fallback: {fallback_artist} - {fallback_track}")
                            return track_id
            except Exception as e:
                if self.debug:
                    logger.debug(f"Post title fallback failed: {e}")
        
        # Fallback 2: Try cleaning the extracted metadata (remove label info, etc.)
        cleaned_info = self.clean_metadata_for_search(music_info, post)
        if cleaned_info:
            cleaned_artist = cleaned_info.get('artist', '')
            cleaned_track = cleaned_info.get('track', '')
            
            # Only try if different from original
            if (cleaned_artist != original_artist or cleaned_track != original_track):
                if self.debug:
                    logger.debug(f"Trying cleaned metadata: {cleaned_artist} - {cleaned_track}")
                
                track_id = self.search_spotify(cleaned_info)
                if track_id:
                    logger.info(f"✓ Found using cleaned metadata: {cleaned_artist} - {cleaned_track}")
                    return track_id
        
        return None
    
    def clean_metadata_for_search(self, music_info: Dict, post: Dict) -> Optional[Dict]:
        """Clean metadata by removing label info and other noise"""
        
        artist = music_info.get('artist', '').strip()
        track = music_info.get('track', '').strip()
        post_title = post.get('title', '')
        
        # Common label patterns to detect and extract real artist from
        label_patterns = [
            r'^(.+?)\s*[-–—]\s*(.+?)\s*\[(.+?)\]',  # "Artist - Track [Label]" -> try "Artist - Track"
            r'^(.+?)\s*[-–—]\s*(.+?)\s*\((.+?)\s*Records?\)',  # "Artist - Track (Label Records)"
            r'^(.+?)\s+Records?\s*[-–—]\s*(.+)',   # "Label Records - Track" -> try from post title
            r'^(.+?)\s+Recordings?\s*[-–—]\s*(.+)',  # "Label Recordings - Track"
        ]
        
        cleaned_info = None
        
        # Try to detect if artist looks like a label
        for pattern in label_patterns:
            match = re.match(pattern, f"{artist} - {track}", re.IGNORECASE)
            if match:
                if self.debug:
                    logger.debug(f"Detected label pattern, trying to extract from post title: '{post_title}'")
                
                # Try to extract real artist/track from post title
                title_patterns = [
                    r'^(.+?)\s*[-–—]\s*(.+?)\s*\[',  # "Artist - Track [anything]"
                    r'^(.+?)\s*[-–—]\s*(.+?)$',      # "Artist - Track"
                ]
                
                for title_pattern in title_patterns:
                    title_match = re.match(title_pattern, post_title.strip(), re.IGNORECASE)
                    if title_match:
                        potential_artist = title_match.group(1).strip()
                        potential_track = title_match.group(2).strip()
                        
                        # Clean up track name (remove label info, year, etc.)
                        potential_track = re.sub(r'\s*\[.*?\]$', '', potential_track)
                        potential_track = re.sub(r'\s*\(.*?\)$', '', potential_track) 
                        
                        if potential_artist and potential_track:
                            cleaned_info = music_info.copy()
                            cleaned_info['artist'] = potential_artist
                            cleaned_info['track'] = potential_track
                            break
                break
        
        return cleaned_info
    
    def normalize_for_matching(self, text: str) -> str:
        """Normalize text for matching (remove spaces, punctuation, etc.)"""
        import re
        # Remove spaces, punctuation, convert to lowercase
        normalized = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        return normalized
    
    def is_clean_title(self, title: str) -> bool:
        """Check if a title is 'clean' (no version/remix info)"""
        title_lower = title.lower()
        
        # If it already has version indicators, it's not clean
        version_indicators = [
            'remix', 'mix', 'edit', 'version', 'rework', 'vip', 'bootleg', 
            'extended', 'radio', 'instrumental', 'acapella', 'live',
            'remaster', 'remastered', 'deluxe', 'special', 'alternate'
        ]
        
        for indicator in version_indicators:
            if indicator in title_lower:
                return False
                
        # If it has parentheses or brackets with content, likely has version info
        if re.search(r'\[.+\]|\(.+\)', title):
            return False
            
        return True
    
    def has_version_suffix(self, spotify_title: str) -> bool:
        """Check if Spotify title has version/label suffix that wasn't in original query"""
        spotify_lower = spotify_title.lower()
        
        # Common version patterns in Spotify titles
        version_patterns = [
            r'-\s+(.*?)\s+(version|mix|edit|remix)',  # " - Something Version/Mix"
            r'-\s+(extended|radio|instrumental|live)',  # " - Extended/Radio/etc"
            r'-\s+(remaster|remastered|deluxe)',       # " - Remastered/Deluxe"
            r'\(\s*(.*?)\s*(version|mix|edit)\s*\)',   # "(Something Version)"
        ]
        
        for pattern in version_patterns:
            if re.search(pattern, spotify_lower):
                return True
                
        return False
    
    def build_search_queries(self, artist: str, track: str, is_remix: bool, remixer: str, remix_type: str) -> List[str]:
        """Build prioritized search queries based on remix status"""
        queries = []
        
        if is_remix and remixer and remix_type:
            # Remix-specific queries (highest priority)
            if artist:
                queries.extend([
                    f'artist:"{artist}" track:"{track}" "{remixer}" {remix_type}',
                    f'"{artist}" "{track}" "{remixer}" {remix_type}',
                    f'artist:"{artist}" "{remixer}" {remix_type}',
                    f'"{track}" "{remixer}" {remix_type}',
                ])
            else:
                queries.extend([
                    f'track:"{track}" "{remixer}" {remix_type}',
                    f'"{track}" "{remixer}" {remix_type}',
                ])
        
        # Standard queries (fallback or non-remix)
        if artist:
            queries.extend([
                f'artist:"{artist}" track:"{track}"',
                f'"{artist}" "{track}"',
                f'artist:{artist} {track}',
                f'{artist} {track}',
                # More flexible artist matching
                artist.split()[0] + ' ' + track if len(artist.split()) > 1 else None,
                # Try without quotes
                artist + ' ' + track,
            ])
        
        # Track-only searches as last resort
        queries.extend([
            f'track:"{track}"',
            f'"{track}"',
            track
        ])
        
        # Remove None values
        return [q for q in queries if q is not None]
    
    def find_best_remix_match(self, tracks: List[Dict], artist: str, track: str, remixer: str, remix_type: str) -> Optional[Dict]:
        """Find the best matching remix from search results"""
        # Score tracks based on how well they match the remix criteria
        scored_tracks = []
        
        for spotify_track in tracks:
            score = 0
            track_name = spotify_track['name'].lower()
            artist_names = [a['name'].lower() for a in spotify_track['artists']]
            
            # Check if remixer appears in track name or artists
            if remixer and remixer.lower() in track_name:
                score += 5
            if remixer and any(remixer.lower() in artist_name for artist_name in artist_names):
                score += 5
                
            # Check if remix type appears in track name
            if remix_type and remix_type.lower() in track_name:
                score += 3
                
            # Check for general remix indicators
            if any(indicator in track_name for indicator in ['remix', 'mix', 'edit', 'rework', 'vip']):
                score += 2
                
            # Check if original artist matches
            if artist and any(artist.lower() in artist_name for artist_name in artist_names):
                score += 2
                
            # Check if original track name is in the title
            if track and track.lower() in track_name:
                score += 1
                
            # Require a higher threshold for remix matches to prevent false positives
            if score >= 5:  # Must have remixer match OR strong original track/artist connection
                scored_tracks.append((score, spotify_track))
        
        # Return highest scoring track only if we have good matches
        if scored_tracks:
            scored_tracks.sort(key=lambda x: x[0], reverse=True)
            return scored_tracks[0][1]
        
        # No fallback for remixes - if we can't find a good remix match, return None
        return None
    
    def find_best_track_match(self, tracks: List[Dict], artist: str, track: str) -> Optional[Dict]:
        """Find the best matching track from search results (non-remix)"""
        if not tracks:
            return None
            
        # If we don't have good artist/track info, be more strict
        if not artist or not track:
            logger.info(f"Insufficient track info for reliable matching: '{artist}' - '{track}'")
            return None
        
        # Only reject if track is extremely short or both are very generic
        if len(track) <= 2 or (len(artist) <= 2 and len(track) <= 3):
            logger.info(f"Track info too vague for reliable matching: '{artist}' - '{track}'")
            return None
            
        # Score tracks based on how well they match
        scored_tracks = []
        
        for spotify_track in tracks:
            score = 0
            track_name = spotify_track['name'].lower()
            artist_names = [a['name'].lower() for a in spotify_track['artists']]
            
            # Strong artist match (multiple strategies)
            if artist:
                artist_lower = artist.lower()
                for artist_name in artist_names:
                    # Direct substring matching
                    if artist_lower in artist_name or artist_name in artist_lower:
                        score += 10
                        break
                    # Try normalized versions (remove spaces/punctuation)
                    elif self.normalize_for_matching(artist_lower) == self.normalize_for_matching(artist_name):
                        score += 10
                        break
                    # Try matching first word of artist (e.g., "Deadmau5" from "Deadmau5 feat. Someone")
                    elif len(artist.split()) > 1 and artist.split()[0].lower() in artist_name:
                        score += 8
                        break
                    # Try partial word matching
                    elif any(word in artist_name for word in artist_lower.split() if len(word) > 3):
                        score += 6
                        break
            
            # Strong track name match - be more strict
            if track and track.lower() in track_name:
                score += 8
                
                # PURE TITLE MATCHING: If query is clean but result has version info, penalize heavily
                if self.is_clean_title(track) and self.has_version_suffix(track_name):
                    score -= 15  # Heavy penalty - should eliminate most matches
                    if self.debug:
                        logger.debug(f"Pure title penalty (-15): '{track}' vs '{track_name}'")
                        
            elif track:
                # Partial track name match (require more substantial overlap)
                track_words = track.lower().split()
                matching_words = sum(1 for word in track_words if word in track_name and len(word) > 3)
                if matching_words >= 2:  # Need at least 2 significant words
                    score += matching_words * 3
                elif matching_words == 1 and len(track_words) == 1:  # Single word exact match
                    score += 4
            
            # Balanced validation - strict artist, more flexible track
            artist_score = 0
            track_score = 0
            
            # STRICT artist matching (prevent wrong artists)
            if artist:
                artist_lower = artist.lower()
                for artist_name in artist_names:
                    # Direct substring matching
                    if artist_lower in artist_name or artist_name in artist_lower:
                        artist_score = 10
                        break
                    # Try normalized versions (remove spaces/punctuation)
                    elif self.normalize_for_matching(artist_lower) == self.normalize_for_matching(artist_name):
                        artist_score = 10
                        break
                    elif len(artist.split()) > 1 and artist.split()[0].lower() in artist_name:
                        artist_score = 8
                        break
                    elif any(word in artist_name for word in artist_lower.split() if len(word) > 3):
                        artist_score = 6
                        break
            
            # MORE FLEXIBLE track matching (handle variations like "Bubblin (2022)" vs "Bubblin")
            if track:
                # Normalize smart quotes and other unicode characters
                def normalize_text(text):
                    # Replace smart apostrophes and quotes with regular ones
                    return text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
                
                track_lower = normalize_text(track.lower())
                track_name_lower = normalize_text(track_name.lower())
                
                # Exact match
                if track_lower in track_name_lower:
                    track_score = 8
                    
                    # Apply pure title penalty in final validation
                    if self.is_clean_title(track) and self.has_version_suffix(spotify_track['name']):
                        track_score -= 15
                        if self.debug:
                            logger.debug(f"Final validation penalty (-15): '{track}' vs '{spotify_track['name']}'")
                            
                # Handle year/version variations - remove common suffixes  
                elif self.tracks_match_with_variations(track_lower, track_name_lower):
                    track_score = 7
                # Word-based matching
                else:
                    track_words = track_lower.split()
                    # For single word tracks, be more lenient
                    if len(track_words) == 1:
                        if track_lower in track_name_lower or any(track_lower in word for word in track_name_lower.split()):
                            track_score = 6
                    # Multi-word tracks need better overlap
                    else:
                        matching_words = sum(1 for word in track_words if word in track_name_lower and len(word) > 3)
                        if matching_words >= len(track_words) * 0.7:  # 70% of words match
                            track_score = matching_words * 2
                        elif matching_words >= 1:
                            track_score = matching_words
            
            # Require GOOD artist match, more flexible track match
            if artist_score < 6:  # Must have good artist match
                if self.debug:
                    logger.debug(f"Rejected {spotify_track['artists'][0]['name']} - {spotify_track['name']}: artist score {artist_score} < 6")
                continue
            if track_score < 2:  # More lenient track requirement
                if self.debug:
                    logger.debug(f"Rejected {spotify_track['artists'][0]['name']} - {spotify_track['name']}: track score {track_score} < 2")
                continue
                
            score = artist_score + track_score
            if self.debug:
                logger.debug(f"Match candidate: {spotify_track['artists'][0]['name']} - {spotify_track['name']} (artist: {artist_score}, track: {track_score}, total: {score})")
                
            scored_tracks.append((score, spotify_track))
        
        if not scored_tracks:
            logger.info(f"No confident matches found for: {artist} - {track}")
            return None
            
        # Return highest scoring track
        scored_tracks.sort(key=lambda x: x[0], reverse=True)
        return scored_tracks[0][1]
    
    def tracks_match_with_variations(self, track1: str, track2: str) -> bool:
        """Check if tracks match allowing for common variations like years, versions, etc."""
        import re
        
        # Normalize smart quotes first
        def normalize_text(text):
            return text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        
        # Remove common variations
        def clean_track(track_text):
            track_text = normalize_text(track_text)  # Normalize smart quotes first
            # Remove years, versions, and common suffixes
            track_text = re.sub(r'\s*\(\d{4}\)\s*', '', track_text)  # (2022)
            track_text = re.sub(r'\s*\[\d{4}\]\s*', '', track_text)  # [2022]
            track_text = re.sub(r'\s*\(remaster\w*\)\s*', '', track_text, flags=re.IGNORECASE)
            track_text = re.sub(r'\s*\(original mix\)\s*', '', track_text, flags=re.IGNORECASE)
            track_text = re.sub(r'\s*\(radio edit\)\s*', '', track_text, flags=re.IGNORECASE)
            return track_text.strip()
        
        clean1 = clean_track(track1)
        clean2 = clean_track(track2)
        
        # Check if cleaned versions match
        return clean1 in clean2 or clean2 in clean1
    
    def get_or_create_playlist(self) -> str:
        """Get existing playlist or create new one"""
        user_id = self.spotify.current_user()['id']
        cache_file = '.playlist_cache'
        
        # Check cache file first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_id = f.read().strip()
                
                # Verify cached playlist still exists and has correct name
                try:
                    cached_playlist = self.spotify.playlist(cached_id)
                    if cached_playlist['name'] == self.config.playlist_name:
                        logger.info(f"Using cached playlist: {cached_playlist['name']} ({cached_id})")
                        return cached_id
                    else:
                        logger.info(f"Cached playlist name changed, ignoring cache")
                except Exception:
                    logger.info(f"Cached playlist no longer exists, ignoring cache")
            except Exception:
                logger.info(f"Could not read playlist cache")
        
        # Search for existing playlist using current_user_playlists
        logger.info(f"Searching for playlist: '{self.config.playlist_name}'")
        playlists = self.spotify.current_user_playlists(limit=50)
        
        page = 1
        while playlists and page <= 5:  # Check first 5 pages
            logger.info(f"Checking page {page} ({len(playlists['items'])} playlists)")
            for playlist in playlists['items']:
                if playlist['name'] == self.config.playlist_name:
                    logger.info(f"Found existing playlist: {playlist['name']} ({playlist['id']})")
                    # Cache the result
                    with open(cache_file, 'w') as f:
                        f.write(playlist['id'])
                    return playlist['id']
                    
            # Check next page if exists  
            if playlists['next'] and page < 5:
                playlists = self.spotify.next(playlists)
                page += 1
            else:
                break
        
        # Create new playlist if not found
        logger.info(f"No existing playlist found, creating new one")
        playlist = self.spotify.user_playlist_create(
            user=user_id,
            name=self.config.playlist_name,
            public=False,
            description="Daily music discoveries from r/theoverload"
        )
        
        # Cache the new playlist ID
        with open(cache_file, 'w') as f:
            f.write(playlist['id'])
        
        logger.info(f"Created new playlist: {playlist['name']} ({playlist['id']})")
        return playlist['id']
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]):
        """Add tracks to playlist (avoiding duplicates)"""
        if not track_ids:
            return
        
        # Get existing tracks in playlist
        existing_tracks = set()
        results = self.spotify.playlist_tracks(playlist_id)
        existing_tracks.update(track['track']['id'] for track in results['items'] if track['track'])
        
        while results['next']:
            results = self.spotify.next(results)
            existing_tracks.update(track['track']['id'] for track in results['items'] if track['track'])
        
        # Filter out duplicates
        new_tracks = [tid for tid in track_ids if tid not in existing_tracks]
        
        if not new_tracks:
            logger.info("No new tracks to add (all tracks already in playlist)")
            return
        
        duplicates_found = len(track_ids) - len(new_tracks)
        if duplicates_found > 0:
            logger.info(f"Skipped {duplicates_found} duplicate track(s)")
        
        # Add tracks in batches of 100 (Spotify limit)
        for i in range(0, len(new_tracks), 100):
            batch = new_tracks[i:i+100]
            self.spotify.playlist_add_items(playlist_id, batch)
            logger.info(f"Added {len(batch)} tracks to playlist")
    
    def run(self):
        """Main execution function"""
        logger.info("Starting Overload to Spotify sync")
        
        try:
            # Get recent posts
            posts = self.get_recent_posts()
            
            if not posts:
                logger.info("No posts found, exiting")
                return
            
            # Extract music info and search Spotify
            track_ids = []
            
            # Process regular posts first
            for post in posts:
                logger.info(f"Processing: {post['title'][:50]}...")
                
                music_info = self.extract_music_info(post)
                if not music_info:
                    continue
                
                # Log remix information if detected
                if music_info.get('is_remix'):
                    remix_info = f"Detected remix: {music_info.get('remixer', 'Unknown')} {music_info.get('remix_type', 'remix')}"
                    logger.info(f"  → {remix_info}")
                
                track_id = self.search_spotify_with_fallback(music_info, post)
                if track_id:
                    track_ids.append(track_id)
                
                # Rate limiting
                time.sleep(0.5)
            
            # Process comments from discussion threads
            logger.info("\n=== PROCESSING DISCUSSION THREAD COMMENTS ===")
            comments = self.get_comments_from_discussion_threads(posts)
            
            comment_track_count = 0
            for comment in comments:
                logger.info(f"Processing comment ({comment['score']} upvotes): {comment['body'][:50]}...")
                
                music_info = self.extract_music_info_from_comment(comment)
                if not music_info:
                    continue
                
                # Enhanced logging for comment-sourced tracks
                source_type = music_info.get('source', 'unknown')
                logger.info(f"  → Found track from {source_type} (comment: {comment['score']} upvotes)")
                
                # Log remix information if detected
                if music_info.get('is_remix'):
                    remix_info = f"Detected remix: {music_info.get('remixer', 'Unknown')} {music_info.get('remix_type', 'remix')}"
                    logger.info(f"  → {remix_info}")
                
                track_id = self.search_spotify_with_fallback(music_info, comment)
                if track_id:
                    track_ids.append(track_id)
                    comment_track_count += 1
                
                # Rate limiting
                time.sleep(0.5)
            
            logger.info(f"Found {comment_track_count} additional tracks from discussion thread comments")
            
            if not track_ids:
                logger.info("No tracks found on Spotify")
                return
            
            # Get/create playlist and add tracks
            playlist_id = self.get_or_create_playlist()
            self.add_tracks_to_playlist(playlist_id, track_ids)
            
            logger.info(f"Successfully processed {len(track_ids)} tracks")
            
        except Exception as e:
            logger.error(f"Error in main execution: {e}")
            raise

if __name__ == "__main__":
    sync = OverloadSpotifySync()
    sync.run()