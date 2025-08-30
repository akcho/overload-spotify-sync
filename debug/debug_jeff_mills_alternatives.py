#!/usr/bin/env python3
"""
See what other Jeff Mills tracks might be better matches
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def debug_jeff_mills_alternatives():
    """Check what other Jeff Mills tracks might work"""
    
    sync = OverloadSpotifySync(debug=True)
    
    print("=== JEFF MILLS TRACK SEARCH ===")
    
    # Broader search for Jeff Mills tracks
    try:
        results = sync.spotify.search(q='Jeff Mills', type='track', limit=50)
        tracks = results['tracks']['items']
        
        jeff_tracks = [t for t in tracks if any('jeff mills' in a['name'].lower() for a in t['artists'])]
        
        print(f"Found {len(jeff_tracks)} Jeff Mills tracks:")
        
        # Show tracks with their versions/titles
        for i, track in enumerate(jeff_tracks[:20], 1):  # Top 20
            artist = track['artists'][0]['name']
            track_name = track['name']
            print(f"{i:2d}. {artist} - {track_name}")
            
        print(f"\n=== LOOKING FOR GAMMA-RELATED TRACKS ===")
        gamma_related = [t for t in jeff_tracks if 'gamma' in t['name'].lower()]
        
        if gamma_related:
            print(f"Found {len(gamma_related)} gamma-related tracks:")
            for track in gamma_related:
                artist = track['artists'][0]['name']
                track_name = track['name']
                print(f"  • {artist} - {track_name}")
        else:
            print("No other gamma-related tracks found")
            
        print(f"\n=== PROBLEM ANALYSIS ===")
        print(f"If someone posts 'Jeff Mills - Gamma Player', they probably want:")
        print(f"  1. The original 'Gamma Player' (if it exists)")
        print(f"  2. NOT the 'Blue Potential Version'")
        print(f"")
        print(f"Current situation:")
        print(f"  • Only 'Gamma Player - Blue Potential Version' exists on Spotify")
        print(f"  • Our system correctly finds it")
        print(f"  • But it's not the version you want")
        print(f"")
        print(f"Solutions:")
        print(f"  1. Skip tracks with unwanted version suffixes")
        print(f"  2. Prefer 'cleaner' track names over versions")
        print(f"  3. Add a 'bad version' penalty to scoring")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_jeff_mills_alternatives()