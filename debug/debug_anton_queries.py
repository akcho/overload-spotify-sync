#!/usr/bin/env python3
"""
Debug the exact search queries generated for Anton Zap case
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def debug_anton_queries():
    """Debug the exact queries generated for AntonZap - Lovin U"""
    
    sync = OverloadSpotifySync(debug=True)
    
    print("=== DEBUGGING ANTON ZAP SEARCH QUERIES ===")
    
    # What the system extracted (from the logs)
    artist = "AntonZap"  # No space
    track = "Lovin U"
    
    print(f"Extracted: artist='{artist}', track='{track}'")
    
    # Generate the same queries the system would use
    queries = sync.build_search_queries(artist, track, False, "", "")
    
    print(f"\nGenerated queries:")
    for i, query in enumerate(queries, 1):
        print(f"{i}. '{query}'")
    
    print(f"\n=== TESTING EACH QUERY ===")
    
    for i, query in enumerate(queries[:5], 1):  # Test first 5
        print(f"\n--- Query {i}: '{query}' ---")
        try:
            results = sync.spotify.search(q=query, type='track', limit=5)
            tracks = results['tracks']['items']
            
            if tracks:
                print(f"Found {len(tracks)} results:")
                for j, track in enumerate(tracks, 1):
                    track_artist = track['artists'][0]['name']
                    track_name = track['name']
                    print(f"  {j}. {track_artist} - {track_name}")
                    
                # Test matching
                best_match = sync.find_best_track_match(tracks, artist, "Lovin U")
                if best_match:
                    found_artist = best_match['artists'][0]['name']
                    found_track = best_match['name']
                    print(f"  → Would match: {found_artist} - {found_track}")
                else:
                    print(f"  → No confident match")
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    debug_anton_queries()