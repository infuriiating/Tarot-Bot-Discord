import discord
from discord.ext import commands
from config import DISCORD_TOKEN

intents = discord.Intents.default()
# We don't need any special intents just to sync commands.
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Clearing global commands...')
    bot.tree.clear_commands(guild=None) # Clear global commands
    await bot.tree.sync()
    print('Global commands cleared!')
    await bot.close()

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
