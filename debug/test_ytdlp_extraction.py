#!/usr/bin/env python3
"""
Test metadata extraction using yt-dlp for reliable results
"""

import yt_dlp
import re

def extract_metadata_with_ytdlp(url):
    """Extract metadata using yt-dlp"""
    try:
        # Configure yt-dlp to extract info only (no download)
        ydl_opts = {
            'quiet': True,  # Suppress output
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', '').strip()
            uploader = info.get('uploader', '').strip()
            description = info.get('description', '').strip()
            
            print(f"  Raw title: {title}")
            print(f"  Uploader: {uploader}")
            print(f"  Description snippet: {description[:200]}...")
            
            # Try to parse artist - track format from title
            if ' - ' in title:
                parts = title.split(' - ', 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    track = parts[1].strip()
                    
                    # Clean up common YouTube title patterns
                    track = re.sub(r'\s*\[.*?\]$', '', track)  # Remove [label] at end
                    track = re.sub(r'\s*\(.*?\)$', '', track)  # Remove (year) at end
                    
                    return artist, track
            
            # If no clear separation, try to extract from description or use title
            return None, title
            
    except Exception as e:
        print(f"  Error with yt-dlp: {e}")
        return None, None

def test_ytdlp_extraction():
    """Test yt-dlp metadata extraction"""
    
    test_urls = [
        "https://www.youtube.com/watch?v=vVz8vkJopI4",  # Paranoid London - Eating Glue (SAD PROM Live Rework)
        "https://www.youtube.com/watch?v=3zA7QK9QCa4",  # Let's try another one
    ]
    
    for url in test_urls:
        print(f"\n=== Testing URL: {url} ===")
        
        artist, track = extract_metadata_with_ytdlp(url)
        print(f"Extracted: {artist} - {track}")

if __name__ == "__main__":
    test_ytdlp_extraction()