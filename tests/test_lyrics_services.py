import importlib
import types
import sys

import pytest
import requests


@pytest.mark.asyncio
async def test_get_lyrics_success(monkeypatch):
    # Set required environment variables before importing modules
    monkeypatch.setenv("TELEGRAM_TOKEN", "dummy")
    monkeypatch.setenv("GENIUS_ACCESS_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    import music_wizard_lib.config as config
    importlib.reload(config)

    import music_wizard_lib.lyrics_services as lyrics_services
    importlib.reload(lyrics_services)

    captured = []
    lyrics_text = "Intro\n[Verse 1]\nLine1\nLine2\nYou might also like55\n55\n"

    class FakeSong:
        def __init__(self, lyrics):
            self.lyrics = lyrics

    class FakeGenius:
        def __init__(self, *args, **kwargs):
            pass

        def search_song(self, title, artist=None):
            captured.append((title, artist))
            return FakeSong(lyrics_text)

    fake_module = types.SimpleNamespace(Genius=FakeGenius)
    monkeypatch.setitem(sys.modules, "lyricsgenius", fake_module)

    result = await lyrics_services.get_lyrics("Artist", "The Song (feat. B)")

    assert result == "[Verse 1]\nLine1\nLine2"
    assert captured == [("The Song", "Artist")]


@pytest.mark.asyncio
async def test_get_lyrics_http_error(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "dummy")
    monkeypatch.setenv("GENIUS_ACCESS_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    import music_wizard_lib.config as config
    importlib.reload(config)

    import music_wizard_lib.lyrics_services as lyrics_services
    importlib.reload(lyrics_services)

    class FakeResponse:
        status_code = 404

    class FakeGenius:
        def __init__(self, *args, **kwargs):
            pass

        def search_song(self, title, artist=None):
            err = requests.exceptions.HTTPError("boom")
            err.response = FakeResponse()
            raise err

    fake_module = types.SimpleNamespace(Genius=FakeGenius)
    monkeypatch.setitem(sys.modules, "lyricsgenius", fake_module)

    result = await lyrics_services.get_lyrics("A", "T")

    assert result == "An error occurred while fetching lyrics (HTTP 404)."


@pytest.mark.asyncio
async def test_get_lyrics_missing(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "dummy")
    monkeypatch.setenv("GENIUS_ACCESS_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    import music_wizard_lib.config as config
    importlib.reload(config)

    import music_wizard_lib.lyrics_services as lyrics_services
    importlib.reload(lyrics_services)

    responses = [types.SimpleNamespace(lyrics=None), None]

    class FakeGenius:
        def __init__(self, *args, **kwargs):
            pass

        def search_song(self, title, artist=None):
            return responses.pop(0)

    fake_module = types.SimpleNamespace(Genius=FakeGenius)
    monkeypatch.setitem(sys.modules, "lyricsgenius", fake_module)

    result = await lyrics_services.get_lyrics("A", "T")

    assert result == "Could not find lyrics for this song."
