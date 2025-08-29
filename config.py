"""
Configuration management for Overload Spotify Sync
"""

import os
from typing import Optional

class Config:
    """Configuration class that loads settings from environment variables"""
    
    def __init__(self):
        # Reddit API Configuration
        self.reddit_client_id = self._get_env_var('REDDIT_CLIENT_ID', required=True)
        self.reddit_client_secret = self._get_env_var('REDDIT_CLIENT_SECRET', required=True)
        
        # Spotify API Configuration
        self.spotify_client_id = self._get_env_var('SPOTIFY_CLIENT_ID', required=True)
        self.spotify_client_secret = self._get_env_var('SPOTIFY_CLIENT_SECRET', required=True)
        self.spotify_redirect_uri = self._get_env_var('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
        
        # Application Configuration
        self.min_upvotes = int(self._get_env_var('MIN_UPVOTES', '3'))
        self.playlist_name = self._get_env_var('PLAYLIST_NAME', 'notes from r/theoverload')
        
        # Validation
        self._validate_config()
    
    def _get_env_var(self, var_name: str, default: Optional[str] = None, required: bool = False) -> str:
        """Get environment variable with optional default and required validation"""
        value = os.getenv(var_name, default)
        
        if required and not value:
            raise ValueError(f"Required environment variable {var_name} is not set")
        
        return value or ''
    
    def _validate_config(self):
        """Validate configuration values"""
        if self.min_upvotes < 0:
            raise ValueError("MIN_UPVOTES must be non-negative")
        
        if not self.playlist_name.strip():
            raise ValueError("PLAYLIST_NAME cannot be empty")
    
    def __str__(self) -> str:
        """String representation (hiding sensitive information)"""
        return f"""Config:
  Reddit Client ID: {'*' * len(self.reddit_client_id) if self.reddit_client_id else 'Not set'}
  Spotify Client ID: {'*' * len(self.spotify_client_id) if self.spotify_client_id else 'Not set'}
  Min Upvotes: {self.min_upvotes}
  Playlist Name: {self.playlist_name}
  Redirect URI: {self.spotify_redirect_uri}"""