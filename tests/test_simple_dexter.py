#!/usr/bin/env python3
"""
Simple test for Dexter track
"""

# Test our smart quote fix in isolation
def test_smart_quotes():
    # From our debug: b'I Don\xe2\x80\x99t Care' 
    track1 = bytes([73, 32, 68, 111, 110, 226, 128, 153, 116, 32, 67, 97, 114, 101]).decode('utf-8')  # Smart apostrophe from Reddit
    track2 = "I Don't Care"  # Regular apostrophe (from Spotify)
    
    print(f"Track1 (Reddit): '{track1}'")  
    print(f"Track1 bytes: {track1.encode('utf-8')}")
    print(f"Track2 (Spotify): '{track2}'")
    print(f"Track2 bytes: {track2.encode('utf-8')}")
    
    # Test direct comparison
    print(f"Direct match: {track1 == track2}")
    print(f"Track1 in Track2: {track1.lower() in track2.lower()}")
    
    # Test with normalization
    def normalize_text(text):
        return text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
    
    track1_norm = normalize_text(track1.lower())
    track2_norm = normalize_text(track2.lower())
    
    print(f"Track1 normalized: '{track1_norm}'")
    print(f"Track1 norm bytes: {track1_norm.encode('utf-8')}")
    print(f"Track2 normalized: '{track2_norm}'")  
    print(f"Track2 norm bytes: {track2_norm.encode('utf-8')}")
    
    print(f"Normalized match: {track1_norm == track2_norm}")
    print(f"Normalized 'in' test: {track1_norm in track2_norm}")

if __name__ == "__main__":
    test_smart_quotes()