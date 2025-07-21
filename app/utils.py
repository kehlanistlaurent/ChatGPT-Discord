import requests
import random

def clean_message(content, bot_name):
    return content.replace(f"@{bot_name}", "").strip()

async def search_web(query):
    try:
        return f"Search results for '{query}' (pretend link)."  # Placeholder for real API
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return "Couldn’t fetch search results."

async def get_gif(query, giphy_key):
    try:
        resp = requests.get(
            "https://api.giphy.com/v1/gifs/search",
            params={"api_key": giphy_key, "q": query, "limit": 1, "rating": "pg"}
        )
        data = resp.json()
        if data['data']:
            return data['data'][0]['url']
    except Exception as e:
        print(f"❌ GIF fetch error: {e}")
    return None

async def add_reaction(message):
    emojis = ["🔥", "😏", "💎", "😉"]
    try:
        await message.add_reaction(random.choice(emojis))
    except Exception as e:
        print(f"❌ Reaction error: {e}")
