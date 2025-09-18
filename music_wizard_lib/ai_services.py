import json
import logging
import openai
from . import config

logger = logging.getLogger(__name__)

try:
    openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)
except Exception as e:
    logger.error(f"Could not initialize OpenAI client: {e}")
    openai_client = None


async def extract_song_info_with_openai(video_title: str) -> dict:
    logger.info(f"Attempting to extract info from '{video_title}' with OpenAI.")
    system_prompt = (
        "You are an expert at parsing song information. Extract the artist and "
        "song title from the following "
        "YouTube video title. Respond ONLY with a valid JSON object containing "
        "'artist' and 'title' keys. "
        "If you cannot determine one of them, set its value to null. "
        "For example, for 'Artist - Song (Official Video)', respond with "
        '{"artist": "Artist", "title": "Song"}. '
        "If you know the song name and author yourself, respond with them. For "
        "example: eye of the tiger acapella beat drop - you know that its eye of "
        "the tiger by Survivor"
    )
    try:
        response = await openai_client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": video_title},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            timeout=10,
        )
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        artist = parsed_json.get("artist")
        title = parsed_json.get("title")
        logger.info(f"OpenAI extracted: Artist='{artist}', Title='{title}'")
        return {"artist": artist, "title": title}
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}", exc_info=True)
        return {"artist": None, "title": None}


async def generate_song_list_with_ai(vibe, num_songs=10):
    logger.info(f"Asking AI to generate a playlist for the vibe: '{vibe}'...")
    system_prompt = (
        "You are a helpful playlist assistant. "
        "Your task is to generate a list of songs "
        "based on a user's request. You must respond *only* with a valid JSON object "
        "that has a single key, 'songs', which contains an array of song objects. "
        "Each object in the array must have two string keys: 'artist' and 'title'."
    )
    user_prompt = (
        f'Generate a playlist of {num_songs} songs for the following vibe: "{vibe}"'
    )
    try:
        response = await openai_client.chat.completions.create(
            model=config.OPENAI_PLAYLIST_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("songs", [])
    except Exception as e:
        logger.error(f"OpenAI API call for playlist failed: {e}")
        return None
