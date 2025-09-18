import os
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from . import config

logger = logging.getLogger(__name__)


def get_authenticated_service():
    try:
        credentials = None
        if os.path.exists(config.TOKEN_FILE):
            with open(config.TOKEN_FILE, "rb") as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not os.path.exists(config.CLIENT_SECRET_FILE):
                    raise FileNotFoundError(
                        f"Error: The credentials file '{config.CLIENT_SECRET_FILE}' "
                        "was not found."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CLIENT_SECRET_FILE, config.SCOPES
                )
                credentials = flow.run_local_server(port=0)
            with open(config.TOKEN_FILE, "wb") as token:
                pickle.dump(credentials, token)
        return build(config.API_NAME, config.API_VERSION, credentials=credentials)
    except Exception as e:
        logger.error(f"Failed to authenticate with YouTube: {e}")
        return None


def search_for_song_on_youtube(youtube, song):
    query = f"{song['artist']} {song['title']}"
    logger.info(f"Searching YouTube for '{query}'...")
    try:
        search_response = (
            youtube.search()
            .list(q=query, part="snippet", maxResults=1, type="video")
            .execute()
        )
        items = search_response.get("items", [])
        if not items:
            return None
        return items[0]["id"]["videoId"]
    except HttpError as e:
        logger.error(f"Youtube failed: {e}")
        return None


def create_youtube_playlist(youtube, title, description):
    try:
        playlist_response = (
            youtube.playlists()
            .insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "defaultLanguage": "en",
                    },
                    "status": {"privacyStatus": "unlisted"},
                },
            )
            .execute()
        )
        return playlist_response["id"]
    except HttpError as e:
        logger.error(f"Could not create YouTube playlist: {e}")
        return None


def add_video_to_youtube_playlist(youtube, playlist_id, video_id):
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        ).execute()
        return True
    except HttpError:
        return False
