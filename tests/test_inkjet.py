#!/usr/bin/env python3
"""
Test specifically with Beatrice Dillon and Call Super - Inkjet
"""

from overload_spotify_sync import OverloadSpotifySync

def test_inkjet():
    sync = OverloadSpotifySync(debug=True)  # Enable debug logging
    
    # Test the specific case
    title = "Beatrice Dillon and Call Super - Inkjet"
    print(f"Testing: {title}")
    
    music_info = sync.extract_music_info({'title': title, 'url': 'https://example.com'})
    if not music_info:
        print("❌ Rejected by extract_music_info (non-music post filter?)")
        return
        
    print(f"Extracted: {music_info['artist']} - {music_info['track']}")
    
    # Test actual Spotify search
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

if __name__ == "__main__":
    test_inkjet()