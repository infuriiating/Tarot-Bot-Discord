import discord
import os
from discord.ext import commands
from discord import app_commands
from utils import draw_random_card, get_discord_file, create_card_embeds

class Draw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='draw', description='Draws a random Tarot card with a 30% chance to be reversed.')
    async def draw_card(self, interaction: discord.Interaction):
        card, is_reversed = draw_random_card()
        embeds, image_path, filename = create_card_embeds(card, is_reversed)
        
        if not os.path.exists(image_path):
            await interaction.response.send_message(f"Error: Could not find image for {card['name']}.")
            return

        file = get_discord_file(image_path, is_reversed, filename)
        await interaction.response.send_message(file=file, embeds=embeds)

async def setup(bot):
    await bot.add_cog(Draw(bot))
