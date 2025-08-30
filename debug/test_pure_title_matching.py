#!/usr/bin/env python3
"""
Test the pure title matching logic
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def test_pure_title_matching():
    """Test pure title matching with Jeff Mills case"""
    
    sync = OverloadSpotifySync(debug=True)
    
    print("=== TESTING PURE TITLE MATCHING ===")
    
    # Test the detection logic
    test_cases = [
        {
            'query_title': 'Gamma Player',
            'spotify_title': 'Gamma Player - Blue Potential Version',
            'expected_clean': True,
            'expected_version': True
        },
        {
            'query_title': 'Gamma Player (Remix)',
            'spotify_title': 'Gamma Player - Blue Potential Version', 
            'expected_clean': False,  # Query already has version info
            'expected_version': True
        },
        {
            'query_title': 'The Bells',
            'spotify_title': 'The Bells',
            'expected_clean': True,
            'expected_version': False
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Query: '{case['query_title']}'")
        print(f"Spotify: '{case['spotify_title']}'")
        
        is_clean = sync.is_clean_title(case['query_title'])
        has_version = sync.has_version_suffix(case['spotify_title'])
        
        print(f"Is clean query: {is_clean} (expected: {case['expected_clean']})")
        print(f"Has version suffix: {has_version} (expected: {case['expected_version']})")
        
        if is_clean and has_version:
            print(f"→ Would apply PENALTY (clean query vs versioned result)")
        else:
            print(f"→ No penalty")
    
    print(f"\n=== TESTING WITH REAL SEARCH ===")
    
    # Test with actual Jeff Mills search
    try:
        results = sync.spotify.search(q='Jeff Mills Gamma Player', type='track', limit=5)
        tracks = results['tracks']['items']
        
        print(f"Found {len(tracks)} tracks:")
        for track in tracks:
            artist = track['artists'][0]['name'] 
            track_name = track['name']
            print(f"  • {artist} - {track_name}")
        
        if tracks:
            print(f"\nTesting matching with 'Gamma Player' query:")
            best_match = sync.find_best_track_match(tracks, "Jeff Mills", "Gamma Player")
            
            if best_match:
                found_artist = best_match['artists'][0]['name']
                found_track = best_match['name']
                print(f"Selected: {found_artist} - {found_track}")
            else:
                print(f"No confident match (penalty may have eliminated options)")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pure_title_matching()