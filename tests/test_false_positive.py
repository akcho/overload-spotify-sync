#!/usr/bin/env python3
"""
Test the false positive case
"""

from overload_spotify_sync import OverloadSpotifySync

def test_false_positive():
    sync = OverloadSpotifySync()
    
    # The original case that gave false positive
    title = "Prime Minister of Doom - Deep In Your Heart"
    print(f"Testing: {title}")
    
    music_info = sync.extract_music_info({'title': title, 'url': 'https://example.com'})
    print(f"Extracted: {music_info['artist']} - {music_info['track']}")
    
    # Mock the bad match that was returned
    bad_match = {
        'name': 'Deep In Your Mind', 
        'artists': [{'name': 'Casa del Mirto'}], 
        'id': 'test123'
    }
    
    good_match = {
        'name': 'Deep In Your Heart', 
        'artists': [{'name': 'Prime Minister of Doom'}], 
        'id': 'test456'
    }
    
    tracks_mock = [bad_match, good_match]
    best_match = sync.find_best_track_match(tracks_mock, music_info['artist'], music_info['track'])
    
    if best_match:
        print(f"Would match: {best_match['artists'][0]['name']} - {best_match['name']}")
        print(f"Correct match: {best_match['id'] == 'test456'}")
    else:
        print("No match found (better than false positive)")

if __name__ == "__main__":
    test_false_positive()