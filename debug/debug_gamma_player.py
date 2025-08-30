#!/usr/bin/env python3
"""
Debug the Jeff Mills - Gamma Player version selection issue
"""

import sys
sys.path.append('..')
from overload_spotify_sync import OverloadSpotifySync

def debug_gamma_player():
    """Debug Jeff Mills - Gamma Player search results"""
    
    sync = OverloadSpotifySync(debug=True)
    
    # Test the search for Gamma Player
    print("=== DEBUGGING JEFF MILLS - GAMMA PLAYER ===")
    
    # Simulate the search
    try:
        results = sync.spotify.search(q='Jeff Mills Gamma Player', type='track', limit=10)
        tracks = results['tracks']['items']
        
        print(f"Found {len(tracks)} results:")
        for i, track in enumerate(tracks, 1):
            artist = track['artists'][0]['name']
            track_name = track['name']
            print(f"{i}. {artist} - {track_name}")
            
        print(f"\n=== TESTING TRACK MATCHING ===")
        
        # Test what our matching algorithm picks
        if tracks:
            best_match = sync.find_best_track_match(tracks, "Jeff Mills", "Gamma Player")
            if best_match:
                found_artist = best_match['artists'][0]['name']
                found_track = best_match['name']
                print(f"Our algorithm selected: {found_artist} - {found_track}")
                
                # Show the scoring
                print(f"\nScoring breakdown for selected track:")
                artist_score = sync.calculate_artist_score("Jeff Mills", found_artist)
                track_score = sync.calculate_track_score("Gamma Player", found_track)
                print(f"  Artist score: {artist_score}")
                print(f"  Track score: {track_score}")
            else:
                print("No confident match found")
                
        # Test all tracks to see their scores
        print(f"\n=== ALL TRACKS SCORING ===")
        for i, track in enumerate(tracks[:5], 1):  # Top 5 only
            artist = track['artists'][0]['name']
            track_name = track['name']
            
            artist_score = sync.calculate_artist_score("Jeff Mills", artist)
            track_score = sync.calculate_track_score("Gamma Player", track_name)
            
            print(f"{i}. {artist} - {track_name}")
            print(f"   Artist: {artist_score}, Track: {track_score}, Total: {artist_score + track_score}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_gamma_player()