#!/usr/bin/env python3
"""
Test specifically with Octex - Bubblin case to ensure it passes
"""

from overload_spotify_sync import OverloadSpotifySync

def test_octex_bubblin():
    sync = OverloadSpotifySync()
    
    # Test the specific case that was rejected
    title = "Octex - Bubblin (2022)"
    print(f"Testing: {title}")
    
    music_info = sync.extract_music_info({'title': title, 'url': 'https://example.com'})
    print(f"Extracted: {music_info['artist']} - {music_info['track']}")
    
    # Mock different variations we might get from Spotify
    test_cases = [
        {
            'name': 'Bubblin',  # Exact match
            'artists': [{'name': 'Octex'}],
            'id': 'exact_match'
        },
        {
            'name': 'Bubblin (2022)',  # With year
            'artists': [{'name': 'Octex'}], 
            'id': 'with_year'
        },
        {
            'name': 'Bubblin (Remastered)',  # Different suffix
            'artists': [{'name': 'Octex'}],
            'id': 'remastered'
        },
        {
            'name': 'Different Song',  # Should be rejected
            'artists': [{'name': 'Octex'}],
            'id': 'wrong_song'
        },
        {
            'name': 'Bubblin',  # Right song, wrong artist
            'artists': [{'name': 'Wrong Artist'}],
            'id': 'wrong_artist'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['artists'][0]['name']} - {test_case['name']}")
        
        best_match = sync.find_best_track_match([test_case], music_info['artist'], music_info['track'])
        
        if best_match:
            print(f"  ✅ Would match: {best_match['id']}")
        else:
            print(f"  ❌ Rejected")
    
    # Test with multiple candidates (realistic scenario)
    print(f"\n=== REALISTIC TEST WITH MULTIPLE CANDIDATES ===")
    all_candidates = test_cases
    best_match = sync.find_best_track_match(all_candidates, music_info['artist'], music_info['track'])
    
    if best_match:
        print(f"Best match: {best_match['artists'][0]['name']} - {best_match['name']} ({best_match['id']})")
    else:
        print("No matches found")

if __name__ == "__main__":
    test_octex_bubblin()