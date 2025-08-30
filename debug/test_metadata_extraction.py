#!/usr/bin/env python3
"""
Test metadata extraction from YouTube and Bandcamp URLs
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync
import requests
from bs4 import BeautifulSoup
import json
import re

def extract_youtube_metadata(url):
    """Extract title and artist from YouTube URL"""
    try:
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"  Failed to fetch YouTube page: {response.status_code}")
            return None, None
            
        # Look for JSON-LD structured data
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find the video title in meta tags
        title_tag = soup.find('meta', property='og:title')
        if title_tag:
            title = title_tag.get('content', '').strip()
            print(f"  Found title: {title}")
            
            # Try to parse artist - track format
            if ' - ' in title:
                parts = title.split(' - ', 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    track = parts[1].strip()
                    return artist, track
            
            # If no clear separation, return title as track with unknown artist
            return None, title
            
        print("  No title found in meta tags")
        return None, None
        
    except Exception as e:
        print(f"  Error extracting YouTube metadata: {e}")
        return None, None

def extract_bandcamp_metadata(url):
    """Extract title and artist from Bandcamp URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"  Failed to fetch Bandcamp page: {response.status_code}")
            return None, None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Bandcamp has structured data in script tags
        script_tags = soup.find_all('script', type='application/ld+json')
        
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if '@type' in data and data['@type'] == 'MusicRecording':
                    track = data.get('name', '').strip()
                    artist = None
                    
                    # Look for artist in byArtist
                    if 'byArtist' in data:
                        if isinstance(data['byArtist'], dict):
                            artist = data['byArtist'].get('name', '').strip()
                        elif isinstance(data['byArtist'], list) and len(data['byArtist']) > 0:
                            artist = data['byArtist'][0].get('name', '').strip()
                    
                    if track:
                        print(f"  Found track: {track}")
                        print(f"  Found artist: {artist}")
                        return artist, track
                        
            except json.JSONDecodeError:
                continue
        
        # Fallback: try to extract from page title and meta tags
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            print(f"  Fallback title: {title}")
            
            # Bandcamp titles are often "Track | Artist"
            if ' | ' in title:
                parts = title.split(' | ')
                if len(parts) >= 2:
                    track = parts[0].strip()
                    artist = parts[1].strip()
                    return artist, track
        
        print("  No structured data found")
        return None, None
        
    except Exception as e:
        print(f"  Error extracting Bandcamp metadata: {e}")
        return None, None

def test_metadata_extraction():
    """Test metadata extraction with sample URLs"""
    
    # Sample URLs from recent posts (based on what we've seen)
    test_urls = [
        "https://www.youtube.com/watch?v=vVz8vkJopI4",  # Paranoid London - Eating Glue (SAD PROM Live Rework)
        "https://www.youtube.com/watch?v=oQz6Z8p4Ihs",  # Jeff Mills - Gamma Player
        "https://www.youtube.com/watch?v=YhLkQbFYe6s",  # Underworld - Oich Oich
        # Add some Bandcamp URLs to test (hypothetical but realistic format)
        "https://artist.bandcamp.com/track/track-name",  # Test invalid URL for format
    ]
    
    for url in test_urls:
        print(f"\n=== Testing URL: {url} ===")
        
        if 'youtube.com' in url or 'youtu.be' in url:
            artist, track = extract_youtube_metadata(url)
            print(f"Result: {artist} - {track}")
            
        elif 'bandcamp.com' in url:
            artist, track = extract_bandcamp_metadata(url)
            print(f"Result: {artist} - {track}")
            
        else:
            print("  Unsupported URL format")

if __name__ == "__main__":
    test_metadata_extraction()