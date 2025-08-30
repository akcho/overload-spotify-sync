#!/usr/bin/env python3
"""
Test if there's a delay in playlist appearing in search results
"""

import time
from overload_spotify_sync import OverloadSpotifySync

def test_playlist_delay():
    sync = OverloadSpotifySync()
    target_name = sync.config.playlist_name
    
    print(f"Testing playlist creation and immediate search...")
    print(f"Looking for: '{target_name}'")
    
    # Create a playlist
    print(f"\n1. Creating playlist...")
    playlist_id = sync.get_or_create_playlist()
    print(f"Created/found: {playlist_id}")
    
    # Test searches at different intervals
    intervals = [0, 1, 3, 5, 10]
    
    for delay in intervals:
        print(f"\n2. Waiting {delay} seconds, then searching...")
        time.sleep(delay)
        
        playlists = sync.spotify.current_user_playlists(limit=20)
        found = False
        
        for playlist in playlists['items']:
            if playlist['name'] == target_name:
                print(f"   ✅ FOUND: {playlist['name']} (ID: {playlist['id']})")
                found = True
                break
                
        if not found:
            print(f"   ❌ Not found in first 20 playlists")
            
        # Try a direct lookup by ID
        try:
            direct_playlist = sync.spotify.playlist(playlist_id)
            print(f"   Direct lookup: {direct_playlist['name']} - exists!")
        except Exception as e:
            print(f"   Direct lookup failed: {e}")
            
        if delay >= 5:  # Stop after 5 seconds if we found it
            break

if __name__ == "__main__":
    test_playlist_delay()