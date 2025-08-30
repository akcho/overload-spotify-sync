#!/usr/bin/env python3
"""
Debug Caroline Polachek extraction in detail
"""

from overload_spotify_sync import OverloadSpotifySync

def debug_extraction():
    sync = OverloadSpotifySync(debug=True)
    
    # The actual post
    post = {
        'title': 'A trip-hop remix of Caroline Polachek "Pretty In Possible"',
        'url': 'https://ksianboktet.bandcamp.com/track/pretty-in-possible-ksian-boktet-remix'
    }
    
    print(f"Original title: '{post['title']}'")
    print(f"URL: {post['url']}")
    
    # Test each step of extraction
    print(f"\n=== STEP 1: Non-music filtering ===")
    result = sync.extract_music_info(post)
    if not result:
        print("❌ Filtered out as non-music")
        return
        
    print(f"✅ Passed non-music filter")
    
    print(f"\n=== STEP 2: Title cleaning ===")
    clean_title = sync.clean_title_for_parsing(post['title'])
    print(f"Clean title: '{clean_title}'")
    
    print(f"\n=== STEP 3: Remix detection ===")
    remix_info = sync.extract_remix_info(post['title'])
    print(f"Is remix: {remix_info['is_remix']}")
    if remix_info['is_remix']:
        print(f"Remixer: {remix_info['remixer']}")
        print(f"Remix type: {remix_info['remix_type']}")
    
    print(f"\n=== STEP 4: Artist/Track parsing ===")
    print(f"Final extraction result:")
    print(f"  Artist: '{result['artist']}'")  
    print(f"  Track: '{result['track']}'")
    print(f"  Is remix: {result['is_remix']}")
    if result['is_remix']:
        print(f"  Remixer: '{result['remixer']}'")
        print(f"  Remix type: '{result['remix_type']}'")

if __name__ == "__main__":
    debug_extraction()