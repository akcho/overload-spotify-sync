#!/usr/bin/env python3
"""
Analyze URLs in recent overload posts to understand what sources are used
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync
from datetime import datetime, timedelta
from collections import defaultdict
import re

def analyze_post_urls():
    """Analyze URLs in recent posts"""
    sync = OverloadSpotifySync(debug=False)
    
    posts = []
    subreddit = sync.reddit.subreddit('theoverload')
    cutoff_date = datetime.now() - timedelta(days=7)
    
    url_patterns = defaultdict(int)
    sample_urls = []
    
    print("=== ANALYZING POST URLs ===")
    
    for submission in subreddit.new(limit=100):
        created_time = datetime.fromtimestamp(submission.created_utc)
        
        if created_time < cutoff_date:
            continue
            
        if submission.score >= sync.config.min_upvotes:
            url = submission.url
            title = submission.title
            
            # Categorize URLs
            if 'youtube.com' in url or 'youtu.be' in url:
                url_patterns['YouTube'] += 1
                if len(sample_urls) < 10:
                    sample_urls.append(('YouTube', url, title))
                    
            elif 'bandcamp.com' in url:
                url_patterns['Bandcamp'] += 1
                if len(sample_urls) < 10:
                    sample_urls.append(('Bandcamp', url, title))
                    
            elif 'soundcloud.com' in url:
                url_patterns['SoundCloud'] += 1
                if len(sample_urls) < 10:
                    sample_urls.append(('SoundCloud', url, title))
                    
            elif 'spotify.com' in url:
                url_patterns['Spotify'] += 1
                if len(sample_urls) < 10:
                    sample_urls.append(('Spotify', url, title))
                    
            else:
                url_patterns['Other'] += 1
                if len(sample_urls) < 10:
                    sample_urls.append(('Other', url, title))
    
    # Print statistics
    print(f"\nURL Source Statistics:")
    for source, count in sorted(url_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} posts")
    
    # Print sample URLs for testing
    print(f"\nSample URLs for testing:")
    for source, url, title in sample_urls:
        print(f"  {source}: {title}")
        print(f"    URL: {url}")
        print()

if __name__ == "__main__":
    analyze_post_urls()