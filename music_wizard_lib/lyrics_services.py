import re
import logging
import asyncio
import requests
from . import config

logger = logging.getLogger(__name__)


async def get_lyrics(artist: str, title: str) -> str:
    logger.info(f"Searching lyrics for Artist: '{artist}', Title: '{title}'")
    try:
        import lyricsgenius

        genius = lyricsgenius.Genius(
            config.GENIUS_ACCESS_TOKEN,
            verbose=False,
            remove_section_headers=False,
            timeout=15,
        )
        cleaned_title = re.sub(r"\(.*\)|\[.*\]", "", title).strip()
        # Run blocking network call in a thread to avoid blocking the event loop
        song = await asyncio.to_thread(genius.search_song, cleaned_title, artist)
        if not song or not song.lyrics:
            # Try again without the artist
            song = await asyncio.to_thread(genius.search_song, cleaned_title)
            if not song or not song.lyrics:
                return "Could not find lyrics for this song."

        lyrics = song.lyrics
        first_section_match = re.search(r"(\[.+\])", lyrics)
        if first_section_match:
            lyrics = lyrics[first_section_match.start() :]
        else:
            lines = lyrics.split("\n", 1)
            if len(lines) > 1:
                lyrics = lines[1]
        lyrics = re.split(r"\d*You might also like\d*", lyrics, flags=re.IGNORECASE)[0]
        lines = lyrics.strip().split("\n")
        if lines and lines[-1].strip().isdigit():
            lyrics = "\n".join(lines[:-1])
        return lyrics.strip()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error fetching lyrics: {e}", exc_info=True)
        return (
            f"An error occurred while fetching lyrics (HTTP {e.response.status_code})."
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while fetching lyrics: {e}", exc_info=True
        )
        return "An unexpected error occurred while fetching lyrics."
