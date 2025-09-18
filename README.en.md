MusicWizard Telegram Bot

MusicWizard is a powerful, multi-functional Telegram bot designed to be your ultimate music companion. It seamlessly integrates with YouTube, OpenAI, and Genius to offer a rich set of features, from downloading individual songs to curating entire AI-generated playlists on your YouTube account.
✨ Features

    🎵 Single Song Downloader: Send a YouTube link to the bot, and it will:

        Download the audio in high-quality MP3 format.

        Use AI (GPT-4o-mini) to accurately parse the Artist and Title from the video's name.

        Send the MP3 file directly to you in the chat, complete with correct metadata.

    📄 Lyrics On-Demand: After downloading a song, get the full lyrics with a single button press, fetched directly from Genius.

    🤖 AI Playlist Creator: Don't know what to listen to?

        Describe a vibe, theme, or occasion (e.g., "upbeat 80s synthwave for driving" or "chill lofi for studying").

        The bot uses AI (GPT-3.5-Turbo) to generate a custom list of songs that match your request.

        It then automatically creates a new, unlisted playlist on your YouTube account and adds all the generated songs to it.

    🔒 Secure Authentication: Uses a secure OAuth2 flow to connect to your YouTube account, ensuring your credentials are safe. Tokens are stored locally for seamless future use.

    💬 Conversational Interface: A simple, menu-driven conversation flow makes it easy to navigate between features.

🛠️ Setup and Installation

Follow these steps to get your own instance of the MusicWizard Bot running.
1. Prerequisites

    Python 3.9 or higher

    A Telegram account and a bot token.

    An OpenAI API key.

    A Genius API access token.

    Google Cloud project with the YouTube Data API v3 enabled.

2. Clone the Repository

git clone <your-repository-url>
cd <your-repository-directory>

3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate

4. Install Dependencies

Install the required packages using the provided requirements file:

pip install -r requirements.txt

5. Configure API Credentials

The bot relies on environment variables and a Google client secret file for its API keys.

A. Environment Variables:

Set the following environment variables in your system. You can also copy the
provided example file: `cp .env.example .env` and fill in your values.

    For macOS/Linux:

    export TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    export GENIUS_ACCESS_TOKEN="YOUR_GENIUS_ACCESS_TOKEN"

    For Windows (Command Prompt):

    set TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    set OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    set GENIUS_ACCESS_TOKEN="YOUR_GENIUS_ACCESS_TOKEN"

B. Google API Credentials:

    Go to the Google Cloud Console.

    Create a new project or select an existing one.

    Enable the YouTube Data API v3.

    Go to "Credentials", click "Create Credentials", and choose "OAuth client ID".

    Select "Desktop app" as the application type.

    Click "Create" and then "Download JSON".

    Rename the downloaded file to client_secret.json and place it in the root directory of the project.

🚀 Running the Bot

Once all the setup and configuration steps are complete, you can start the bot.

    First-Time YouTube Authentication:
    The first time you try to create a playlist, the script will open a link in your web browser to ask for your permission to manage your YouTube playlists. After you approve, a token.pickle file will be created in the project directory. You will only need to do this once.

    Start the Bot:

    python bot.py

    Interact with the Bot on Telegram:

        Open Telegram and find the bot you created.

        Send the /start command to begin.

        Follow the on-screen buttons to download a song or create a playlist.

📂 Project Structure

The project is organized into three main files for clarity and maintainability:

    config.py: Stores all configuration variables, API keys, and global settings.

    music_wizard_lib: The core logic library. It contains all the functions for interacting with external APIs (YouTube, OpenAI, Genius) and is completely independent of the bot interface.

    bot.py: The main executable for the Telegram bot. It handles all user interactions, conversation flows, and calls functions from the music_wizard_lib.
## Testing

Run the unit tests with:

    pytest

 

📄 License

This project is licensed under the MIT License. See the LICENSE file for details.
