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
    def __init__(self):
        self.config = Config()
        
        # Reddit API setup
        self.reddit = praw.Reddit(
            client_id=self.config.reddit_client_id,
            client_secret=self.config.reddit_client_secret,
            user_agent='overload-spotify-sync/1.0'
        )
        
        # Spotify API setup
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.config.spotify_client_id,
            client_secret=self.config.spotify_client_secret,
            redirect_uri=self.config.spotify_redirect_uri,
            scope='playlist-modify-public playlist-modify-private'
        ))
        
    def get_recent_posts(self) -> List[Dict]:
        """Fetch recent posts from r/theoverload with minimum upvotes"""
        posts = []
        subreddit = self.reddit.subreddit('theoverload')
        
        # Get posts from the last day
        yesterday = datetime.now() - timedelta(days=1)
        
        for submission in subreddit.new(limit=100):
            created_time = datetime.fromtimestamp(submission.created_utc)
            
            if created_time < yesterday:
                continue
                
            if submission.score >= self.config.min_upvotes:
                posts.append({
                    'title': submission.title,
                    'url': submission.url,
                    'score': submission.score,
                    'id': submission.id,
                    'created': created_time
                })
                
        logger.info(f"Found {len(posts)} posts with {self.config.min_upvotes}+ upvotes")
        return posts
    
    def extract_music_info(self, post: Dict) -> Optional[Dict]:
        """Extract artist and track info from various music platforms"""
        url = post['url']
        title = post['title']
        
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
    
    def extract_youtube_info(self, url: str, title: str) -> Optional[Dict]:
        """Extract info from YouTube URL and title"""
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
            match = re.match(pattern, title.strip(), re.IGNORECASE)
            if match:
                return {
                    'artist': match.group(1).strip(),
                    'track': match.group(2).strip(),
                    'source': 'youtube'
                }
        
        # Fallback: assume title is track name
        return {
            'artist': '',
            'track': title.strip(),
            'source': 'youtube'
        }
    
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
        """Extract info from Bandcamp (similar to YouTube)"""
        return self.extract_youtube_info(url, title)
    
    def extract_from_title(self, title: str) -> Optional[Dict]:
        """Try to extract artist/track from Reddit post title"""
        return self.extract_youtube_info('', title)
    
    def search_spotify(self, music_info: Dict) -> Optional[str]:
        """Search for track on Spotify and return track ID"""
        if music_info.get('spotify_id'):
            return music_info['spotify_id']
        
        artist = music_info.get('artist', '')
        track = music_info.get('track', '')
        
        if not track:
            return None
        
        # Try different search queries
        search_queries = []
        
        if artist:
            search_queries.extend([
                f"artist:{artist} track:{track}",
                f"{artist} {track}",
                f'"{artist}" "{track}"'
            ])
        
        search_queries.append(track)
        
        for query in search_queries:
            try:
                results = self.spotify.search(q=query, type='track', limit=10)
                
                if results['tracks']['items']:
                    # Return the first result
                    track_id = results['tracks']['items'][0]['id']
                    found_artist = results['tracks']['items'][0]['artists'][0]['name']
                    found_track = results['tracks']['items'][0]['name']
                    
                    logger.info(f"Found on Spotify: {found_artist} - {found_track}")
                    return track_id
                    
            except Exception as e:
                logger.warning(f"Spotify search failed for '{query}': {e}")
                continue
        
        logger.info(f"Could not find on Spotify: {artist} - {track}")
        return None
    
    def get_or_create_playlist(self) -> str:
        """Get existing playlist or create new one"""
        user_id = self.spotify.current_user()['id']
        
        # Search for existing playlist
        playlists = self.spotify.user_playlists(user_id)
        for playlist in playlists['items']:
            if playlist['name'] == self.config.playlist_name:
                logger.info(f"Found existing playlist: {playlist['id']}")
                return playlist['id']
        
        # Create new playlist
        playlist = self.spotify.user_playlist_create(
            user=user_id,
            name=self.config.playlist_name,
            public=False,
            description="Daily music discoveries from r/theoverload"
        )
        
        logger.info(f"Created new playlist: {playlist['id']}")
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
            logger.info("No new tracks to add")
            return
        
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
            
            for post in posts:
                logger.info(f"Processing: {post['title'][:50]}...")
                
                music_info = self.extract_music_info(post)
                if not music_info:
                    continue
                
                track_id = self.search_spotify(music_info)
                if track_id:
                    track_ids.append(track_id)
                
                # Rate limiting
                time.sleep(0.5)
            
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