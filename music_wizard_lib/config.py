import os
import logging
from dotenv import load_dotenv

# --- Environment Variable Loading ---
# Load environment variables from a .env file
load_dotenv()

# It's highly recommended to use environment variables for your tokens.
# Run the following in your terminal before starting the bot:
# export TELEGRAM_TOKEN="YOUR_TELEGRAM_TOKEN"
# export GENIUS_ACCESS_TOKEN="YOUR_GENIUS_TOKEN"
# export OPENAI_API_KEY="YOUR_OPENAI_KEY"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GENIUS_ACCESS_TOKEN = os.environ.get("GENIUS_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# --- Validate Configuration ---
if not all([TELEGRAM_TOKEN, GENIUS_ACCESS_TOKEN, OPENAI_API_KEY]):
    raise ValueError(
        "One or more required environment variables "
        "(TELEGRAM_TOKEN, GENIUS_ACCESS_TOKEN, OPENAI_API_KEY) are not set."
    )

# --- OpenAI Models ---
OPENAI_CHAT_MODEL = "gpt-4o-mini"
OPENAI_PLAYLIST_MODEL = "gpt-4o"

# --- YouTube API Configuration ---
CLIENT_SECRET_FILE = "client_secret.json"
API_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_FILE = "token.pickle"

# --- Bot Settings ---
MAX_FILE_SIZE_MB = 49
TELEGRAM_MESSAGE_LIMIT = 4096
# --- Audio Quality ---
# Options: "perfect", "high", "medium", "low"
AUDIO_QUALITY = "perfect"

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
