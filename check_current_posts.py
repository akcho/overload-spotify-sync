#!/usr/bin/env python3
"""
Check current posts to see what's available
"""

from overload_spotify_sync import OverloadSpotifySync

def check_current_posts():
    sync = OverloadSpotifySync()
    
    posts = sync.get_recent_posts()
    print(f"Found {len(posts)} posts:")
    print("="*60)
    
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title']}")
        print(f"   Score: {post['score']}, URL: {post['url'][:50]}...")
        
        # Test extraction
        music_info = sync.extract_music_info(post)
        if music_info:
            if music_info.get('is_remix'):
                print(f"   → REMIX: {music_info['artist']} - {music_info['track']} ({music_info['remixer']} {music_info['remix_type']})")
            else:
                print(f"   → MUSIC: {music_info['artist']} - {music_info['track']}")
        else:
            print(f"   → SKIP: Non-music post")
        print()

if __name__ == "__main__":
    check_current_posts()