import discord
import json
import random
import os
import io
import typing
from PIL import Image
from datetime import datetime, timezone
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN, COMMAND_PREFIX, CARDS_JSON_PATH, IMAGES_DIR, DATA_DIR, SUIT_COLORS

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

# --- BOT SETUP ---
intents = discord.Intents.default()
# We may not even need message_content if we only use Slash commands,
# but keeping it just in case of any hybrid prefix usage.
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print('------')

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
    
    image_path = get_card_image_path(card)
    filename = os.path.basename(image_path)
    embed1.set_image(url=f"attachment://{filename}")
    
    embed2 = discord.Embed(color=embed_color)
        
    meaning = card['reversed_meaning'] if is_reversed else card['upright_meaning']
    embed2.add_field(name="Meaning", value=meaning, inline=False)
    
    return [embed1, embed2], image_path, filename

# --- SLASH COMMANDS ---

async def card_name_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> typing.List[app_commands.Choice[str]]:
    choices = []
    current_lower = current.lower()
    for card in tarot_cards:
        card_name = card['name']
        card_num = str(card['number'])
        if current_lower in card_name.lower() or current_lower == card_num:
            choices.append(app_commands.Choice(name=card_name, value=card_name))
        if len(choices) >= 25:
            break
    return choices

@bot.tree.command(name='card_info', description='Look up the details of a specific Tarot card.')
@app_commands.autocomplete(card_name=card_name_autocomplete)
@app_commands.describe(card_name='Start typing the name or number of the card')
async def card_info(interaction: discord.Interaction, card_name: str):
    card = next((c for c in tarot_cards if c['name'].lower() == card_name.lower()), None)
    if not card:
        await interaction.response.send_message(f"Could not find a card named '{card_name}'.", ephemeral=True)
        return
        
    embed_color = SUIT_COLORS.get(card['suit'], 0x4a0072)
    
    embed1 = discord.Embed(
        title=f"📖 {card['name']}",
        description=f"**Suit:** {card['suit']} | **Number:** {card['number']} | **Element:** {card.get('element', 'N/A')}",
        color=embed_color
    )
    
    if 'zodiac_sign' in card:
        embed1.add_field(name="Astrology", value=card['zodiac_sign'], inline=False)
    
    image_path = get_card_image_path(card)
    filename = os.path.basename(image_path)
    embed1.set_image(url=f"attachment://{filename}")
    
    embed2 = discord.Embed(color=embed_color)
    
    if 'symbols' in card and card['symbols']:
        embed2.add_field(name="Symbols", value=", ".join(card['symbols']), inline=False)
        
    if 'meanings' in card and card['meanings']:
        embed2.add_field(name="Keywords", value=", ".join(card['meanings']), inline=False)
        
    embed2.add_field(name="Upright Meaning", value=card.get('upright_meaning', 'N/A')[:1024], inline=False)
    embed2.add_field(name="Reversed Meaning", value=card.get('reversed_meaning', 'N/A')[:1024], inline=False)
    
    if 'yes_no' in card:
        embed2.add_field(name="Yes/No", value=card['yes_no'], inline=False)
        
    if os.path.exists(image_path):
        file = discord.File(image_path, filename=filename)
        await interaction.response.send_message(file=file, embeds=[embed1, embed2])
    else:
        await interaction.response.send_message(f"Error: Could not find image for {card['name']}.")

@bot.tree.command(name='draw', description='Draws a random Tarot card with a 30% chance to be reversed.')
async def draw_card(interaction: discord.Interaction):
    card, is_reversed = draw_random_card()
    embeds, image_path, filename = create_card_embeds(card, is_reversed)
    
    if not os.path.exists(image_path):
        await interaction.response.send_message(f"Error: Could not find image for {card['name']}.")
        return

    file = get_discord_file(image_path, is_reversed, filename)
    await interaction.response.send_message(file=file, embeds=embeds)

@bot.tree.command(name='yes_or_no', description='Ask a yes or no question and draw a Tarot card for guidance.')
@app_commands.describe(question='The question you want to ask the Tarot')
async def yes_or_no(interaction: discord.Interaction, question: str):
    card, is_reversed = draw_random_card()
    state = "Reversed" if is_reversed else "Upright"
    
    element = card.get('element', 'N/A')
    description_text = f"**Card Drawn:** {card['name']} ({state})\n**Suit:** {card['suit']} | **Number:** {card['number']} | **Element:** {element}"
    
    embed_color = SUIT_COLORS.get(card['suit'], 0x4a0072)
    
    embed1 = discord.Embed(
        title=f"Question: {question}",
        description=description_text,
        color=embed_color
    )
    
    image_path = get_card_image_path(card)
    filename = os.path.basename(image_path)
    embed1.set_image(url=f"attachment://{filename}")
    
    embed2 = discord.Embed(color=embed_color)
    if 'yes_no' in card:
        embed2.add_field(name="Yes/No", value=card['yes_no'], inline=False)
    
    if os.path.exists(image_path):
        file = get_discord_file(image_path, is_reversed, filename)
        await interaction.response.send_message(file=file, embeds=[embed1, embed2])
    else:
        await interaction.response.send_message(f"Error: Could not find image for {card['name']}.")

@bot.tree.command(name='daily', description='Draw your daily Tarot card (Resets at midnight UTC).')
async def daily_draw(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    daily_data = load_daily_data()
    
    # Use UTC date to determine "today"
    current_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if user_id in daily_data and daily_data[user_id] == current_date_str:
        await interaction.response.send_message("You have already drawn your daily card for today! Come back tomorrow.", ephemeral=True)
        return
        
    card, is_reversed = draw_random_card()
    embeds, image_path, filename = create_card_embeds(card, is_reversed, title_prefix="🌟 Daily Card: ")
    
    if not os.path.exists(image_path):
        await interaction.response.send_message(f"Error: Could not find image for {card['name']}.")
        return

    # Save the successful draw logic
    daily_data[user_id] = current_date_str
    save_daily_data(daily_data)

    file = get_discord_file(image_path, is_reversed, filename)
    await interaction.response.send_message(file=file, embeds=embeds)

if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables. Please check your .env file.")
