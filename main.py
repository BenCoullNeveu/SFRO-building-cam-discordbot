from playwright.async_api import async_playwright
import time
import discord
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1308820057635295303

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_ids = []

async def fetch_images():
    """Fetch images from the web page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://status.starfront.space/")
        
        await page.reload()
        
        await page.wait_for_selector("img")

        image_urls = await page.evaluate("""
            Array.from(document.querySelectorAll('img'), img => img.src)
        """)

        timestamp = int(time.time())
        building_images = [
            f"{url}?cache_bust={timestamp}" if "building-0005" in url else None
            for url in image_urls
        ]
        
        building_5_image = [url for url in building_images if url is not None]
        print(building_5_image)

        await browser.close()
        return building_5_image

@tasks.loop(seconds=60)
async def check_and_post_images():
    """Fetch images and manage Discord channel messages."""
    global message_ids
    images = await fetch_images()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return

    for img_url in images:
        message = await channel.send(img_url)
        message_ids.append(message.id)

    while len(message_ids) > 10:
        oldest_message_id = message_ids.pop(0)
        try:
            old_message = await channel.fetch_message(oldest_message_id)
            await old_message.delete()
        except discord.NotFound:
            print(f"Message with ID {oldest_message_id} not found. Skipping deletion.")

@client.event
async def on_ready():
    """Start the task loop when the bot is ready."""
    print(f"{client.user} has connected to Discord!")
    check_and_post_images.start()

client.run(TOKEN)
