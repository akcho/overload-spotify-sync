#!/usr/bin/env python3
"""
Comprehensive playlist debugging to understand duplicate issue
"""

import time
from overload_spotify_sync import OverloadSpotifySync

def comprehensive_playlist_debug():
    sync = OverloadSpotifySync()
    user_id = sync.spotify.current_user()['id']
    target_name = sync.config.playlist_name
    
    print(f"=== COMPREHENSIVE PLAYLIST DEBUG ===")
    print(f"User ID: {user_id}")
    print(f"Target playlist name: '{target_name}'")
    print(f"Target name length: {len(target_name)} chars")
    
    # Method 1: current_user_playlists
    print(f"\n=== METHOD 1: current_user_playlists ===")
    playlists1 = sync.spotify.current_user_playlists(limit=50)
    found_matches1 = []
    
    page = 1
    while playlists1 and page <= 3:
        print(f"\nPage {page}: {len(playlists1['items'])} playlists")
        for i, playlist in enumerate(playlists1['items']):
            name = playlist['name']
            is_exact_match = name == target_name
            contains_target = target_name.lower() in name.lower()
            
            if is_exact_match or contains_target:
                found_matches1.append({
                    'name': name,
                    'id': playlist['id'],
                    'exact_match': is_exact_match,
                    'contains': contains_target,
                    'owner': playlist['owner']['id']
                })
                print(f"  MATCH: {name} (ID: {playlist['id'][:8]}...)")
            elif 'overload' in name.lower():
                print(f"  Similar: {name}")
                
        if playlists1['next'] and page < 3:
            playlists1 = sync.spotify.next(playlists1)
            page += 1
        else:
            break
    
    # Method 2: user_playlists
    print(f"\n=== METHOD 2: user_playlists ===")
    playlists2 = sync.spotify.user_playlists(user_id, limit=50)
    found_matches2 = []
    
    page = 1
    while playlists2 and page <= 3:
        print(f"\nPage {page}: {len(playlists2['items'])} playlists")
        for playlist in playlists2['items']:
            name = playlist['name']
            if name == target_name or target_name.lower() in name.lower():
                found_matches2.append({
                    'name': name,
                    'id': playlist['id'],
                    'exact_match': name == target_name
                })
                print(f"  MATCH: {name} (ID: {playlist['id'][:8]}...)")
                
        if playlists2['next'] and page < 3:
            playlists2 = sync.spotify.next(playlists2)
            page += 1
        else:
            break
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Method 1 (current_user_playlists) found: {len(found_matches1)} matches")
    for match in found_matches1:
        print(f"  - '{match['name']}' (exact: {match['exact_match']})")
        
    print(f"Method 2 (user_playlists) found: {len(found_matches2)} matches")
    for match in found_matches2:
        print(f"  - '{match['name']}' (exact: {match['exact_match']})")
    
    # Test the actual function
    print(f"\n=== TESTING ACTUAL FUNCTION ===")
    result_id = sync.get_or_create_playlist()
    print(f"Function returned playlist ID: {result_id}")
    
    # Check if this new playlist appears immediately
    print(f"\n=== IMMEDIATE RE-CHECK ===")
    time.sleep(2)  # Wait 2 seconds
    playlists_check = sync.spotify.current_user_playlists(limit=10)
    for playlist in playlists_check['items']:
        if playlist['name'] == target_name:
            print(f"Found immediately: {playlist['name']} (ID: {playlist['id']})")

if __name__ == "__main__":
    comprehensive_playlist_debug()