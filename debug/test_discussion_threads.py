#!/usr/bin/env python3
"""
Test the discussion thread detection and comment processing logic
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import overload_spotify_sync
OverloadSpotifySync = overload_spotify_sync.OverloadSpotifySync

def test_discussion_threads():
    """Test discussion thread detection with real r/theoverload data"""
    
    sync = OverloadSpotifySync(debug=True)
    
    print("=== TESTING DISCUSSION THREAD DETECTION ===")
    
    # Get recent posts (including submission objects)
    posts = sync.get_recent_posts()
    
    if not posts:
        print("No posts found to test")
        return
    
    print(f"\nFound {len(posts)} total posts")
    print("\n=== ANALYZING EACH POST FOR DISCUSSION THREAD CRITERIA ===")
    
    discussion_threads = []
    
    for post in posts:
        submission = post['submission']
        title = post['title']
        
        print(f"\n--- Post: {title[:60]}... ---")
        print(f"  Comments: {submission.num_comments}")
        print(f"  Upvotes: {submission.score}")
        
        # Test each criterion individually
        meets_comment_count = submission.num_comments > 20
        meets_upvote_threshold = submission.score > 5
        
        print(f"  ✓ Comment count > 20: {meets_comment_count}")
        print(f"  ✓ Upvotes > 5: {meets_upvote_threshold}")
        
        if meets_comment_count and meets_upvote_threshold:
            print("  → Checking track sharing density...")
            try:
                density = sync.calculate_track_sharing_density(submission)
                meets_density = density >= 0.25
                print(f"  ✓ Track sharing density ≥ 25%: {meets_density} ({density:.1%})")
                
                if meets_density:
                    print("  🎯 QUALIFIES AS DISCUSSION THREAD!")
                    discussion_threads.append(post)
                else:
                    print("  ❌ Does not meet track sharing threshold")
                    
            except Exception as e:
                print(f"  ❌ Error calculating density: {e}")
        else:
            print("  ❌ Does not meet basic criteria")
    
    print(f"\n=== SUMMARY ===")
    print(f"Posts analyzed: {len(posts)}")
    print(f"Discussion threads found: {len(discussion_threads)}")
    
    if discussion_threads:
        print(f"\nDiscussion threads:")
        for dt in discussion_threads:
            print(f"  • {dt['title'][:50]}... ({dt['submission'].num_comments} comments, {dt['score']} upvotes)")
            
        # Test comment extraction
        print(f"\n=== TESTING COMMENT EXTRACTION ===")
        comments = sync.get_comments_from_discussion_threads(discussion_threads)
        
        if comments:
            print(f"\nExtracted {len(comments)} qualifying comments:")
            for comment in comments[:5]:  # Show first 5
                print(f"  • ({comment['score']} upvotes) {comment['body'][:60]}...")
                
            # Test track extraction from comments
            print(f"\n=== TESTING TRACK EXTRACTION FROM COMMENTS ===")
            tracks_found = 0
            for i, comment in enumerate(comments, 1):
                music_info = sync.extract_music_info_from_comment(comment)
                if music_info:
                    tracks_found += 1
                    source = music_info.get('source', 'unknown')
                    artist = music_info.get('artist', 'Unknown')
                    track = music_info.get('track', 'Unknown')
                    print(f"  ✓ Comment {i}: Found track from {source}: {artist} - {track}")
                else:
                    print(f"  ✗ Comment {i}: No track found - {comment['body'][:50]}...")
                    
            print(f"\nTracks extracted from comments: {tracks_found}/{len(comments)}")
        else:
            print("No qualifying comments found")
    else:
        print("No discussion threads found in current time window")

if __name__ == "__main__":
    test_discussion_threads()