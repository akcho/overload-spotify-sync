#!/usr/bin/env python3
"""
Test the skip patterns for various descriptive remix titles
"""

from overload_spotify_sync import OverloadSpotifySync

def test_skip_patterns():
    sync = OverloadSpotifySync()
    
    # Test cases that SHOULD be skipped
    should_skip = [
        'A trip-hop remix of Caroline Polachek "Pretty In Possible"',
        'A house remix of Disclosure - Latch',
        'An electronic remix of Jamie xx - Gosh',
        'A drum-and-bass remix of Aphex Twin - Windowlicker',
        'A ambient remix of Brian Eno - Music for Airports',
    ]
    
    # Test cases that should NOT be skipped (legitimate track titles)  
    should_not_skip = [
        'Artist - A Trip (House Remix)',  # This is a proper remix title format
        'DJ - Electronic Dreams',         # Artist name that sounds like genre
        'Ambient - Track Name',           # Artist named "Ambient"
        'The House Remix - Song Title',   # "The House Remix" as artist name
        'Aphex Twin - A Remix',           # "A Remix" as track name
    ]
    
    print("=== SHOULD BE SKIPPED ===")
    for title in should_skip:
        is_skipped = sync.is_non_music_post(title)
        status = "✅ SKIPPED" if is_skipped else "❌ NOT SKIPPED"
        print(f"{status}: '{title}'")
    
    print(f"\n=== SHOULD NOT BE SKIPPED ===")
    for title in should_not_skip:
        is_skipped = sync.is_non_music_post(title)  
        status = "✅ NOT SKIPPED" if not is_skipped else "❌ SKIPPED"
        print(f"{status}: '{title}'")

if __name__ == "__main__":
    test_skip_patterns()