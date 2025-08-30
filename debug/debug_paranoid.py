#!/usr/bin/env python3
"""
Debug the Paranoid track to see what's being processed
"""

from overload_spotify_sync import OverloadSpotifySync
from datetime import datetime, timedelta

def debug_paranoid():
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
    
    # Find posts mentioning Paranoid, Diern, or mixx
    paranoid_posts = []
    for post in posts:
        title_lower = post['title'].lower()
        if ('paranoid' in title_lower or 'diern' in title_lower or 
            'mixx' in title_lower or 'eating glue' in title_lower or
            'sad prom' in title_lower):
            paranoid_posts.append(post)
    
    print(f"\nFound {len(paranoid_posts)} posts mentioning Paranoid/Diern/Mixx/Eating Glue/SAD PROM:")
    
    for i, post in enumerate(paranoid_posts, 1):
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
            
            # Test Spotify search
            print(f"   → TESTING SPOTIFY SEARCH:")
            track_id = sync.search_spotify(music_info)
            if track_id:
                try:
                    track_details = sync.spotify.track(track_id)
                    found_artist = track_details['artists'][0]['name']
                    found_track = track_details['name']
                    print(f"   → SPOTIFY RESULT: {found_artist} - {found_track}")
                except Exception as e:
                    print(f"   → SPOTIFY ERROR: {e}")
            else:
                print(f"   → SPOTIFY: No match found")
        else:
            print(f"   → SKIPPED: Non-music post")

if __name__ == "__main__":
    debug_paranoid()