# GitHub Actions Setup Guide

This guide will help you set up automated daily syncing using GitHub Actions.

## Prerequisites

1. GitHub repository with this code
2. Reddit and Spotify API credentials (from your `.env` file)

## Step 1: Generate Refresh Token

First, run the setup script locally to generate a Spotify refresh token:

```bash
# Make sure your .env file is configured with your API credentials
source venv/bin/activate
python3 setup_github_secrets.py
```

This will output a `SPOTIFY_REFRESH_TOKEN` - copy this value.

## Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

### Add these **Repository Secrets**:

1. `REDDIT_CLIENT_ID` - Your Reddit app client ID
2. `REDDIT_CLIENT_SECRET` - Your Reddit app client secret  
3. `SPOTIFY_CLIENT_ID` - Your Spotify app client ID
4. `SPOTIFY_CLIENT_SECRET` - Your Spotify app client secret
5. `SPOTIFY_REFRESH_TOKEN` - The refresh token from Step 1

### Add these **Repository Variables** (optional):

1. `MIN_UPVOTES` - Minimum upvotes for posts (default: 3)
2. `PLAYLIST_NAME` - Name of your Spotify playlist (default: "notes from r/theoverload")

## Step 3: Enable GitHub Actions

1. Go to your repository → Actions tab
2. If prompted, click "I understand my workflows" to enable Actions
3. The workflow will automatically run daily at 11:30 PM UTC

## Step 4: Test the Setup

You can manually trigger the workflow to test:

1. Go to Actions tab → "Daily Overload Spotify Sync"
2. Click "Run workflow" → "Run workflow"
3. Monitor the execution and check the logs

## How It Works

- **Daily Schedule**: Runs automatically at 11:30 PM UTC every day
- **Headless Authentication**: Uses refresh token (no browser required)
- **Logging**: Saves execution logs as artifacts for 30 days
- **Error Handling**: Continues running even if individual posts fail

## Monitoring

- Check the Actions tab for execution history
- Download log artifacts to troubleshoot issues
- Logs show which tracks were added and any remix information detected

## Timezone Adjustment

To change when the sync runs, edit `.github/workflows/daily-sync.yml`:

```yaml
# Current: 11:30 PM UTC daily
- cron: '30 23 * * *'

# Examples:
# - cron: '0 6 * * *'   # 6:00 AM UTC daily
# - cron: '30 16 * * *' # 4:30 PM UTC daily  
```

Use [crontab.guru](https://crontab.guru) to help with cron syntax.

## Troubleshooting

**"No module named 'praw'"**: Dependencies failed to install - check the workflow logs

**"Invalid refresh token"**: Re-run `setup_github_secrets.py` and update the `SPOTIFY_REFRESH_TOKEN` secret

**"Could not find on Spotify"**: Normal - not all Reddit posts have matching Spotify tracks

**Workflow not running**: Check that the repository secrets are set correctly and GitHub Actions is enabled