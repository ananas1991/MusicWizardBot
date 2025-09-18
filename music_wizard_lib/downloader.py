import os
import json
import asyncio
import subprocess
import logging

from music_wizard_lib.config import AUDIO_QUALITY

logger = logging.getLogger(__name__)


async def download_song_from_youtube(url: str, download_folder: str) -> (dict, str):
    # Get metadata
    meta_command = ["yt-dlp", "--dump-json", "--no-playlist", url]
    meta_process = await asyncio.to_thread(
        subprocess.run,
        meta_command,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    metadata = json.loads(meta_process.stdout)

    # Map audio quality to yt-dlp setting
    quality_mapping = {
        "perfect": "0",
        "high": "3",
        "medium": "6",
        "low": "9",
    }
    audio_quality = quality_mapping.get(AUDIO_QUALITY, "0")

    # Download audio
    output_template = os.path.join(download_folder, "%(title)s.%(ext)s")
    command = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        audio_quality,
        "--output",
        output_template,
        "--no-playlist",
        url,
    ]
    await asyncio.to_thread(
        subprocess.run, command, check=True, capture_output=True, text=True, timeout=300
    )

    downloaded_files = os.listdir(download_folder)
    if not downloaded_files:
        raise FileNotFoundError("yt-dlp finished, but no file was found.")

    audio_filepath = os.path.join(download_folder, downloaded_files[0])
    return metadata, audio_filepath
