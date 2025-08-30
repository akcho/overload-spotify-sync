#!/usr/bin/env python3
"""
Test specific title parsing
"""

from overload_spotify_sync import OverloadSpotifySync

def test_specific_title():
    sync = OverloadSpotifySync()
    
    title = "Beatrice Dillon and Call Super - Inkjet"
    print(f"Testing: {title}")
    
    music_info = sync.extract_music_info({'title': title, 'url': 'https://example.com'})
    print(f"Extracted info: {music_info}")
    
    if music_info:
        # Test search
        print(f"Artist: '{music_info['artist']}'")
        print(f"Track: '{music_info['track']}'")
        
        # Test the validation logic
        tracks_mock = [{'name': 'Inkjet', 'artists': [{'name': 'Beatrice Dillon'}, {'name': 'Call Super'}], 'id': 'test123'}]
        best_match = sync.find_best_track_match(tracks_mock, music_info['artist'], music_info['track'])
        print(f"Would match: {best_match is not None}")
        if best_match:
            print(f"Match: {best_match['artists'][0]['name']} - {best_match['name']}")

if __name__ == "__main__":
    test_specific_title()