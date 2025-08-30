#!/usr/bin/env python3
"""
Debug playlist search
"""

from overload_spotify_sync import OverloadSpotifySync

def debug_playlists():
    sync = OverloadSpotifySync()
    user_id = sync.spotify.current_user()['id']
    
    print(f"Looking for playlist named: '{sync.config.playlist_name}'")
    print(f"User ID: {user_id}")
    
    # Get all playlists
    playlists = sync.spotify.user_playlists(user_id, limit=50)
    
    print("\nAll playlists:")
    found_target = False
    while playlists:
        for playlist in playlists['items']:
            is_target = playlist['name'] == sync.config.playlist_name
            if is_target:
                found_target = True
                print(f"  ✅ {playlist['name']} (ID: {playlist['id']}) - TARGET MATCH!")
            else:
                print(f"  - {playlist['name']} (ID: {playlist['id']})")
        
        if playlists['next']:
            playlists = sync.spotify.next(playlists)
        else:
            break
    
    if not found_target:
        print(f"\n❌ No playlist found with exact name: '{sync.config.playlist_name}'")
    
    # Test the actual function
    print(f"\nTesting get_or_create_playlist():")
    playlist_id = sync.get_or_create_playlist()
    print(f"Result: {playlist_id}")

if __name__ == "__main__":
    debug_playlists()