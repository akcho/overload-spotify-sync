#!/usr/bin/env python3
"""
Helper script to generate a refresh token for GitHub Actions
Run this locally once to get the refresh token, then add it to GitHub secrets
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

def get_refresh_token():
    """Get refresh token for headless authentication"""
    
    # Use your local credentials
    auth_manager = SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope='playlist-modify-public playlist-modify-private',
        cache_path='.cache'
    )
    
    # This will prompt for authentication if no valid token exists
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    # Test the connection
    user = spotify.current_user()
    print(f"Successfully authenticated as: {user['display_name']} ({user['id']})")
    
    # Get the refresh token
    token_info = auth_manager.get_cached_token()
    if token_info and 'refresh_token' in token_info:
        refresh_token = token_info['refresh_token']
        print(f"\n🔑 Add this refresh token to your GitHub secrets:")
        print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")
        print("\n📋 You'll also need these secrets:")
        print(f"REDDIT_CLIENT_ID={os.getenv('REDDIT_CLIENT_ID')}")
        print(f"REDDIT_CLIENT_SECRET={os.getenv('REDDIT_CLIENT_SECRET')}")
        print(f"SPOTIFY_CLIENT_ID={os.getenv('SPOTIFY_CLIENT_ID')}")
        print(f"SPOTIFY_CLIENT_SECRET={os.getenv('SPOTIFY_CLIENT_SECRET')}")
        
        return refresh_token
    else:
        print("❌ Could not get refresh token")
        return None

if __name__ == "__main__":
    get_refresh_token()