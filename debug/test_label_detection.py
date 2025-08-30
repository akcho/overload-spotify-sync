#!/usr/bin/env python3
"""
Test label detection and cleaning logic
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def test_label_detection():
    """Test label detection with simulated extracted metadata"""
    
    sync = OverloadSpotifySync(debug=True)
    
    # Simulate cases where YouTube/Bandcamp extraction gets confused by labels
    test_cases = [
        {
            'post_title': 'DJ Qu - Prayer [Strength Music, 2011]',
            'extracted_artist': 'Strength Music Recordings',  # What YouTube might extract
            'extracted_track': 'Prayer',
            'expected': 'Should clean to "DJ Qu - Prayer"'
        },
        {
            'post_title': 'Surgeon - Badger Bite [Dynamic Tension Records]',
            'extracted_artist': 'Dynamic Tension Records',
            'extracted_track': 'Badger Bite', 
            'expected': 'Should clean to "Surgeon - Badger Bite"'
        },
        {
            'post_title': 'Kerrier District - Fever [Kompakt]',
            'extracted_artist': 'Kompakt',
            'extracted_track': 'Fever',
            'expected': 'Should clean to "Kerrier District - Fever"'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== TEST CASE {i} ===")
        print(f"Post Title: '{test_case['post_title']}'")
        print(f"Extracted: '{test_case['extracted_artist']}' - '{test_case['extracted_track']}'")
        print(f"Expected: {test_case['expected']}")
        
        # Create simulated extracted metadata
        music_info = {
            'artist': test_case['extracted_artist'],
            'track': test_case['extracted_track'],
            'source': 'youtube',
            'is_remix': False
        }
        
        # Create mock post
        post = {
            'title': test_case['post_title'],
            'url': 'https://www.youtube.com/watch?v=example'
        }
        
        print(f"\nOriginal extracted metadata:")
        print(f"  Artist: '{music_info.get('artist', '')}'")
        print(f"  Track: '{music_info.get('track', '')}'")
        
        # Test label detection and cleaning
        cleaned_info = sync.clean_metadata_for_search(music_info, post)
        
        if cleaned_info:
            print(f"\nCleaned metadata:")
            print(f"  Artist: '{cleaned_info.get('artist', '')}'")
            print(f"  Track: '{cleaned_info.get('track', '')}'")
            
            # Show search queries
            queries = sync.build_search_queries(
                cleaned_info.get('artist', ''),
                cleaned_info.get('track', ''),
                cleaned_info.get('is_remix', False),
                cleaned_info.get('remixer', ''),
                cleaned_info.get('remix_type', '')
            )
            print(f"  Search queries: {queries[:2]}")
        else:
            print(f"\nNo cleaning applied (no label pattern detected)")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_label_detection()