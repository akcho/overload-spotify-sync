#!/usr/bin/env python3
"""
Test the fallback search logic with problematic cases
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def test_fallback_logic():
    """Test fallback search logic with known problematic cases"""
    
    sync = OverloadSpotifySync(debug=True)
    
    # Test cases where extracted metadata might be wrong but post title is correct
    test_cases = [
        {
            'title': 'DJ Qu - Prayer [Strength Music, 2011]',
            'url': 'https://www.youtube.com/watch?v=fake_id',  # This would extract "Strength Music Recordings - Prayer"
            'expected': 'Should fallback from "Strength Music" to "DJ Qu" when Strength Music search fails'
        },
        {
            'title': 'Surgeon - Badger Bite [Dynamic Tension, 2010]', 
            'url': 'https://www.youtube.com/watch?v=another_fake',
            'expected': 'Should fallback from label name to "Surgeon" if label search fails'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== TEST CASE {i} ===")
        print(f"Title: '{test_case['title']}'")
        print(f"URL: {test_case['url']}")
        print(f"Expected: {test_case['expected']}")
        
        # Create mock post
        post = {
            'title': test_case['title'],
            'url': test_case['url']
        }
        
        # Test the complete extraction and search process
        print(f"\n1. Primary extraction:")
        music_info = sync.extract_music_info(post)
        if music_info:
            print(f"   Artist: '{music_info.get('artist', '')}'")
            print(f"   Track: '{music_info.get('track', '')}'")
            print(f"   Source: {music_info.get('source', '')}")
        
        print(f"\n2. Fallback extraction from title:")
        fallback_info = sync.extract_from_title(test_case['title'])
        if fallback_info:
            print(f"   Artist: '{fallback_info.get('artist', '')}'")
            print(f"   Track: '{fallback_info.get('track', '')}'")
        
        print(f"\n3. Cleaned metadata:")
        if music_info:
            cleaned_info = sync.clean_metadata_for_search(music_info, post)
            if cleaned_info:
                print(f"   Artist: '{cleaned_info.get('artist', '')}'")
                print(f"   Track: '{cleaned_info.get('track', '')}'")
            else:
                print("   No cleaning applied")
        
        # Test full search with fallback (but don't actually search Spotify to avoid rate limits)
        print(f"\n4. Search queries that would be tried:")
        if music_info:
            # Show what the build_search_queries method would generate
            primary_queries = sync.build_search_queries(
                music_info.get('artist', ''),
                music_info.get('track', ''),
                music_info.get('is_remix', False),
                music_info.get('remixer', ''),
                music_info.get('remix_type', '')
            )
            print(f"   Primary: {primary_queries[:3]}...")  # Show first few
            
            if fallback_info:
                fallback_queries = sync.build_search_queries(
                    fallback_info.get('artist', ''),
                    fallback_info.get('track', ''),
                    fallback_info.get('is_remix', False),
                    fallback_info.get('remixer', ''),
                    fallback_info.get('remix_type', '')
                )
                print(f"   Fallback: {fallback_queries[:3]}...")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_fallback_logic()