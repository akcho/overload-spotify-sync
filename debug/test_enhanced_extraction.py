#!/usr/bin/env python3
"""
Test the enhanced metadata extraction with real URLs from recent posts
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def test_enhanced_extraction():
    """Test enhanced metadata extraction"""
    
    sync = OverloadSpotifySync(debug=True)
    
    # Test cases with known problematic examples
    test_cases = [
        {
            'title': 'Paranoid London - Eating Glue (SAD PROM Live Rework)',
            'url': 'https://www.youtube.com/watch?v=vVz8vkJopI4',
            'expected_issue': 'Should correctly identify this as Paranoid London track with SAD PROM remix'
        },
        {
            'title': 'If We Ever — High Contrast (Overmono Remix)',
            'url': 'https://www.youtube.com/watch?v=example',  # hypothetical
            'expected_issue': 'Should identify as High Contrast track with Overmono remix'
        },
        {
            'title': 'Random misleading title that says nothing about music',
            'url': 'https://www.youtube.com/watch?v=vVz8vkJopI4',  # Same video, different title
            'expected_issue': 'Should extract true metadata from YouTube, ignoring misleading title'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== TEST CASE {i} ===")
        print(f"Post Title: '{test_case['title']}'")
        print(f"URL: {test_case['url']}")
        print(f"Expected: {test_case['expected_issue']}")
        
        # Create a mock post
        post = {
            'title': test_case['title'],
            'url': test_case['url']
        }
        
        # Extract metadata
        music_info = sync.extract_music_info(post)
        
        if music_info:
            print(f"Result:")
            print(f"  Artist: '{music_info.get('artist', 'N/A')}'")
            print(f"  Track: '{music_info.get('track', 'N/A')}'")
            print(f"  Source: {music_info.get('source', 'N/A')}")
            print(f"  Is remix: {music_info.get('is_remix', False)}")
            if music_info.get('is_remix'):
                print(f"  Remixer: '{music_info.get('remixer', 'N/A')}'")
                print(f"  Remix type: '{music_info.get('remix_type', 'N/A')}'")
        else:
            print("Result: No music info extracted")

if __name__ == "__main__":
    test_enhanced_extraction()