import discord
import os
from discord.ext import commands
from discord import app_commands
from utils import draw_random_card, get_card_image_path, get_discord_file
from config import SUIT_COLORS

class YesOrNo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='yes_or_no', description='Ask a yes or no question and draw a Tarot card for guidance.')
    @app_commands.describe(question='The question you want to ask the Tarot')
    async def yes_or_no(self, interaction: discord.Interaction, question: str):
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

async def setup(bot):
    await bot.add_cog(YesOrNo(bot))
