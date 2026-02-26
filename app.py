import discord
import os
from discord.ext import commands
from config import DISCORD_TOKEN, COMMAND_PREFIX

# --- BOT SETUP ---
class TarotBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)

    async def setup_hook(self):
        # Load extensions/commands from the cmd folder
        for filename in os.listdir('./cmd'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'cmd.{filename[:-3]}')
                print(f"Loaded extension: {filename}")

bot = TarotBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print('------')

if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables. Please check your .env file.")
