import discord
import os
import typing
from discord.ext import commands
from discord import app_commands
from utils import tarot_cards, get_card_image_path
from config import SUIT_COLORS

class CardInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def card_name_autocomplete(
        self,
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

    @app_commands.command(name='card_info', description='Look up the details of a specific Tarot card.')
    @app_commands.describe(card_name='Start typing the name or number of the card')
    @app_commands.autocomplete(card_name=card_name_autocomplete)
    async def card_info(self, interaction: discord.Interaction, card_name: str):
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

async def setup(bot):
    await bot.add_cog(CardInfo(bot))
