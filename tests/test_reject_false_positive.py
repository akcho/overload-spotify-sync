#!/usr/bin/env python3
"""
Test that false positives get rejected
"""

from overload_spotify_sync import OverloadSpotifySync

def test_reject_false_positive():
    sync = OverloadSpotifySync()
    
    # The original case that should be rejected
    title = "Prime Minister of Doom - Deep In Your Heart"
    print(f"Testing: {title}")
    
    music_info = sync.extract_music_info({'title': title, 'url': 'https://example.com'})
    print(f"Extracted: {music_info['artist']} - {music_info['track']}")
    
    # Mock only bad matches (what we actually get from Spotify)
    bad_matches = [
        {
            'name': 'Deep In Your Mind',  # Wrong track
            'artists': [{'name': 'Casa del Mirto'}],  # Wrong artist
            'id': 'test123'
        },
        {
            'name': 'Deep In Your Heart',  # Right track 
            'artists': [{'name': 'CID'}],  # Wrong artist
            'id': 'test456'
        }
    ]
    
    best_match = sync.find_best_track_match(bad_matches, music_info['artist'], music_info['track'])
    
    if best_match:
        print(f"Would incorrectly match: {best_match['artists'][0]['name']} - {best_match['name']}")
        print("❌ Still has false positive problem")
    else:
        print("✅ Correctly rejected all poor matches")

if __name__ == "__main__":
    test_reject_false_positive()