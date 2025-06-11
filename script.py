#!/usr/bin/env python3
"""
Sync Spotify “Now Playing” → Telegram Bio
----------------------------------------
• Checks Spotify every 45 seconds
• Prepends/clears a 🎶 … line in your Telegram About
• Designed to be run with:  nohup python3 nowplaying.py &
"""

import os
import time
import spotipy
import sys

from telethon.sync import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


# ────────────────────────────────────────────
# 1.  CONFIGURATION (read from env for safety)
# ────────────────────────────────────────────

load_dotenv()

TG_API_ID = int(os.environ["TG_API_ID"])  # from https://my.telegram.org
TG_API_HASH = os.environ["TG_API_HASH"]

SPOTIPY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"
)

CHECK_EVERY_SEC = 45
PRINT_DEBUG = "--debug" in sys.argv
SINGLE_RUN = "--single" in sys.argv


# ────────────────────────────────────────────
# 2.  HELPERS
# ────────────────────────────────────────────
def track_as_string(item: dict) -> str:
    """Make 'Song - Artist1, Artist2'."""
    artists = ", ".join(a["name"] for a in item["artists"])
    return f"\"{item['name']}\" by {artists}"
    # return f"{artists} - {item['name']}"


def strip_old_track(bio: str) -> str:
    """Remove anything after the first 🎶"""
    return bio.split("🎶")[0].rstrip()


def printd(*args, **kwargs) -> None:
    """Print debug messages if PRINT_DEBUG is True."""
    if PRINT_DEBUG:
        print(*args, **kwargs)


# ────────────────────────────────────────────
# 3.  MAIN LOOP
# ────────────────────────────────────────────
def main() -> None:
    # Spotipy OAuth (needs scope 'user-read-playback-state')
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope="user-read-playback-state",
            cache_path=".cache",  # reuse token silently
        )
    )

    # One Telegram session for the whole run
    with TelegramClient("my_account", TG_API_ID, TG_API_HASH) as client:
        last_track = None  # remember what we already set

        while True:
            try:
                # ── 3-a  Spotify: what’s playing?
                pb = sp.current_playback()
                is_playing = pb and pb["is_playing"]

                # ── 3-b  Telegram: fetch current bio (once each loop)
                me = client.get_me()
                full = client(GetFullUserRequest(me.id))
                base_bio = strip_old_track(full.full_user.about or "")

                if is_playing and pb is not None and pb.get("item") is not None:
                    track_str = track_as_string(pb["item"])
                    nbsp = "\u00a0"
                    track_str = track_str.replace(" ", nbsp)  # non-breaking spaces

                    # Update only if changed
                    if track_str != last_track:
                        new_bio = f"{base_bio} 🎶{nbsp}Now{nbsp}listening: {track_str}".strip()
                        client(UpdateProfileRequest(about=new_bio))
                        printd("🎶 Updated bio →", new_bio)
                        last_track = track_str
                else:
                    # Nothing playing → clear any old 🎶 line
                    if last_track is not None:
                        client(UpdateProfileRequest(about=base_bio))
                        printd("⊘ Cleared track from bio")
                        last_track = None

            except Exception as e:
                print("⚠️  Error:", e)

            if SINGLE_RUN:
                print("🔚 Single run mode, exiting.")
                break

            time.sleep(CHECK_EVERY_SEC)


# ────────────────────────────────────────────
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Sync Spotify Now Playing to Telegram Bio")
        print("--------------------------------------------------")
        print("Usage: python3 script.py [--debug] [--single] [--help]")
        print("  --debug   Print debug messages")
        print("  --single  Run only one iteration and exit")
        print("  --help    Show this help message and exit")
        sys.exit(0)

    main()
