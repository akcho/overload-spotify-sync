#!/usr/bin/env python3
"""
Test script to validate remix parsing functionality
"""

from overload_spotify_sync import OverloadSpotifySync

def test_remix_parsing():
    """Test remix parsing with various title formats"""
    
    test_titles = [
        # Basic remix patterns
        "Deadmau5 - Strobe (Eric Prydz Remix)",
        "Porter Robinson - Language [Mat Zo Remix]", 
        "Above & Beyond - Blue Sky Action (Spencer Brown Remix)",
        "Disclosure - Latch (Sam Smith VIP Mix)",
        "Flume - Never Be Like You (What So Not Remix)",
        
        # Featured artist + remix
        "Deadmau5 feat. Kaskade - I Remember (Caspa Remix)",
        "Above & Beyond ft. Zoë Johnston - Blue Sky Action (Grum Edit)",
        
        # Different remix types
        "Moderat - A New Error (Thom Yorke Rework)",
        "Aphex Twin - Windowlicker [Boards of Canada Flip]",
        "Justice - Genesis (Boys Noize Bootleg)",
        
        # Non-remix tracks (should not detect remixes)
        "Deadmau5 - Strobe",
        "Porter Robinson - Language",
        "Disclosure - Latch",
        
        # Edge cases
        "Artist - Track (Something Not A Remix)",
        "Artist - Track (Original Mix)",  # This might be tricky
    ]
    
    sync = OverloadSpotifySync()
    
    print("Testing remix parsing:\n")
    print("=" * 80)
    
    for title in test_titles:
        print(f"\nTitle: {title}")
        print("-" * len(title))
        
        # Test remix extraction
        remix_info = sync.extract_remix_info(title)
        clean_title = sync.clean_title_for_parsing(title)
        
        print(f"Clean title: {clean_title}")
        print(f"Is remix: {remix_info['is_remix']}")
        if remix_info['is_remix']:
            print(f"Remixer: {remix_info['remixer']}")
            print(f"Remix type: {remix_info['remix_type']}")
            if remix_info.get('featured_artist'):
                print(f"Featured: {remix_info['featured_artist']}")
        
        # Test full extraction
        music_info = sync.extract_youtube_info('', title)
        if music_info:
            print(f"Artist: '{music_info['artist']}'")
            print(f"Track: '{music_info['track']}'")
            
            # Test search query building
            queries = sync.build_search_queries(
                music_info['artist'], 
                music_info['track'],
                music_info['is_remix'],
                music_info.get('remixer', ''),
                music_info.get('remix_type', '')
            )
            print(f"Search queries: {queries[:3]}...")  # Show first 3
        
        print("=" * 80)

if __name__ == "__main__":
    test_remix_parsing()