#!/usr/bin/env python3
"""
Debug playlist search with more thorough checking
"""

import time
from overload_spotify_sync import OverloadSpotifySync

def debug_playlists_thorough():
    sync = OverloadSpotifySync()
    user_id = sync.spotify.current_user()['id']
    
    print(f"Looking for playlist named: '{sync.config.playlist_name}'")
    
    # Check recently created playlists first
    playlists = sync.spotify.current_user_playlists(limit=50)
    
    print("\nChecking current user playlists (most recent first):")
    found_target = False
    page = 1
    
    while playlists and page <= 3:  # Check first 3 pages
        print(f"\nPage {page}:")
        for i, playlist in enumerate(playlists['items']):
            is_target = playlist['name'] == sync.config.playlist_name
            if is_target:
                found_target = True
                print(f"  ✅ {playlist['name']} (ID: {playlist['id']}) - TARGET MATCH!")
            else:
                print(f"  {i+1:2d}. {playlist['name']}")
                
            # Show first few for debugging
            if i < 3:
                print(f"      ID: {playlist['id']}, Owner: {playlist['owner']['id']}")
        
        if playlists['next'] and page < 3:
            playlists = sync.spotify.next(playlists) 
            page += 1
        else:
            break
    
    return found_target

if __name__ == "__main__":
    found = debug_playlists_thorough()
    print(f"\nResult: {'Found' if found else 'Not found'} target playlist")