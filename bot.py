import os
import logging
import uuid
import shutil
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)

# Import from your new library
from music_wizard_lib import (
    config,
    ai_services,
    lyrics_services,
    youtube_services,
    downloader,
    utils,
    localization,
)

logger = logging.getLogger(__name__)


def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Retrieve the user's language choice."""
    return context.user_data.get("lang", "en")


def build_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Return the main menu keyboard for a given language."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"🎵 {localization.get_text('download_single_song', lang=lang)}",
                callback_data="download_song",
            )
        ],
        [
            InlineKeyboardButton(
                f"✨ {localization.get_text('create_ai_playlist', lang=lang)}",
                callback_data="create_playlist",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# === Conversation States ===
(
    CHOOSE_LANGUAGE,
    CHOOSE_ACTION,
    HANDLE_LINK,
    AWAITING_LYRICS_CHOICE,
    PLAYLIST_VIBE,
    PLAYLIST_SONGS,
    PLAYLIST_TITLE,
    PLAYLIST_DESC,
    PLAYLIST_DECISION,
) = range(9)

# === Telegram Bot UI and Handlers ===


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation by asking the user to choose a language."""
    context.user_data.clear()
    keyboard = [
        [
            InlineKeyboardButton(
                localization.get_text("english_button"), callback_data="lang_en"
            ),
            InlineKeyboardButton(
                localization.get_text("russian_button"), callback_data="lang_ru"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = localization.get_text("language_prompt")
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    return CHOOSE_LANGUAGE


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the selected language and show the main menu."""
    query = update.callback_query
    await query.answer()
    lang = "en" if query.data == "lang_en" else "ru"
    context.user_data["lang"] = lang
    reply_markup = build_main_menu_keyboard(lang)
    await query.edit_message_text(
        localization.get_text("welcome", lang=lang), reply_markup=reply_markup
    )
    return CHOOSE_ACTION


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the main menu, used as a fallback to return to the start."""
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    reply_markup = build_main_menu_keyboard(lang)
    await query.edit_message_text(
        localization.get_text("menu_prompt", lang=lang), reply_markup=reply_markup
    )
    return CHOOSE_ACTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the current operation and ends the conversation."""
    lang = get_lang(context)
    await update.message.reply_text(
        localization.get_text("cancelled", lang=lang),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# --- Single Song Download Flow ---


async def request_youtube_link(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Asks the user to send a YouTube link OR a song name."""
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(
        text=localization.get_text("send_link", lang=lang)
    )
    return HANDLE_LINK


async def handle_youtube_link(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Processes a link or song name, sends the song, and asks about lyrics."""
    lang = get_lang(context)
    text = update.message.text.strip()

    # Determine if it's a YouTube link
    is_youtube = "youtube.com/" in text or "youtu.be/" in text

    if not is_youtube:
        # Treat as search query
        lang = get_lang(context)
        await update.message.reply_text(
            localization.get_text("searching", lang=lang, query=text)
        )
        try:
            youtube = await asyncio.to_thread(
                youtube_services.get_authenticated_service
            )
            if not youtube:
                await update.message.reply_text(
                    localization.get_text("auth_error", lang=lang)
                )
                return HANDLE_LINK
            video_id = await asyncio.to_thread(
                youtube_services.search_for_song_on_youtube,
                youtube,
                {"title": text, "artist": "# "},
            )
            if not video_id:
                await update.message.reply_text(
                    localization.get_text("not_found", lang=lang)
                )
                return HANDLE_LINK
            text = f"https://www.youtube.com/watch?v={video_id}"
        except Exception as e:
            logger.error(f"Error searching for song: {e}", exc_info=True)
            await update.message.reply_text(
                localization.get_text("search_error", lang=lang)
            )
            return HANDLE_LINK

    # Now, `text` is guaranteed to be a valid YouTube URL.
    url = text

    chat_id = update.effective_chat.id
    download_folder = f"temp_{uuid.uuid4()}"
    os.makedirs(download_folder, exist_ok=True)

    processing_message = await update.message.reply_text(
        localization.get_text("link_received", lang=lang)
    )

    try:
        await context.bot.edit_message_text(
            text=localization.get_text("downloading", lang=lang),
            chat_id=chat_id,
            message_id=processing_message.message_id,
        )
        metadata, audio_filepath = await downloader.download_song_from_youtube(
            url, download_folder
        )

        video_title = metadata.get("title", "Unknown Title")
        openai_info = await ai_services.extract_song_info_with_openai(video_title)
        song_title = openai_info.get("title") or metadata.get("track") or video_title
        song_artist = (
            openai_info.get("artist") or metadata.get("artist") or "Unknown Artist"
        )

        await context.bot.edit_message_text(
            text=localization.get_text("download_complete", lang=lang),
            chat_id=chat_id,
            message_id=processing_message.message_id,
        )

        with open(audio_filepath, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                filename=os.path.basename(audio_filepath),
                caption=f"{song_title} by {song_artist}",
                title=song_title,
                performer=song_artist,
            )

        await context.bot.delete_message(
            chat_id=chat_id, message_id=processing_message.message_id
        )

        callback_data = f"lyrics_{uuid.uuid4()}"
        context.chat_data[callback_data] = {"artist": song_artist, "title": song_title}

        keyboard = [
            [
                InlineKeyboardButton(
                    localization.get_text("get_lyrics", lang=lang),
                    callback_data=callback_data,
                )
            ],
            [
                InlineKeyboardButton(
                    localization.get_text("main_menu", lang=lang),
                    callback_data="main_menu",
                )
            ],
        ]
        await update.message.reply_text(
            localization.get_text("ask_lyrics", lang=lang),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        logger.error(f"Error processing link {url}: {e}", exc_info=True)
        await context.bot.edit_message_text(
            text=localization.get_text("error", lang=lang, error=e),
            chat_id=chat_id,
            message_id=processing_message.message_id,
        )
        return await start(update, context)  # On error, restart the conversation
    finally:
        if os.path.exists(download_folder):
            shutil.rmtree(download_folder, ignore_errors=True)

    # Transition to the state where we wait for the user to click a button
    return AWAITING_LYRICS_CHOICE


async def lyrics_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handles the 'Get Lyrics' button press and returns to the main menu state."""
    query = update.callback_query
    await query.answer()
    callback_data_key = query.data
    song_info = context.chat_data.get(callback_data_key)

    lang = get_lang(context)
    await query.edit_message_text(
        text=localization.get_text("searching_lyrics", lang=lang)
    )

    if not song_info:
        await query.edit_message_text(
            text=localization.get_text("request_expired", lang=lang)
        )
        return await main_menu(update, context)

    lyrics_text = await lyrics_services.get_lyrics(
        song_info["artist"], song_info["title"]
    )
    full_text = localization.get_text(
        "lyrics_header",
        lang=lang,
        title=song_info["title"],
        artist=song_info["artist"],
    ) + f"{lyrics_text}"

    # Send lyrics as a new message. edit_message_text above keeps the old message
    # as feedback.
    await utils.send_long_message(context.bot, query.message.chat_id, full_text)

    del context.chat_data[callback_data_key]

    # Show main menu again and return to start state
    reply_markup = build_main_menu_keyboard(lang)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=localization.get_text("next_action", lang=lang),
        reply_markup=reply_markup,
    )
    return CHOOSE_ACTION


# --- AI Playlist Creation Flow ---


async def request_playlist_vibe(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["playlist"] = {}
    lang = get_lang(context)
    await query.edit_message_text(
        text=localization.get_text("playlist_intro", lang=lang)
    )
    return PLAYLIST_VIBE


async def handle_playlist_vibe(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["playlist"]["vibe"] = update.message.text
    lang = get_lang(context)
    await update.message.reply_text(
        localization.get_text("playlist_how_many", lang=lang)
    )
    return PLAYLIST_SONGS


async def handle_playlist_songs(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    try:
        num_songs = int(update.message.text)
        if not 1 <= num_songs <= 69:
            lang = get_lang(context)
            await update.message.reply_text(
                localization.get_text("number_range", lang=lang)
            )
            return PLAYLIST_SONGS
        context.user_data["playlist"]["num_songs"] = num_songs
        lang = get_lang(context)
        await update.message.reply_text(
            localization.get_text("generating", lang=lang)
        )

        playlist_data = context.user_data["playlist"]
        song_list = await ai_services.generate_song_list_with_ai(
            playlist_data["vibe"], playlist_data["num_songs"]
        )

        if not song_list:
            await update.message.reply_text(
                localization.get_text("ai_fail", lang=lang)
            )
            reply_markup = build_main_menu_keyboard(lang)
            await update.message.reply_text(
                localization.get_text("next_action", lang=lang),
                reply_markup=reply_markup,
            )
            return CHOOSE_ACTION

        song_list_text = "\n".join(
            [f"{i+1}. {s['title']} by {s['artist']}" for i, s in enumerate(song_list)]
        )
        await utils.send_long_message(
            context.bot,
            update.effective_chat.id,
            localization.get_text("ai_list", lang=lang, song_list=song_list_text),
        )

        context.user_data["playlist"]["songs"] = song_list

        keyboard = [
            [
                InlineKeyboardButton(
                    localization.get_text("upload_youtube", lang=lang),
                    callback_data="playlist_upload",
                )
            ],
            [
                InlineKeyboardButton(
                    localization.get_text("download_mp3s", lang=lang),
                    callback_data="playlist_download",
                )
            ],
            [
                InlineKeyboardButton(
                    localization.get_text("main_menu", lang=lang),
                    callback_data="main_menu",
                )
            ],
        ]

        await update.message.reply_text(
            localization.get_text("playlist_choice", lang=lang),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return PLAYLIST_DECISION
    except ValueError:
        lang = get_lang(context)
        await update.message.reply_text(
            localization.get_text("not_a_number", lang=lang)
        )
        return PLAYLIST_SONGS


async def handle_playlist_title(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["playlist"]["title"] = update.message.text
    lang = get_lang(context)
    await update.message.reply_text(
        localization.get_text("playlist_desc", lang=lang)
    )
    return PLAYLIST_DESC


async def handle_playlist_desc_and_create(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    description = update.message.text
    if description.lower() in ["none", "no", "skip"]:
        description = localization.get_text(
            "default_desc",
            lang=get_lang(context),
            vibe=context.user_data["playlist"]["vibe"],
        )
    context.user_data["playlist"]["description"] = description

    lang = get_lang(context)
    await update.message.reply_text(
        localization.get_text("creating_playlist", lang=lang)
    )

    playlist_data = context.user_data.get("playlist", {})
    song_list = playlist_data.get("songs", [])
    try:
        youtube = await asyncio.to_thread(youtube_services.get_authenticated_service)
        if not youtube:
            await update.message.reply_text(
                localization.get_text("auth_error", lang=lang)
            )
            return CHOOSE_ACTION

        playlist_id = await asyncio.to_thread(
            youtube_services.create_youtube_playlist,
            youtube,
            playlist_data.get("title"),
            playlist_data.get("description"),
        )
        if not playlist_id:
            await update.message.reply_text(
                localization.get_text("create_fail", lang=lang)
            )
            return CHOOSE_ACTION

        progress_message = await update.message.reply_text(
            localization.get_text("playlist_created", lang=lang, count=len(song_list))
        )

        for i, song in enumerate(song_list):
            video_id = await asyncio.to_thread(
                youtube_services.search_for_song_on_youtube, youtube, song
            )
            if video_id:
                await asyncio.to_thread(
                    youtube_services.add_video_to_youtube_playlist,
                    youtube,
                    playlist_id,
                    video_id,
                )
                await context.bot.edit_message_text(
                    text=localization.get_text(
                        "added_song",
                        lang=lang,
                        num=i + 1,
                        total=len(song_list),
                        title=song["title"],
                    ),
                    chat_id=update.effective_chat.id,
                    message_id=progress_message.message_id,
                )
            await asyncio.sleep(1)

        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        await context.bot.edit_message_text(
            text=localization.get_text("playlist_ready", lang=lang, url=playlist_url),
            chat_id=update.effective_chat.id,
            message_id=progress_message.message_id,
        )

    except FileNotFoundError:
        await update.message.reply_text(
            localization.get_text("auth_error", lang=lang)
        )
    except Exception as e:
        logger.error(f"Playlist creation failed: {e}", exc_info=True)
        await update.message.reply_text(
            localization.get_text("playlist_unexpected_error", lang=lang, error=e)
        )

    reply_markup = build_main_menu_keyboard(lang)
    await update.message.reply_text(
        localization.get_text("next_action", lang=lang),
        reply_markup=reply_markup,
    )
    return CHOOSE_ACTION


async def handle_playlist_upload(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(
        localization.get_text("playlist_name", lang=lang)
    )
    return PLAYLIST_TITLE


async def handle_playlist_download(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    playlist_data = context.user_data.get("playlist", {})
    song_list = playlist_data.get("songs", [])

    try:
        youtube = await asyncio.to_thread(youtube_services.get_authenticated_service)
        if not youtube:
            await query.edit_message_text(
                localization.get_text("auth_error", lang=lang)
            )
            return CHOOSE_ACTION

        progress_message = await query.edit_message_text(
            localization.get_text(
                "downloading_playlist",
                lang=lang,
                num=1,
                total=len(song_list),
                title=song_list[0]["title"] if song_list else "",
            )
        )

        for i, song in enumerate(song_list):
            if i > 0:
                await context.bot.edit_message_text(
                    text=localization.get_text(
                        "downloading_playlist",
                        lang=lang,
                        num=i + 1,
                        total=len(song_list),
                        title=song["title"],
                    ),
                    chat_id=query.message.chat_id,
                    message_id=progress_message.message_id,
                )
            video_id = await asyncio.to_thread(
                youtube_services.search_for_song_on_youtube, youtube, song
            )
            if not video_id:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=localization.get_text(
                        "song_not_found", lang=lang, title=song["title"]
                    ),
                )
                continue

            url = f"https://www.youtube.com/watch?v={video_id}"
            download_folder = f"temp_{uuid.uuid4()}"
            os.makedirs(download_folder, exist_ok=True)
            try:
                metadata, audio_filepath = await downloader.download_song_from_youtube(
                    url, download_folder
                )
                video_title = metadata.get("title", "Unknown Title")
                openai_info = await ai_services.extract_song_info_with_openai(
                    video_title
                )
                song_title = (
                    openai_info.get("title") or metadata.get("track") or video_title
                )
                song_artist = (
                    openai_info.get("artist")
                    or metadata.get("artist")
                    or "Unknown Artist"
                )

                with open(audio_filepath, "rb") as audio_file:
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=audio_file,
                        filename=os.path.basename(audio_filepath),
                        caption=f"{song_title} by {song_artist}",
                        title=song_title,
                        performer=song_artist,
                    )
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}", exc_info=True)
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=localization.get_text(
                        "download_song_fail", lang=lang, title=song["title"]
                    ),
                )
            finally:
                if os.path.exists(download_folder):
                    shutil.rmtree(download_folder, ignore_errors=True)

        await context.bot.edit_message_text(
            text=localization.get_text("songs_sent", lang=lang),
            chat_id=query.message.chat_id,
            message_id=progress_message.message_id,
        )

    except Exception as e:
        logger.error(f"Download playlist failed: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=localization.get_text("playlist_unexpected_error", lang=lang, error=e),
        )

    reply_markup = build_main_menu_keyboard(lang)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=localization.get_text("next_action", lang=lang),
        reply_markup=reply_markup,
    )
    return CHOOSE_ACTION


# === Main Bot Setup ===


def main():
    if not ai_services.openai_client:
        logger.error("OpenAI client not initialized. The bot cannot start.")
        return

    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        allow_reentry=True,
        states={
            CHOOSE_LANGUAGE: [
                CallbackQueryHandler(choose_language, pattern="^lang_")
            ],
            CHOOSE_ACTION: [
                CallbackQueryHandler(request_youtube_link, pattern="^download_song$"),
                CallbackQueryHandler(
                    request_playlist_vibe, pattern="^create_playlist$"
                ),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            HANDLE_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            AWAITING_LYRICS_CHOICE: [
                CallbackQueryHandler(lyrics_button_callback, pattern=r"^lyrics_"),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            PLAYLIST_VIBE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_playlist_vibe),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            PLAYLIST_SONGS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_playlist_songs),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            PLAYLIST_DECISION: [
                CallbackQueryHandler(
                    handle_playlist_upload, pattern="^playlist_upload$"
                ),
                CallbackQueryHandler(
                    handle_playlist_download, pattern="^playlist_download$"
                ),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            PLAYLIST_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_playlist_title),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
            PLAYLIST_DESC: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_playlist_desc_and_create
                ),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(main_menu, pattern="^main_menu$"),
        ],
        per_user=True,
        per_chat=False,
    )

    application.add_handler(conv_handler)

    logger.info("Music Wizard Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
