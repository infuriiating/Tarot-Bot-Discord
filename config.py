import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "!"

# Data Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "./data")
CARDS_JSON_PATH = os.path.join(DATA_DIR, "./cards.json")
IMAGES_DIR = os.path.join(BASE_DIR, "./src")

# Embed Colors based on Suit
SUIT_COLORS = {
    "Major Arcana": 0x4a0072,  # Deep Purple
    "Wands": 0xc0392b,         # Fiery Red
    "Cups": 0x2980b9,          # Watery Blue
    "Swords": 0xf39c12,        # Golden Yellow / Air
    "Pentacles": 0x27ae60      # Earthy Green
}
