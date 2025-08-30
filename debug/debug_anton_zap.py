#!/usr/bin/env python3
"""
Debug why Anton Zap - Lovin U was missed
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def debug_anton_zap():
    """Debug Anton Zap - Lovin U extraction and search"""
    
    sync = OverloadSpotifySync(debug=True)
    
    print("=== DEBUGGING ANTON ZAP - LOVIN U ===")
    
    # The post that was processed
    post_title = "You wont believe this. Just insane. Heavy dubby moving groove, hats that slice through the room and a clap that feels just so right. Anton Zap, one of the best to do it. Enjoy."
    
    print(f"Post title: '{post_title}'")
    
    # Test what was extracted
    print(f"\n1. What got extracted from YouTube:")
    # We saw it extracted "AntonZap - Lovin U" from the logs
    
    # Test direct search for different variations
    search_variations = [
        "AntonZap Lovin U",
        "Anton Zap Lovin U", 
        "AntonZap Loving U",
        "Anton Zap Loving U",
        "Anton Zap Lovin' U",
        "Anton Zap Love U"
    ]
    
    for query in search_variations:
        print(f"\n--- Testing query: '{query}' ---")
        try:
            results = sync.spotify.search(q=query, type='track', limit=5)
            tracks = results['tracks']['items']
            
            if tracks:
                print(f"Found {len(tracks)} results:")
                for i, track in enumerate(tracks, 1):
                    artist = track['artists'][0]['name']
                    track_name = track['name']
                    print(f"  {i}. {artist} - {track_name}")
                    
                # Test our matching
                best_match = sync.find_best_track_match(tracks, "Anton Zap", "Lovin U")
                if best_match:
                    found_artist = best_match['artists'][0]['name']
                    found_track = best_match['name']
                    print(f"  → Our algorithm would select: {found_artist} - {found_track}")
                else:
                    print(f"  → Our algorithm found no confident match")
                    
            else:
                print(f"  No results found")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    debug_anton_zap()