import json
import random
import os
import io
import discord
from PIL import Image
from config import CARDS_JSON_PATH, IMAGES_DIR, DATA_DIR, SUIT_COLORS

# --- DATA LOADING & STORAGE ---
def load_cards():
    with open(CARDS_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

tarot_cards = load_cards()

DAILY_FILE = os.path.join(DATA_DIR, "daily_draws.json")

def load_daily_data():
    if not os.path.exists(DAILY_FILE):
        return {}
    with open(DAILY_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_daily_data(data):
    with open(DAILY_FILE, 'w') as f:
        json.dump(data, f)

# --- HELPER FUNCTIONS ---
def get_card_image_path(card):
    if card['suit'] == 'Major Arcana':
        name_part = card['name'].replace(' ', '')
        filename = f"{card['number']:02d}-{name_part}.jpg"
    else:
        filename = f"{card['suit']}{card['number']:02d}.jpg"
    return os.path.join(IMAGES_DIR, filename)

def draw_random_card():
    card = random.choice(tarot_cards)
    is_reversed = random.random() < 0.30  # 30% chance
    return card, is_reversed

def get_discord_file(image_path, is_reversed, filename):
    if not is_reversed:
        return discord.File(image_path, filename=filename)
        
    # If reversed, we load it, rotate it 180 degrees, and save to a BytesIO buffer
    with Image.open(image_path) as img:
        rotated_img = img.rotate(180, expand=True)
        buffer = io.BytesIO()
        # Save as JPEG as original files are .jpg
        rotated_img.save(buffer, format="JPEG")
        buffer.seek(0)
        return discord.File(fp=buffer, filename=filename)

def create_card_embeds(card, is_reversed, title_prefix=""):
    state = "Reversed" if is_reversed else "Upright"
    embed_title = f"{title_prefix}{card['name']} ({state})"
    
    element = card.get('element', 'N/A')
    description_text = f"**Suit:** {card['suit']} | **Number:** {card['number']} | **Element:** {element}"
    
    embed_color = SUIT_COLORS.get(card['suit'], 0x4a0072)
    
    embed1 = discord.Embed(
        title=embed_title,
        description=description_text,
        color=embed_color
    )
    
    if 'zodiac_sign' in card:
        embed1.add_field(name="Astrology", value=card['zodiac_sign'], inline=False)
    
    if 'meanings' in card and card['meanings']:
        embed1.add_field(name="Keywords", value=", ".join(card['meanings']), inline=False)
    
    image_path = get_card_image_path(card)
    filename = os.path.basename(image_path)
    embed1.set_image(url=f"attachment://{filename}")
    
    embed2 = discord.Embed(color=embed_color)
        
    meaning = card['reversed_meaning'] if is_reversed else card['upright_meaning']
    embed2.add_field(name="Meaning", value=meaning, inline=False)
    
    return [embed1, embed2], image_path, filename
