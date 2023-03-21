import os
from dotenv import load_dotenv

load_dotenv()

BROWSER_DRIVER_PATH = os.environ.get("BROWSER_DRIVER_PATH")
GAME_URL = os.environ.get("GAME_URL")
