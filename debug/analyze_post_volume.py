#!/usr/bin/env python3
"""
Analyze post volume over different time periods to determine feasible sweep range
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync
from datetime import datetime, timedelta
import os

def analyze_post_volume():
    sync = OverloadSpotifySync(debug=True)
    
    # Test different time windows
    time_windows = [7, 14, 30, 60, 90]  # days
    
    for days in time_windows:
        print(f"\n=== ANALYZING {days} DAYS ===")
        
        posts = []
        subreddit = sync.reddit.subreddit('theoverload')
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Count posts in this time window
        total_checked = 0
        posts_in_window = 0
        music_posts = 0
        
        for submission in subreddit.new(limit=1000):  # Check more posts for longer windows
            total_checked += 1
            created_time = datetime.fromtimestamp(submission.created_utc)
            
            if created_time < cutoff_date:
                continue
                
            posts_in_window += 1
            
            if submission.score >= sync.config.min_upvotes:
                # Check if it's likely a music post
                music_info = sync.extract_music_info({
                    'title': submission.title,
                    'url': submission.url
                })
                
                if not sync.is_non_music_post(submission.title):
                    music_posts += 1
                    if music_posts <= 5:  # Show first few examples
                        print(f"  Example: {submission.title} ({submission.score} upvotes)")
        
        print(f"  Posts in {days}d window: {posts_in_window}")
        print(f"  Music posts with min upvotes: {music_posts}")
        print(f"  Total posts checked: {total_checked}")
        
        if posts_in_window == 0:
            print(f"  ⚠️  No posts found - may have hit Reddit API limit")
            break

if __name__ == "__main__":
    analyze_post_volume()