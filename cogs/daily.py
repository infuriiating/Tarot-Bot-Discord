import discord
import os
from datetime import datetime, timezone
from discord.ext import commands
from discord import app_commands
from utils import draw_random_card, get_discord_file, create_card_embeds, load_daily_data, save_daily_data

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='daily', description='Draw your daily Tarot card (Resets at midnight UTC).')
    async def daily_draw(self, interaction: discord.Interaction):
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

        # Save the successful draw
        daily_data[user_id] = current_date_str
        save_daily_data(daily_data)

        file = get_discord_file(image_path, is_reversed, filename)
        await interaction.response.send_message(file=file, embeds=embeds)

async def setup(bot):
    await bot.add_cog(Daily(bot))
