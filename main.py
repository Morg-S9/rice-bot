import discord
import asyncio
import simplejson as json
import requests
from uuid import uuid4
import sys
import os

intents = discord.Intents.default()
# Place any intents you wish for this bot to have here.
# https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.value

bot = discord.Bot(intents=intents)

print(
    "\n{Cobalt Bot}\nVersion 1.0.0\nWritten by morg.mov\nhttps://github.com/Morg-S9 \n"
)

if not os.path.isfile("./config.json"):
    print("No config.json found.\n")
    while True:
        token = input("Enter your Discord Bot Token: ")
        if token:
            break
        print("No bot token provided.\n")
        
    print("Creating config.json...")
    config = {
        "token": token,
        "api": "https://co.wuk.sh/api/json"
    }
    try:
        with open("./config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print("Done.\n")
    except OSError as e:
        print(f"\nAn error occurred creating the file.\n{e}\n")
        input("Press [Enter] to exit...")
        sys.exit(1)

if not os.path.isdir("./tmp"):
    os.makedirs("./tmp")

config = json.load(open("./config.json", "r", encoding="utf-8"))

if not config["api"].startswith("https://") and not config["api"].startswith("http://"):
    print("[ERROR] Invalid API Value detected in config.json. Must start with http[s]://")
    sys.exit(1)

@bot.event
async def on_ready():
    print(f"[Pycord] Connected as {bot.user}!")

@bot.command(description="Download video from provided URL")
async def video(ctx,
                url: discord.Option(str)):
    if not url.startswith("https://") and not url.startswith("http://"):
        await ctx.respond("Invalid URL. URL's must start with \"http[s]://\"", ephemeral=True)
        return
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "url": url,
        "isNoTTWatermark": True
    }
    request = requests.post(config["api"], headers=headers, json=data, timeout=15)
    response = request.json()
    if response["status"] == "error":
        errtext = response["text"].replace("<br/>", "\n")
        await ctx.respond(errtext)
        return
    
    await ctx.defer()

    filename = f'./tmp/{uuid4()}.mp4'
    f = open(filename, 'wb')
    f.write(requests.get(response["url"], timeout=15).content)
    f.close()
    f = None
    
    file = discord.File(filename)
    await ctx.respond(file=file)
    
    return

bot.run(config["token"])