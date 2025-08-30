#!/usr/bin/env python3
"""
Debug why Diern - Paranoid Mixx is being accepted as a remix match
"""

from overload_spotify_sync import OverloadSpotifySync

def debug_remix_scoring():
    sync = OverloadSpotifySync(debug=True)
    
    # The search criteria
    original_artist = "Paranoid London"
    original_track = "Eating Glue" 
    remixer = "SAD PROM Live"
    remix_type = "rework"
    
    # The track that's being matched
    diern_track = {
        'name': 'Paranoid Mixx',
        'artists': [{'name': 'Diern'}],
        'id': '4qxB0G1bAbI8Fml7d2xqzp'
    }
    
    print(f"Testing match for:")
    print(f"  Original: {original_artist} - {original_track}")
    print(f"  Remixer: {remixer}")
    print(f"  Remix type: {remix_type}")
    print(f"")
    print(f"Against Spotify track:")
    print(f"  {diern_track['artists'][0]['name']} - {diern_track['name']}")
    print(f"")
    
    # Manually calculate the score
    score = 0
    track_name = diern_track['name'].lower()  # "paranoid mixx"
    artist_names = [a['name'].lower() for a in diern_track['artists']]  # ["diern"]
    
    print(f"Scoring breakdown:")
    
    # Check if remixer appears in track name or artists
    if remixer and remixer.lower() in track_name:
        score += 5
        print(f"  Remixer '{remixer}' in track name: +5")
    else:
        print(f"  Remixer '{remixer}' NOT in track name '{track_name}': +0")
        
    if remixer and any(remixer.lower() in artist_name for artist_name in artist_names):
        score += 5
        print(f"  Remixer '{remixer}' in artist names: +5")
    else:
        print(f"  Remixer '{remixer}' NOT in artist names {artist_names}: +0")
        
    # Check if remix type appears in track name
    if remix_type and remix_type.lower() in track_name:
        score += 3
        print(f"  Remix type '{remix_type}' in track name: +3")
    else:
        print(f"  Remix type '{remix_type}' NOT in track name '{track_name}': +0")
        
    # Check for general remix indicators
    if any(indicator in track_name for indicator in ['remix', 'mix', 'edit', 'rework', 'vip']):
        score += 2
        found_indicators = [ind for ind in ['remix', 'mix', 'edit', 'rework', 'vip'] if ind in track_name]
        print(f"  General remix indicators {found_indicators} found: +2")
    else:
        print(f"  No general remix indicators in '{track_name}': +0")
        
    # Check if original artist matches
    if original_artist and any(original_artist.lower() in artist_name for artist_name in artist_names):
        score += 2
        print(f"  Original artist '{original_artist}' in artist names: +2")
    else:
        # Check if any part of original artist is in artist names
        original_words = original_artist.lower().split()
        found_words = []
        for word in original_words:
            if any(word in artist_name for artist_name in artist_names):
                found_words.append(word)
        
        if found_words:
            score += 2  # This might be what's happening
            print(f"  Original artist words {found_words} found in artist names: +2")
        else:
            print(f"  Original artist '{original_artist}' NOT in artist names {artist_names}: +0")
        
    # Check if original track name is in the title
    if original_track and original_track.lower() in track_name:
        score += 1
        print(f"  Original track '{original_track}' in track name: +1")
    else:
        print(f"  Original track '{original_track}' NOT in track name '{track_name}': +0")
    
    print(f"")
    print(f"Total score: {score}")
    
    # Test the actual function
    print(f"")
    print(f"=== TESTING ACTUAL FUNCTION ===")
    result = sync.find_best_remix_match([diern_track], original_artist, original_track, remixer, remix_type)
    if result:
        print(f"✅ Function returned: {result['artists'][0]['name']} - {result['name']}")
    else:
        print(f"❌ Function returned: None")

if __name__ == "__main__":
    debug_remix_scoring()