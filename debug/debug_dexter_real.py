#!/usr/bin/env python3
"""
Debug the actual Dexter post from Reddit to see why it fails in real sync
"""

from overload_spotify_sync import OverloadSpotifySync
import os
from datetime import datetime, timedelta

def debug_dexter_real():
    sync = OverloadSpotifySync(debug=True)
    
    # Get posts from the last 7 days to find Dexter
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
                'created': post_date
            })
    
    print(f"Found {len(posts)} posts in last {time_window} days")
    
    # Find the Dexter post - let's be more flexible with matching
    dexter_post = None
    for post in posts:
        title_lower = post['title'].lower()
        if 'dexter' in title_lower and ('don\'t care' in title_lower or 'dont care' in title_lower):
            dexter_post = post
            break
    
    if not dexter_post:
        # Let's check all titles that contain dexter and just use the first one
        dexter_posts = [p for p in posts if 'dexter' in p['title'].lower()]
        if dexter_posts:
            dexter_post = dexter_posts[0]
            print(f"Found Dexter post with smart apostrophe: '{dexter_post['title']}'")
        else:
            print("❌ Could not find any Dexter posts")
            return
    
    print(f"✅ Found Dexter post: '{dexter_post['title']}'")
    print(f"   URL: {dexter_post['url']}")
    print(f"   Score: {dexter_post['score']}")
    
    # Test extraction with the real post data
    print(f"\n=== TESTING WITH REAL POST DATA ===")
    music_info = sync.extract_music_info(dexter_post)
    if not music_info:
        print("❌ extract_music_info rejected the post")
        return
        
    print(f"Extracted: '{music_info['artist']}' - '{music_info['track']}'")
    
    # Compare with our test case
    print(f"\n=== COMPARING WITH TEST CASE ===")
    test_post = {'title': "Dexter - I Don't Care [Klakson, 2000]", 'url': 'https://example.com'}
    test_info = sync.extract_music_info(test_post)
    print(f"Test case: '{test_info['artist']}' - '{test_info['track']}'")
    
    # Test if they're identical
    if music_info['artist'] == test_info['artist'] and music_info['track'] == test_info['track']:
        print("✅ Extraction results are identical")
    else:
        print("❌ Extraction results differ!")
        print(f"  Real: '{music_info['artist']}' - '{music_info['track']}'")
        print(f"  Test: '{test_info['artist']}' - '{test_info['track']}'")
        # Show character codes for the track names
        print(f"  Real track bytes: {music_info['track'].encode('utf-8')}")
        print(f"  Test track bytes: {test_info['track'].encode('utf-8')}")
        print("Continuing anyway to test search...")
    
    # Test actual Spotify search with real post data
    print(f"\n=== REAL SPOTIFY SEARCH WITH ACTUAL POST ===")
    track_id = sync.search_spotify(music_info)
    
    if track_id:
        print(f"✅ Found track ID: {track_id}")
        try:
            track_details = sync.spotify.track(track_id)
            print(f"Track: {track_details['artists'][0]['name']} - {track_details['name']}")
        except Exception as e:
            print(f"Error getting track details: {e}")
    else:
        print(f"❌ No track found with real post data")

if __name__ == "__main__":
    debug_dexter_real()