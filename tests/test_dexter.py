#!/usr/bin/env python3
"""
Test why Dexter - I Don't Care was rejected
"""

from overload_spotify_sync import OverloadSpotifySync

def test_dexter():
    sync = OverloadSpotifySync(debug=True)  # Enable debug logging
    
    # Test the specific case
    title = "Dexter - I Don't Care [Klakson, 2000]"
    print(f"Testing: {title}")
    
    music_info = sync.extract_music_info({'title': title, 'url': 'https://example.com'})
    if not music_info:
        print("❌ Rejected by extract_music_info")
        return
        
    print(f"Extracted: '{music_info['artist']}' - '{music_info['track']}'")
    
    # Test actual Spotify search with debug
    print(f"\n=== REAL SPOTIFY SEARCH ===")
    track_id = sync.search_spotify(music_info)
    
    if track_id:
        print(f"✅ Found track ID: {track_id}")
        # Get track details
        try:
            track_details = sync.spotify.track(track_id)
            print(f"Track: {track_details['artists'][0]['name']} - {track_details['name']}")
        except Exception as e:
            print(f"Error getting track details: {e}")
    else:
        print(f"❌ No track found")
        
    # Test with simpler title
    print(f"\n=== TESTING SIMPLIFIED VERSION ===")
    simple_title = "Dexter - I Don't Care"
    simple_info = sync.extract_music_info({'title': simple_title, 'url': 'https://example.com'})
    print(f"Simple version: '{simple_info['artist']}' - '{simple_info['track']}'")
    
    simple_track_id = sync.search_spotify(simple_info)
    if simple_track_id:
        print(f"✅ Simple version found: {simple_track_id}")
    else:
        print(f"❌ Simple version also not found")

if __name__ == "__main__":
    test_dexter()