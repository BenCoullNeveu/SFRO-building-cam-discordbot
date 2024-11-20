import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1308820057635295303

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Track the last posted image URL to avoid duplicates
last_posted_image = None

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    fetch_and_post_image.start()

@tasks.loop(minutes=1)
async def fetch_and_post_image():
    global last_posted_image
    url = 'https://status.starfront.space/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the 'Building 5' image
    building_5_section = soup.find('div', alt="Starfront Building 5")
    if building_5_section:
        img_tag = building_5_section.find('img')
        if img_tag:
            img_url = img_tag['src']
            if img_url != last_posted_image:
                last_posted_image = img_url
                channel = client.get_channel(CHANNEL_ID)
                message = await channel.send(img_url)
                # Schedule deletion after 1 hour
                await message.delete(delay=3600)

client.run(TOKEN)
