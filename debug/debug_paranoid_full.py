#!/usr/bin/env python3
"""
Debug the full Paranoid search as it happens in the sync
"""

from overload_spotify_sync import OverloadSpotifySync

def debug_paranoid_full():
    sync = OverloadSpotifySync(debug=True)
    
    # Create the exact post that's being processed
    post = {
        'title': 'Paranoid London - Eating Glue (SAD PROM Live Rework)',
        'url': 'https://www.youtube.com/watch?v=vVz8vkJopI4'
    }
    
    print(f"Post title: '{post['title']}'")
    print(f"Post URL: {post['url']}")
    
    # Extract music info
    music_info = sync.extract_music_info(post)
    print(f"\nExtracted info:")
    print(f"  Artist: {music_info['artist']}")
    print(f"  Track: {music_info['track']}")
    print(f"  Is remix: {music_info['is_remix']}")
    if music_info['is_remix']:
        print(f"  Remixer: {music_info['remixer']}")
        print(f"  Remix type: {music_info['remix_type']}")
    
    # Run the actual search
    print(f"\n=== RUNNING ACTUAL SEARCH ===")
    track_id = sync.search_spotify(music_info)
    
    if track_id:
        # Get the track details
        track_details = sync.spotify.track(track_id)
        found_artist = track_details['artists'][0]['name']
        found_track = track_details['name']
        print(f"\n✅ FINAL RESULT: {found_artist} - {found_track}")
        print(f"   Track ID: {track_id}")
        print(f"   Full track name: {track_details['name']}")
        print(f"   All artists: {[a['name'] for a in track_details['artists']]}")
    else:
        print(f"\n❌ No track found")

if __name__ == "__main__":
    debug_paranoid_full()