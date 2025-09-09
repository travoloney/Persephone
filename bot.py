import os
import discord
from discord.ext import commands
from pymongo import MongoClient

TOKEN = os.environ["DISCORD_TOKEN"]
MONGO_URI = os.environ["MONGO_URI"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["restaurant_bot"]           # database name
stock_collection = db["stock_items"]    # collection name

# Helper to format board
def format_board():
    items = list(stock_collection.find({}))
    if not items:
        return "✅ Everything is in stock!"
    msg = "📦 **Current Stock Status**\n"
    for item in items:
        status = item["status"]
        name = item["name"]
        if status == "out":
            msg += f"❌ {name} — 86’d\n"
        elif status == "low":
            msg += f"⚠️ {name} — Running Low\n"
        else:
            msg += f"✅ {name} — In Stock\n"
    return msg

# Update board in Discord
async def update_board():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="86")
        if channel:
            async for message in channel.history(limit=50):
                if message.author == bot.user:
                    await message.delete()
            await channel.send(format_board())

# Commands
@bot.command()
async def add(ctx, *, item):
    stock_collection.update_one({"name": item}, {"$set": {"status": "out"}}, upsert=True)
    await update_board()
    await ctx.send(f"❌ {item} marked as 86’d.", delete_after=5)

@bot.command()
async def low(ctx, *, item):
    stock_collection.update_one({"name": item}, {"$set": {"status": "low"}}, upsert=True)
    await update_board()
    await ctx.send(f"⚠️ {item} marked as running low.", delete_after=5)

@bot.command()
async def remove(ctx, *, item):
    stock_collection.delete_one({"name": item})
    await update_board()
    await ctx.send(f"✅ {item} is back in stock.", delete_after=5)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    await update_board()

bot.run(TOKEN)
