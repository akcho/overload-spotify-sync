#!/usr/bin/env python3
"""
Check what Gamma Player versions exist on Spotify
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def debug_gamma_alternatives():
    """Check all Gamma Player versions on Spotify"""
    
    sync = OverloadSpotifySync(debug=True)
    
    print("=== SEARCHING ALL GAMMA PLAYER VERSIONS ===")
    
    search_terms = [
        "Jeff Mills Gamma Player",
        "Jeff Mills Gamma Player original",
        '"Jeff Mills" "Gamma Player" -Blue',
        "Gamma Player Jeff Mills",
    ]
    
    all_tracks = set()
    
    for search_term in search_terms:
        print(f"\n--- Search: '{search_term}' ---")
        try:
            results = sync.spotify.search(q=search_term, type='track', limit=50)
            tracks = results['tracks']['items']
            
            gamma_tracks = [t for t in tracks if 'gamma player' in t['name'].lower() 
                           and any('jeff mills' in a['name'].lower() for a in t['artists'])]
            
            if gamma_tracks:
                print(f"Found {len(gamma_tracks)} Gamma Player tracks:")
                for track in gamma_tracks:
                    artist = track['artists'][0]['name']
                    track_name = track['name']
                    track_id = track['id']
                    track_key = f"{artist} - {track_name}"
                    
                    if track_key not in all_tracks:
                        all_tracks.add(track_key)
                        print(f"  • {artist} - {track_name} (ID: {track_id})")
            else:
                print("  No Gamma Player tracks found")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total unique Gamma Player versions found: {len(all_tracks)}")
    for track in sorted(all_tracks):
        print(f"  • {track}")
        
    if len(all_tracks) == 1:
        print(f"\nConclusion: Only one version exists on Spotify")
        print(f"The 'Blue Potential Version' appears to be the only available version.")

if __name__ == "__main__":
    debug_gamma_alternatives()