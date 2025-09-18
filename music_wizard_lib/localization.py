MESSAGES = {
    "en": {
        "language_prompt": "Please choose your language / выберите язык",
        "english_button": "English",
        "russian_button": "Русский",
        "download_single_song": "Download Single Song",
        "create_ai_playlist": "Create AI Playlist",
        "welcome": "👋 Welcome to MusicWizard!\n\nWhat would you like to do?",
        "menu_prompt": "What would you like to do?",
        "cancelled": "Operation cancelled. Send /start to begin again.",
        "send_link": (
            "🔗 Please send me the YouTube link **or type the name of the song "
            "you want to download**."
        ),
        "searching": "🔎 Searching YouTube for: {query}",
        "auth_error": (
            "🔴 This feature is not working currently, please notify admin at "
            "@ananas19911."
        ),
        "not_found": "❌ Sorry, couldn't find that song on YouTube. Please try again!",
        "search_error": "❌ There was an error searching YouTube. Please try again.",
        "link_received": "🔗 Link received. Working on it...",
        "downloading": "⬇️ Downloading...",
        "download_complete": "✅ Download complete! Uploading to chat...",
        "get_lyrics": "📄 Get Lyrics",
        "main_menu": "⬅️ Main Menu",
        "ask_lyrics": "Song sent! Would you like the lyrics?",
        "error": "An error occurred: {error}",
        "searching_lyrics": "📄 Searching for lyrics...",
        "request_expired": "Sorry, this request has expired.",
        "lyrics_header": "📜 Lyrics for '{title}' by {artist}\n\n",
        "next_action": "What would you like to do next?",
        "playlist_intro": (
            "🎧 Let's create a playlist! What's the vibe, theme, or occasion?\n\n"
        ),
        "playlist_how_many": (
            "🎶 Got it. How many songs should be in the playlist? "
            "(e.g., 10, 25)"
        ),
        "number_range": "Please enter a number between 1 and 69.",
        "playlist_name": "📝 Great! What should I name the YouTube playlist?",
        "not_a_number": "That doesn't look like a number. Please try again.",
        "playlist_desc": (
            "✍️ Perfect. Any description for the playlist? "
            "(Optional, you can just say 'none')"
        ),
        "default_desc": "AI-generated playlist based on the vibe: {vibe}",
        "generating": "🧠 Generating song list with AI...",
        "ai_fail": "🔴 AI failed to generate a song list. Please try again.",
        "ai_list": "✅ AI Generated this list:\n\n{song_list}",
        "creating_playlist": "⚙️ Now creating the playlist on YouTube...",
        "create_fail": "🔴 Failed to create the YouTube playlist.",
        "playlist_created": "✅ Playlist created! Now adding {count} songs...",
        "added_song": "➕ Added song {num}/{total}: '{title}'",
        "playlist_ready": "🎉 All done! Your new playlist is ready:\n{url}",
        "client_secret_error": (
            "🔴 ERROR: {error}. Please ensure 'client_secret.json' is in the "
            "correct directory."
        ),
        "playlist_unexpected_error": (
            "An unexpected error occurred during playlist creation: {error}"
        ),
        "playlist_choice": "What would you like to do with these songs?",
        "upload_youtube": "Upload to YouTube",
        "download_mp3s": "Download MP3s",
        "downloading_playlist": "⬇️ Downloading {num}/{total}: '{title}'",
        "songs_sent": "✅ All songs have been sent.",
        "song_not_found": "❌ Could not find '{title}' on YouTube.",
        "download_song_fail": "❌ Failed to download '{title}'.",
    },
    "ru": {
        "language_prompt": "Выберите язык / Please choose your language",
        "english_button": "English",
        "russian_button": "Русский",
        "download_single_song": "Скачать песню",
        "create_ai_playlist": "Создать AI плейлист",
        "welcome": (
            "👋 Добро пожаловать в MusicWizard!\n\nЧто вы хотите сделать?"
        ),
        "menu_prompt": "Что вы хотите сделать?",
        "cancelled": "Операция отменена. Отправьте /start чтобы начать заново.",
        "send_link": (
            "🔗 Пришлите ссылку на YouTube или введите название песни, "
            "которую хотите скачать."
        ),
        "searching": "🔎 Поиск на YouTube: {query}",
        "auth_error": "🔴 Эта функция сейчас не работает, сообщите @ananas19911.",
        "not_found": "❌ Не удалось найти песню на YouTube. Попробуйте ещё раз!",
        "search_error": "❌ Произошла ошибка при поиске на YouTube. Попробуйте ещё раз.",
        "link_received": "🔗 Ссылка получена. Обработка...",
        "downloading": "⬇️ Загружаю...",
        "download_complete": "✅ Загрузка завершена! Отправляю в чат...",
        "get_lyrics": "📄 Текст песни",
        "main_menu": "⬅️ Главное меню",
        "ask_lyrics": "Песня отправлена! Хотите получить текст?",
        "error": "Произошла ошибка: {error}",
        "searching_lyrics": "📄 Поиск текста песни...",
        "request_expired": "Извините, запрос устарел.",
        "lyrics_header": "📜 Текст '{title}' — {artist}\n\n",
        "next_action": "Что вы хотите сделать дальше?",
        "playlist_intro": (
            "🎧 Давайте создадим плейлист! Какой настрой, тема или событие?\n\n"
        ),
        "playlist_how_many": (
            "🎶 Сколько песен должно быть в плейлисте? "
            "(например, 10, 25)"
        ),
        "number_range": "Введите число от 1 до 69.",
        "playlist_name": "📝 Отлично! Как назвать плейлист на YouTube?",
        "not_a_number": "Это не похоже на число. Попробуйте ещё раз.",
        "playlist_desc": (
            "✍️ Отлично. Есть ли описание для плейлиста? "
            "(Можно написать 'none')"
        ),
        "default_desc": "Плейлист сгенерирован ИИ на основе настроения: {vibe}",
        "generating": "🧠 Генерирую список песен с помощью ИИ...",
        "ai_fail": "🔴 ИИ не смог сгенерировать список песен. Попробуйте ещё раз.",
        "ai_list": "✅ ИИ сгенерировал список:\n\n{song_list}",
        "creating_playlist": "⚙️ Создаю плейлист на YouTube...",
        "create_fail": "🔴 Не удалось создать плейлист на YouTube.",
        "playlist_created": "✅ Плейлист создан! Добавляю {count} песен...",
        "added_song": "➕ Добавлена песня {num}/{total}: '{title}'",
        "playlist_ready": "🎉 Готово! Ваш новый плейлист:\n{url}",
        "client_secret_error": (
            "🔴 ОШИБКА: {error}. Убедитесь, что 'client_secret.json' "
            "в правильном каталоге."
        ),
        "playlist_unexpected_error": (
            "Произошла непредвиденная ошибка при создании плейлиста: {error}"
        ),
        "playlist_choice": "Что вы хотите сделать с этими песнями?",
        "upload_youtube": "Загрузить на YouTube",
        "download_mp3s": "Скачать MP3",
        "downloading_playlist": "⬇️ Загружаю {num}/{total}: '{title}'",
        "songs_sent": "✅ Все песни отправлены.",
        "song_not_found": "❌ Не удалось найти '{title}' на YouTube.",
        "download_song_fail": "❌ Не удалось скачать '{title}'.",
    },
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    lang_data = MESSAGES.get(lang, MESSAGES["en"])
    text = lang_data.get(key, MESSAGES["en"].get(key, key))
    return text.format(**kwargs)
