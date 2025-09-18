import os
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
"""Utility to generate YouTube OAuth token (token.pickle).

Run this in the project root where client_secret.json resides. The generated
token.pickle will be saved in the same directory (project root) as expected by
the application.
"""

# --- Configuration ---
# These values are based on your project's config.py
CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_FILE = "token.pickle"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_token():
    """
    Runs the OAuth2 flow to generate a token.pickle file.
    """
    credentials = None

    # Check if the client secret file exists
    if not os.path.exists(CLIENT_SECRET_FILE):
        logger.error(
            f"Error: The client secret file '{CLIENT_SECRET_FILE}' was not found."
        )
        logger.info(
            "Please download your 'client_secret.json' from the Google Cloud Console "
            "and place it in the same directory as this script."
        )
        return

    logger.info(
        f"Starting authentication flow using '{CLIENT_SECRET_FILE}'..."
    )

    # Run the OAuth2 flow to get credentials
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        # The user's browser will open for them to grant permissions.
        credentials = flow.run_local_server(port=0)
        logger.info("Authentication successful.")
    except Exception as e:
        logger.error(f"An error occurred during the authentication flow: {e}")
        return

    # Save the credentials for later use
    try:
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)
        logger.info(f"Credentials saved to '{TOKEN_FILE}'.")
        logger.info(
            "\n--- IMPORTANT ---\n"
            f"'{TOKEN_FILE}' saved in project root. Keep it alongside "
            "'client_secret.json' so the app can authenticate without "
            "re-authorizing."
        )
    except Exception as e:
        logger.error(f"Failed to save the token file: {e}")


if __name__ == "__main__":
    generate_token()
