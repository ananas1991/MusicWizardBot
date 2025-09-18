import importlib
import pytest


class FakeBot:
    def __init__(self):
        self.messages = []

    async def send_message(self, chat_id: int, text: str):
        self.messages.append((chat_id, text))


@pytest.mark.asyncio
async def test_send_long_message(monkeypatch):
    # Set required environment variables before importing modules
    monkeypatch.setenv("TELEGRAM_TOKEN", "dummy")
    monkeypatch.setenv("GENIUS_ACCESS_TOKEN", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    import music_wizard_lib.config as config

    importlib.reload(config)

    # Use a small message limit for easier testing
    monkeypatch.setattr(config, "TELEGRAM_MESSAGE_LIMIT", 10)

    import music_wizard_lib.utils as utils

    importlib.reload(utils)

    fake_bot = FakeBot()
    text = "a" * 25
    await utils.send_long_message(fake_bot, chat_id=1, text=text)

    # Expect the message to be split into three chunks of 10, 10, and 5
    # characters
    expected = [
        (1, "a" * 10),
        (1, "a" * 10),
        (1, "a" * 5),
    ]
    assert fake_bot.messages == expected
