import os
import discord
import openai
import asyncio
import random
from dotenv import load_dotenv
from memory import Memory
from rate_limiter import RateLimiter
from utils import clean_message, search_web, get_gif, add_reaction

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')  # Default fallback for Docker
OWNER_ID = int(os.getenv('DISCORD_OWNER_ID'))
OWNER_USERNAME = os.getenv('DISCORD_OWNER_USERNAME')
BOT_PERSONA = os.getenv('BOT_PERSONA', '').replace('\\n', '\n')
CUSTOM_STATUS = os.getenv('CUSTOM_STATUS', f"watching over {OWNER_USERNAME}")
MEMORY_ENABLED = os.getenv('MEMORY_ENABLED', 'true').lower() == 'true'
ESCALATION_ENABLED = os.getenv('ESCALATION_ENABLED', 'false').lower() == 'true'
WEB_SEARCH_ENABLED = os.getenv('WEB_SEARCH_ENABLED', 'false').lower() == 'true'
GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

# OpenAI setup
openai.api_key = OPENAI_API_KEY
SELECTED_MODEL = "gpt-4o"

# Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize helpers
memory = Memory(REDIS_URL) if MEMORY_ENABLED else None
rate_limiter = RateLimiter()

# Cooldowns
gif_cooldown_counter = 0
reaction_cooldown_counter = 0

async def openai_chat(user_id, content, history, persona):
    try:
        response = openai.ChatCompletion.create(
            model=SELECTED_MODEL,
            messages=[{"role": "system", "content": persona}] +
                     [{"role": "user", "content": msg} for msg in history] +
                     [{"role": "user", "content": content}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return "…"

@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=CUSTOM_STATUS)
    )
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    global gif_cooldown_counter, reaction_cooldown_counter

    if message.author.bot or client.user not in message.mentions:
        return  # Only respond if tagged/mentioned

    user_id = str(message.author.id)
    username = message.author.name
    content = clean_message(message.content, client.user.name)

    # Owner recognition
    if message.author.id == OWNER_ID or message.author.name == OWNER_USERNAME:
        persona = BOT_PERSONA
        history = await memory.get(user_id) if MEMORY_ENABLED else []
    else:
        persona = BOT_PERSONA
        history = await memory.get("others") if MEMORY_ENABLED else []

    history = history + [f"{username}: {content}"]

    reply = await openai_chat(user_id, content, history, persona)

    if MEMORY_ENABLED:
        key = user_id if message.author.id == OWNER_ID else "others"
        await memory.save(key, "history", history + [f"Bot: {reply}"])

    # Web search fallback
    if WEB_SEARCH_ENABLED and "search" in content.lower():
        search_results = await search_web(content)
        reply += f"\n🔎 {search_results}"

    await message.reply(reply)

    if reaction_cooldown_counter == 0:
        await add_reaction(message)
        reaction_cooldown_counter = random.randint(3, 5)
    else:
        reaction_cooldown_counter -= 1

    if GIPHY_API_KEY and gif_cooldown_counter == 0:
        gif_url = await get_gif(reply, GIPHY_API_KEY)
        if gif_url:
            await message.channel.send(gif_url)
        gif_cooldown_counter = random.randint(3, 5)
    else:
        gif_cooldown_counter -= 1

client.run(TOKEN)
