# ChatGPT-Discord 🤖✨
Bring your custom ChatGPT personality to Discord. Fully customizable. No coding required.

> [!TIP]
> This project is presented as is, without warranty. It's a personal project and I'm making public in order to easily allow my friends to use and/or test.
---

## 🚀 Quick Start

1. **Get API Keys**
   - OpenAI API Key
   - Discord Bot Token
   - (Optional) Google API Key for web search
   - (Optional) Giphy API Key for GIFs

2. **Edit `.env`**
   - Paste your ChatGPT custom instructions into `BOT_PERSONA`
   - Fill in `BOT_NAME`, `OWNER_TONE`, `OTHERS_TONE`, and API keys

3. **Run the Bot**
```bash
docker-compose up --build
```
To stop:
```bash
docker-compose down
```

---

## 🧠 Memory (ON by default)

This bot remembers conversations with each user for more natural replies.  
Memory is **enabled by default** so your bot feels more human.  

If you prefer the bot to act stateless (forgetting all conversations), set:
```env
MEMORY_ENABLED=false
```

### Redis Details
By default, the bot uses Docker's built-in Redis at:
```
redis://redis:6379
```
To use an external Redis instance, set `REDIS_URL` in `.env`:
```env
REDIS_URL=redis://your-redis-instance:6379
```

---

## 🔥 Escalation System (OFF by default)

When enabled, the bot escalates its tone with users who:
- Spam messages
- Send too many GIFs
- Flirt or act disrespectful

### Escalation Levels
1. Cool and detached  
2. Cold and intimidating  
3. Sharp and ruthless (shuts them down)

Enable in `.env`:
```env
ESCALATION_ENABLED=true
```

---

## 📝 Example Personality Configuration

You can fully customize your bot’s personality and tones in `.env`:
```env
BOT_NAME=Alex
BOT_PERSONA="You are Alex, a sarcastic barista who roasts latte orders but secretly cares."
OWNER_TONE="warm, flirty"
OTHERS_TONE="snarky, dismissive"
```
Just copy your ChatGPT Custom Instructions into `BOT_PERSONA`.

---

## 📦 Features

- 🧠 Memory system (on by default) for human-like conversation flow
- 🔥 Optional escalation for spammy or disrespectful users
- 🔍 Web search fallback (Google + DuckDuckGo)
- 🎨 Fully customizable personality and tone
- 🐳 Docker-ready for easy deployment
- 🌐 Supports GIFs and message reactions

---

## 🐳 Deploy with Docker

Start the bot:
```bash
docker-compose up --build
```

Stop the bot:
```bash
docker-compose down
```

---

## 🛠 Troubleshooting

### ⚠️ Redis Connection Failed
If you see:
```
⚠️ Memory disabled due to Redis error: ...
```
This means the bot couldn't connect to Redis (memory database).  
- By default, Docker runs Redis at `redis://redis:6379`
- Check if Redis is running:
```bash
docker ps
```
- If not, restart Docker Compose:
```bash
docker-compose down
docker-compose up --build
```
If you don’t need memory, set:
```env
MEMORY_ENABLED=false
```

---

### ⚠️ OpenAI API Issues
If you see:
```
openai.error.AuthenticationError: Invalid API key
```
- Double-check your `OPENAI_API_KEY` in `.env`
- Ensure your OpenAI account has API access.

---

### ⚠️ Discord Token Errors
If the bot doesn't start and shows:
```
discord.errors.LoginFailure: Improper token has been passed.
```
- Verify your `DISCORD_TOKEN` in `.env`
- It must be a bot token from the Discord Developer Portal.

---

## 🧑‍💻 Support

This package is designed to be plug-and-play.  
If you encounter issues, double-check your `.env` configuration and ensure all Docker containers are running.
