from . import config


async def send_long_message(bot, chat_id: int, text: str):
    if len(text) <= config.TELEGRAM_MESSAGE_LIMIT:
        await bot.send_message(chat_id=chat_id, text=text)
        return
    chunks = [
        text[i : i + config.TELEGRAM_MESSAGE_LIMIT]
        for i in range(0, len(text), config.TELEGRAM_MESSAGE_LIMIT)
    ]
    for chunk in chunks:
        await bot.send_message(chat_id=chat_id, text=chunk)
