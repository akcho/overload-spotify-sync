#!/usr/bin/env python3
"""
Debug why Paranoid London search is matching Diern - Paranoid Mixx
"""

from overload_spotify_sync import OverloadSpotifySync

def debug_paranoid_search():
    sync = OverloadSpotifySync(debug=True)
    
    # The extracted info from the Reddit post
    music_info = {
        'artist': 'Paranoid London',
        'track': 'Eating Glue', 
        'is_remix': True,
        'remixer': 'SAD PROM',
        'remix_type': 'Live rework'
    }
    
    print(f"Searching for: {music_info['artist']} - {music_info['track']}")
    print(f"Remix by: {music_info['remixer']} ({music_info['remix_type']})")
    
    # Test each search query to see what's being found
    search_queries = sync.build_search_queries(
        music_info['artist'], 
        music_info['track'], 
        music_info['is_remix'],
        music_info['remixer'], 
        music_info['remix_type']
    )
    
    print(f"\n=== SEARCH QUERIES ===")
    for i, query in enumerate(search_queries, 1):
        print(f"{i}. '{query}'")
        
        try:
            results = sync.spotify.search(q=query, type='track', limit=5)
            tracks = results['tracks']['items']
            
            print(f"   Found {len(tracks)} results:")
            for j, track in enumerate(tracks, 1):
                artist = track['artists'][0]['name']
                name = track['name'] 
                track_id = track['id']
                print(f"     {j}. {artist} - {name} (ID: {track_id})")
            
            # Test remix matching
            if tracks and music_info['is_remix']:
                print(f"   → Testing remix matching:")
                best_match = sync.find_best_remix_match(
                    tracks, 
                    music_info['artist'],
                    music_info['track'], 
                    music_info['remixer'],
                    music_info['remix_type']
                )
                if best_match:
                    match_artist = best_match['artists'][0]['name']
                    match_name = best_match['name']
                    print(f"   → REMIX MATCH: {match_artist} - {match_name}")
                    # Don't return, continue to see all queries
                else:
                    print(f"   → No remix match found")
            print()
        except Exception as e:
            print(f"   ERROR: {e}")
            print()

if __name__ == "__main__":
    debug_paranoid_search()