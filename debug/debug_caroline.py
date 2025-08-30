#!/usr/bin/env python3
"""
Debug the Caroline Polachek post to verify it's legitimate
"""

from overload_spotify_sync import OverloadSpotifySync
from datetime import datetime, timedelta

def debug_caroline():
    sync = OverloadSpotifySync(debug=True)
    
    # Get posts from the last 7 days
    time_window = 7
    cutoff_date = datetime.now() - timedelta(days=time_window)
    
    # Find all posts
    posts = []
    for submission in sync.reddit.subreddit('theoverload').new(limit=100):
        post_date = datetime.fromtimestamp(submission.created_utc)
        if post_date >= cutoff_date and submission.score >= 3:
            posts.append({
                'title': submission.title,
                'url': submission.url,
                'score': submission.score,
                'created': post_date,
                'id': submission.id
            })
    
    print(f"Found {len(posts)} posts in last {time_window} days")
    
    # Find posts mentioning Caroline Polachek or "Pretty in Possible"
    caroline_posts = []
    for post in posts:
        title_lower = post['title'].lower()
        if ('caroline' in title_lower or 'polachek' in title_lower or 
            'pretty' in title_lower or 'possible' in title_lower):
            caroline_posts.append(post)
    
    print(f"\nFound {len(caroline_posts)} posts mentioning Caroline/Polachek/Pretty/Possible:")
    
    for i, post in enumerate(caroline_posts, 1):
        print(f"\n{i}. TITLE: '{post['title']}'")
        print(f"   URL: {post['url']}")
        print(f"   Score: {post['score']}")
        print(f"   Reddit ID: {post['id']}")
        print(f"   Created: {post['created']}")
        
        # Test extraction
        music_info = sync.extract_music_info(post)
        if music_info:
            print(f"   → EXTRACTED: {music_info['artist']} - {music_info['track']}")
            if music_info.get('is_remix'):
                print(f"   → REMIX INFO: {music_info['remixer']} {music_info['remix_type']}")
        else:
            print(f"   → SKIPPED: Non-music post")
    
    # Also check if there are any posts with "trip" and "hop" that might be getting parsed strangely
    print(f"\n=== CHECKING FOR 'TRIP-HOP' POSTS ===")
    trip_posts = []
    for post in posts:
        title_lower = post['title'].lower()
        if 'trip' in title_lower and 'hop' in title_lower:
            trip_posts.append(post)
            
    for post in trip_posts:
        print(f"\nTRIP-HOP POST: '{post['title']}'")
        music_info = sync.extract_music_info(post)
        if music_info:
            print(f"   → EXTRACTED: {music_info['artist']} - {music_info['track']}")

if __name__ == "__main__":
    debug_caroline()