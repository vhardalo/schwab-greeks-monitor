import os
from dotenv import load_dotenv

# Load the variables from the hidden .env file
load_dotenv()

# Make sure these are ALL CAPS and have no spaces around the equals sign
APP_KEY = os.getenv("SCHWAB_APP_KEY")
APP_SECRET = os.getenv("SCHWAB_APP_SECRET")
REDIRECT_URI = os.getenv("SCHWAB_REDIRECT_URI", "https://127.0.0.1")

# Base URLs for the Schwab API
AUTH_BASE_URL = "https://api.schwabapi.com/v1/oauth/authorize"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
MARKET_DATA_BASE_URL = "https://api.schwabapi.com/marketdata/v1"