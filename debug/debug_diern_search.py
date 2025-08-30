#!/usr/bin/env python3
"""
Search for where Diern - Paranoid Mixx is coming from
"""

from overload_spotify_sync import OverloadSpotifySync

def debug_diern_search():
    sync = OverloadSpotifySync(debug=True)
    
    # Test various search queries that might return Diern
    test_queries = [
        'paranoid',
        'paranoid sad',
        'paranoid prom', 
        'paranoid live',
        'paranoid rework',
        'sad prom',
        'live rework',
        'paranoid london sad prom',
        'eating glue sad prom',
    ]
    
    print("=== SEARCHING FOR DIERN - PARANOID MIXX ===")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = sync.spotify.search(q=query, type='track', limit=10)
            tracks = results['tracks']['items']
            
            # Look for Diern in the results
            diern_tracks = [t for t in tracks if 'diern' in t['artists'][0]['name'].lower()]
            
            if diern_tracks:
                print(f"  Found {len(diern_tracks)} Diern track(s):")
                for track in diern_tracks:
                    artist = track['artists'][0]['name']
                    name = track['name']
                    print(f"    - {artist} - {name}")
            else:
                print(f"  No Diern tracks found")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Also search specifically for the track
    print(f"\n=== DIRECT SEARCH FOR DIERN PARANOID MIXX ===")
    try:
        results = sync.spotify.search(q='Diern Paranoid Mixx', type='track', limit=5)
        tracks = results['tracks']['items']
        print(f"Found {len(tracks)} results:")
        for track in tracks:
            artist = track['artists'][0]['name']
            name = track['name']
            track_id = track['id']
            print(f"  - {artist} - {name} (ID: {track_id})")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_diern_search()