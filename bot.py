import os  
import discord
from discord.ext import commands

# --- CONFIG ---
TOKEN = "YOUR_BOT_TOKEN_HERE"  # replace with your bot token
CHANNEL_NAME = "86"      # channel where the bot will post

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to track stock items
stock = {}

# Helper: format the status board
def format_board():
    if not stock:
        return "✅ Everything is in stock!"
    msg = "📦 **Current Stock Status**\n"
    for item, status in stock.items():
        if status == "out":
            msg += f"❌ {item} — 86’d\n"
        elif status == "low":
            msg += f"⚠️ {item} — Running Low\n"
        else:
            msg += f"✅ {item} — In Stock\n"
    return msg

async def update_board():
    # Find the channel
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if channel:
            # Clear old messages from bot
            async for message in channel.history(limit=50):
                if message.author == bot.user:
                    await message.delete()
            # Post updated board
            await channel.send(format_board())

# --- COMMANDS ---
@bot.command()
async def add(ctx, *, item):
    """Mark item as 86’d"""
    stock[item] = "out"
    await update_board()
    await ctx.send(f"❌ {item} marked as 86’d.", delete_after=5)

@bot.command()
async def low(ctx, *, item):
    """Mark item as running low"""
    stock[item] = "low"
    await update_board()
    await ctx.send(f"⚠️ {item} marked as running low.", delete_after=5)

@bot.command()
async def remove(ctx, *, item):
    """Mark item back in stock"""
    if item in stock:
        del stock[item]
    await update_board()
    await ctx.send(f"✅ {item} is back in stock.", delete_after=5)

# Start bot
@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    await update_board()

TOKEN = os.environ["DISCORD_TOKEN"]
bot.run(TOKEN)

