from uuid import uuid4
import sys
import os
import discord
from discord.ext import tasks
import wavelink
import simplejson as json
import requests

intents = discord.Intents.default()
# Place any intents you wish for this bot to have here.
# https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.value

bot = discord.Bot(intents=intents)

print(
    "\n{Rice Bot}\nVersion 1.0.0\nWritten by morg.mov\nhttps://github.com/Morg-S9 \n"
)

if not os.path.isfile("./config.json"):
    print("No config.json found.\n")
    while True:
        token = input("Enter your Discord Bot Token: ")
        if token:
            break
        print("No bot token provided.\n")
    llhost = input("\nEnter your Lavalink Server's Host [default: localhost]: ")
    if not llhost:
        llhost = "localhost"
    llport = input("\nEnter your Lavalink Server Port [default: 2333]: ")
    if not llport:
        llport = 2333
    while True:
        llpass = input("\nEnter your Lavalink Server Password: ")
        if llpass:
            break
        print("No password provided.\n")

    print("Creating config.json...")
    config = {
        "token": token,
        "cobalt": {"api": "https://co.wuk.sh/api/json"},
        "lavalink": {"host": llhost, "port": llport, "password": llpass},
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
cobaltapi = config["cobalt"]["api"]

if not cobaltapi.startswith("https://") and not cobaltapi.startswith("http://"):
    print(
        "[ERROR] Invalid API Value detected in config.json. Must start with http[s]://"
    )
    sys.exit(1)

try:
    requests.get(cobaltapi, timeout=15)
except requests.ConnectionError:
    print(
        "An error occurred when attempting a connection test.\nCheck your connection, and your Cobalt API value in your config.json, and try again."
    )
    input("\nPress [Enter] to exit...")
    sys.exit(1)


async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready()  # wait until the bot is ready

    await wavelink.NodePool.create_node(
        bot=bot,
        host=config["lavalink"]["host"],
        port=config["lavalink"]["port"],
        password=config["lavalink"]["password"],
    )  # create a node


@bot.event
async def on_ready():
    print(f"[Pycord] Connected as {bot.user}!")


@tasks.loop(minutes=5)
async def clear_temp():
    if os.listdir("./tmp/") == []:
        return

    for i in os.listdir("./tmp/"):
        os.remove(f"./tmp/{i}")


@bot.command(description="Download video from provided URL")
async def video(
    ctx,
    url: discord.Option(str),
    mention: discord.Option(discord.SlashCommandOptionType.user, required=False),
):
    if not url.startswith("https://") and not url.startswith("http://"):
        await ctx.respond(
            'Invalid URL. URL\'s must start with "http[s]://"', ephemeral=True
        )
        return
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    data = {"url": url, "isNoTTWatermark": True}
    request = requests.post(
        cobaltapi, headers=headers, json=data, timeout=15
    )
    response = request.json()
    if response["status"] == "error":
        errtext = response["text"].replace("<br/>", "\n")
        await ctx.respond(errtext, ephemeral=True)
        return

    await ctx.defer(ephemeral=True)

    filename = f"./tmp/{uuid4()}.mp4"
    
    with open(filename, "wb") as f:
        f.write(requests.get(response["url"], timeout=15).content)

    file = discord.File(filename)

    if mention is None:
        await ctx.send(f"Sent by {ctx.user.mention}", file=file)
    else:
        await ctx.send(f"{mention.mention}\n\nSent by {ctx.user.mention}", file=file)

    await ctx.respond("Done.")


bot.run(config["token"])
