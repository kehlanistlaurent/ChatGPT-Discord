import os
import discord
import openai
import asyncio
import random
import time
import requests
from dotenv import load_dotenv
from memory import Memory
from rate_limiter import rate_limit
from utils import clean_message

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')
REDIS_URL = os.getenv('REDIS_URL')
OWNER_ID = int(os.getenv('OWNER_ID'))
OWNER_USERNAME = os.getenv('OWNER_USERNAME')
BOT_NAME = os.getenv('BOT_NAME', 'ChatGPT')
BOT_PERSONA = os.getenv('BOT_PERSONA', f"You are {BOT_NAME}, a conversational AI.")
OWNER_TONE = os.getenv('OWNER_TONE', 'natural')
OTHERS_TONE = os.getenv('OTHERS_TONE', 'neutral')
CUSTOM_STATUS = os.getenv('CUSTOM_STATUS', f"{BOT_NAME} active")
ENABLE_REACTIONS = os.getenv('ENABLE_REACTIONS', 'true').lower() == 'true'
ENABLE_GIPHY = os.getenv('ENABLE_GIPHY', 'true').lower() == 'true'
GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
LOG_FULL_QA = os.getenv('LOG_FULL_QA', 'false').lower() == 'true'
MEMORY_ENABLED = os.getenv('MEMORY_ENABLED', 'true').lower() == 'true'
ESCALATION_ENABLED = os.getenv('ESCALATION_ENABLED', 'false').lower() == 'true'
DUCKDUCKGO_API_URL = "https://api.duckduckgo.com/"

SPAM_THRESHOLD = 5
GIF_CHANCE = 0.25  # 25% chance for GIF
GIF_COOLDOWN = random.randint(3, 5)
REACT_COOLDOWN = random.randint(3, 5)
gif_cooldown_counter = 0
react_cooldown_counter = 0

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Memory initialization
if MEMORY_ENABLED:
    try:
        memory = Memory(REDIS_URL)
        if not memory.redis:
            raise Exception("Redis connection failed")
    except Exception as e:
        print(f"⚠️ Memory disabled due to Redis error: {e}")
        MEMORY_ENABLED = False
else:
    memory = None
    print("ℹ️ Memory is disabled (MEMORY_ENABLED=false)")

SELECTED_MODEL = "gpt-3.5-turbo"

async def detect_best_model():
    global SELECTED_MODEL
    try:
        models = await openai.models.list()
        available_models = [m.id for m in models.data]
        if "gpt-4o" in available_models:
            SELECTED_MODEL = "gpt-4o"
        elif "gpt-4" in available_models:
            SELECTED_MODEL = "gpt-4"
        safe_log(f"💎 Selected model: {SELECTED_MODEL}")
    except Exception as e:
        safe_log(f"⚠️ Model detection failed: {e}", "error")

async def openai_chat(user_id, username, message, user_history, user_profile, escalation_level):
    rate_limit()
    if user_id == OWNER_ID or username == OWNER_USERNAME:
        system_prompt = f"{BOT_PERSONA} Speak to the owner ({username}) using this tone: {OWNER_TONE}. Full owner recognition and confident tone."
    else:
        escalation_note = ""
        if ESCALATION_ENABLED:
            if escalation_level == 1:
                escalation_note = " Your tone is cool and detached."
            elif escalation_level == 2:
                escalation_note = " Your tone is cold and intimidating."
            elif escalation_level >= 3:
                escalation_note = " Your tone is sharp and ruthless."
        subtle_friend_note = " Subtle recognition of known friend." if user_profile.get("friend", False) else ""
        system_prompt = f"{BOT_PERSONA} Speak to other users using this tone: {OTHERS_TONE}.{escalation_note}{subtle_friend_note}"

    msgs = [{"role": "system", "content": system_prompt}] + user_history + [{"role": "user", "content": message}]
    try:
        response = openai.chat.completions.create(
            model=SELECTED_MODEL,
            messages=msgs,
            temperature=0.85
        )
        return response.choices[0].message.content
    except openai.error.InvalidRequestError:
        return "I couldn't process that."

async def ensure_user_history(user_id, username):
    if not MEMORY_ENABLED:
        return [], {}
    hist = await memory.get(str(user_id))
    if not hist:
        hist = {}
    hist["username"] = username
    history = hist.get("history", [])
    profile = hist.get("profile", {})
    await memory.save(str(user_id), "username", username)
    return history, profile

@client.event
async def on_ready():
    safe_log(f"{BOT_NAME} is live.")
    await detect_best_model()
    await client.change_presence(
        activity=discord.Game(name=CUSTOM_STATUS)
    )

@client.event
async def on_message(message):
    global gif_cooldown_counter, react_cooldown_counter

    if message.author.bot:
        return
    if client.user not in message.mentions:
        return  # Respond only if tagged

    user_id = message.author.id
    username = str(message.author.display_name)
    content = clean_message(message.content, str(client.user.id))
    user_history, user_profile = await ensure_user_history(user_id, username) if MEMORY_ENABLED else ([], {})
    profile = user_profile.copy() if user_profile else {}
    escalation_level = profile.get("escalation_level", 0)

    if ESCALATION_ENABLED:
        msg_times = profile.get("msg_times", [])
        current_time = int(time.time())
        msg_times = [t for t in msg_times if current_time - t < 30] + [current_time]
        profile["msg_times"] = msg_times
        if len(msg_times) >= SPAM_THRESHOLD and escalation_level < 3:
            escalation_level += 1
            profile["escalation_level"] = escalation_level
            safe_log(f"🚨 Escalation triggered for {username} (Spam)")

    response = await openai_chat(user_id, username, content, user_history, user_profile, escalation_level)

    if MEMORY_ENABLED:
        new_history = user_history + [
            {"role": "user", "content": content},
            {"role": "assistant", "content": response}
        ]
        await memory.save(str(user_id), "history", new_history)

    await message.reply(response, mention_author=True)

    # GIF logic
    if ENABLE_GIPHY and gif_cooldown_counter == 0 and random.random() < GIF_CHANCE:
        try:
            giphy_url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": GIPHY_API_KEY,
                "q": content,
                "limit": 10,
                "offset": 0,
                "rating": "pg-13",
                "lang": "en"
            }
            response_gif = requests.get(giphy_url, params=params, timeout=5)
            if response_gif.status_code == 200:
                data = response_gif.json()
                if data["data"]:
                    gif_choice = random.choice(data["data"])
                    gif_url = gif_choice["images"]["original"]["url"]
                    await message.channel.send(gif_url)
                else:
                    safe_log("⚠️ No GIFs found for query.")
            else:
                safe_log(f"⚠️ Giphy API error: {response_gif.status_code}")
        except Exception as e:
            safe_log(f"⚠️ Giphy request failed: {e}")
        gif_cooldown_counter = GIF_COOLDOWN
    elif gif_cooldown_counter > 0:
        gif_cooldown_counter -= 1

    # Reaction logic
    if ENABLE_REACTIONS and react_cooldown_counter == 0:
        try:
            await message.add_reaction("🔥")
            react_cooldown_counter = REACT_COOLDOWN
        except discord.HTTPException:
            pass
    elif react_cooldown_counter > 0:
        react_cooldown_counter -= 1

def safe_log(msg, level="info"):
    if DEBUG_MODE or level == "error":
        print(msg)

client.run(TOKEN)
