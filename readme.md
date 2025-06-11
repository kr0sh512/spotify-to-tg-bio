# Sync Spotify “Now Playing” → Telegram Bio

This script updates your Telegram "About" (bio) with your current Spotify track, prepending a 🎶 line. It checks Spotify every 45 seconds and updates or clears your Telegram bio accordingly.

## Features

- Checks Spotify every 45 seconds for your currently playing track
- Prepends/clears a 🎶 … line in your Telegram About
- Designed to run in the background:

    ```bash
    nohup python3 nowplaying.py &
    ```

## Requirements

- Python 3.7+
- [spotipy](https://spotipy.readthedocs.io/)
- [telethon](https://docs.telethon.dev/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. **Clone** repository:

```bash
git clone https://github.com/kr0sh512/spotify-to-tg-bio
cd ./spotify-to-tg-bio
```

1. **Create a `.env` file** in the script directory with the following variables:

    ```plain
    TG_API_ID=your_telegram_api_id
    TG_API_HASH=your_telegram_api_hash
    SPOTIFY_CLIENT_ID=your_spotify_client_id
    SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
    SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
    ```

    - Get Telegram API credentials from [my.telegram.org](https://my.telegram.org).
    - Get Spotify credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

2. **First run**: The script will prompt you to log in to both Spotify (via Web) and Telegram.

## Usage

```bash
python3 nowplaying.py [--debug] [--single] [--help]
```

- `--debug`   Print debug messages
- `--single`  Run only one iteration and exit
- `--help`    Show help message and exit

## Run in background using `systemd`

To run the script as a background service with `systemd`, copy a unit file:

```bash
sudo cp ./spotify-telegram-bio.service /etc/systemd/system/spotify-telegram-bio.service
```

```ini
# /etc/systemd/system/spotify-telegram-bio.service
[Unit]
Description=Sync Spotify Now Playing to Telegram Bio
After=network.target

[Service]
Type=simple
WorkingDirectory=/your/dir/to/script
ExecStart=/usr/bin/python3 script.py
Restart=always
User=yourusername
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Replace `yourusername` with your actual Linux username.

Then reload `systemd` and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now spotify-telegram-bio.service
```

Check status with:

```bash
systemctl status spotify-telegram-bio.service
```

View logs with:

```bash
sudo journalctl -fu spotify-telegram-bio.service
```

## Notes

- The script requires Spotify OAuth scope: `user-read-playback-state`.
- Your Telegram session is stored locally as `my_account.session`.
- The script only updates your bio if the track changes.

## Disclaimer

Use at your own risk. This script modifies your Telegram bio and uses your API credentials.
