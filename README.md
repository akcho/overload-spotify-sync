# Overload Spotify Sync

Automatically sync music posts from r/theoverload to a Spotify playlist. This tool fetches daily music posts with sufficient upvotes and adds them to your Spotify playlist.

## Features

- 🎵 **Multi-platform support**: Works with YouTube, Spotify, SoundCloud, and Bandcamp links
- 📊 **Smart filtering**: Only includes posts with configurable minimum upvotes
- 🎯 **Intelligent parsing**: Extracts artist and track names from various title formats
- 🔄 **Duplicate prevention**: Avoids adding the same song multiple times
- ⏰ **Daily automation**: Run automatically at the end of each day
- 📝 **Comprehensive logging**: Track all activities and errors

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/overload-spotify-sync.git
   cd overload-spotify-sync
   ```

2. **Run the setup script**
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure your API credentials** (see [API Setup](#api-setup) below)
   ```bash
   nano .env
   ```

4. **Test the sync**
   ```bash
   python3 overload_spotify_sync.py
   ```

5. **Set up daily automation**
   ```bash
   ./scripts/install_cron.sh
   ```

## API Setup

### Reddit API

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note your `client_id` (under the app name) and `client_secret`

### Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Click "Create an App"
3. Fill in the app details
4. Note your `Client ID` and `Client Secret`
5. In Settings, add `http://localhost:8888/callback` as a Redirect URI

### Environment Configuration

Edit the `.env` file with your credentials:

```bash
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Spotify API  
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

# Configuration
MIN_UPVOTES=3
PLAYLIST_NAME=notes from r/theoverload
```

## How It Works

1. **Fetch Posts**: Gets posts from r/theoverload from the last 24 hours with minimum upvotes
2. **Extract Music Info**: Parses artist and track names from:
   - YouTube video titles
   - Spotify track URLs
   - SoundCloud links
   - Bandcamp pages
   - Reddit post titles using various patterns
3. **Search Spotify**: Finds matching tracks on Spotify using multiple search strategies
4. **Update Playlist**: Adds new tracks to your Spotify playlist, avoiding duplicates

## Supported Title Formats

The tool recognizes these common patterns in post titles:

- `Artist - Track`
- `Artist: Track`
- `Track by Artist`
- `[Artist] Track`
- `Artist | Track`
- `Artist "Track"`

## Manual Usage

Run the sync manually:
```bash
python3 overload_spotify_sync.py
```

Run with custom configuration:
```bash
MIN_UPVOTES=5 PLAYLIST_NAME="My Custom Playlist" python3 overload_spotify_sync.py
```

## Automation

The tool includes scripts for daily automation:

- `scripts/setup.sh`: Initial setup and dependency installation
- `scripts/daily_sync.sh`: Wrapper script for cron jobs
- `scripts/install_cron.sh`: Install daily cron job (runs at 11:30 PM)

### Cron Job Management

```bash
# View current cron jobs
crontab -l

# Edit cron jobs manually
crontab -e

# Remove all cron jobs
crontab -r
```

## Logging

The application creates two log files:

- `overload_spotify_sync.log`: Detailed application logs
- `daily_sync.log`: Daily cron job execution logs

View recent logs:
```bash
tail -f overload_spotify_sync.log
```

## Project Structure

```
overload-spotify-sync/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── overload_spotify_sync.py    # Main application
├── config.py                   # Configuration management
└── scripts/
    ├── setup.sh                # Setup automation
    ├── daily_sync.sh          # Cron wrapper
    └── install_cron.sh        # Cron installation
```

## Requirements

- Python 3.7+
- Reddit API credentials
- Spotify API credentials
- Internet connection

## Dependencies

- `praw`: Reddit API wrapper
- `spotipy`: Spotify API wrapper
- `requests`: HTTP requests
- `python-dotenv`: Environment variable management

## Troubleshooting

### Common Issues

**"No posts found"**: Check if r/theoverload has new posts with enough upvotes

**Spotify authentication errors**: Ensure your redirect URI matches exactly in both `.env` and Spotify app settings

**"Required environment variable not set"**: Check that all variables in `.env` are properly configured

**Permission denied on scripts**: Run `chmod +x scripts/*.sh`

### Debug Mode

Enable verbose logging by setting the log level in the script:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for personal use only. Respect Reddit's and Spotify's API terms of service. The tool does not download or redistribute copyrighted content.