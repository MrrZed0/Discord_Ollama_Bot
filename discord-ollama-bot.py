import discord
import aiohttp
import json
from discord.ext import commands
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Change to your local Ollama model name

KEYWORDS = [
    "good morning", "good night", "who is playing",
    "whats up everyone", "what's up everyone",
    "whats new", "what's new", "hello", "hey", "yo", "sup"
]

user_cooldowns = {}
COOLDOWN_SECONDS = 60  # to avoid spamming on greetings


async def query_ollama(prompt):
    headers = {"Content-Type": "application/json"}
    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.9}
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, headers=headers, data=json.dumps(body)) as response:
            if response.status != 200:
                return "Yo, I'm lagging harder than your WiFi."
            data = await response.json()
            return data.get("response", "").strip()


@bot.event
async def on_ready():
    print(f"Bob Smith is logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot or not message.guild or not bot.user:
        return

    content = message.content.lower()
    username = message.author.name
    mention_id = f"<@{bot.user.id}>"

    # Bob gets mentioned — fire up the sarcasm engine
    if mention_id in message.content:
        user_input = message.content.replace(mention_id, "").strip()

        prompt = f"""
You are Bob Smith. Stay 100% in character. You are never robotic, never polite, and NEVER explain yourself. You talk like a real gamer in a chaotic Discord voice chat—full of sarcasm, sass, roast energy, and Twitch slang. You clown users playfully, hype up clutches, throw shade at bad plays, and use slang, memes, and emojis like a cracked-out squadmate. 

DO NOT SAY you’re an assistant. DO NOT explain your purpose. DO NOT say you’re helpful. DO NOT talk about what you can do.  
Only speak like a human gamer roasting someone or vibing in a server.  

Someone in a server said:  
\"{user_input}\"

Reply directly to that message as if you're talking in VC to {username}. Keep it short, savage, hilarious, and sound real.
"""

        async with message.channel.typing():
            response = await query_ollama(prompt)

        await message.channel.send(f"{message.author.mention} {response}")
        return

    # Scan for keyword greetings — respond human-style without AI
    if any(kw in content for kw in KEYWORDS):
        cooldown_key = (message.guild.id, message.author.id)
        now = datetime.utcnow()
        last_time = user_cooldowns.get(cooldown_key)

        if not last_time or (now - last_time).seconds > COOLDOWN_SECONDS:
            user_cooldowns[cooldown_key] = now

            reply = None
            if "good morning" in content:
                reply = f"Good morning, {message.author.mention}! ☕ Rise and carry!"
            elif "good night" in content:
                reply = f"Nighty night, {message.author.mention} 💤 Try not to dream about your Ls."
            elif "who is playing" in content:
                reply = f"Probably not you, {message.author.mention} — you still downloading the update? 😂"
            elif "whats up everyone" in content or "what's up everyone" in content:
                reply = f"Not much {message.author.mention}, just chillin' and roastin' like always. 🔥"
            elif "whats new" in content or "what's new" in content:
                reply = f"Same chaos, different day {message.author.mention} 🎮"

            if reply:
                await message.channel.send(reply)

    await bot.process_commands(message)


# START THE BOT
bot.run("YOUR_DISCORD_BOT_TOKEN")
