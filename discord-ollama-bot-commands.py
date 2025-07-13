import discord
import aiohttp
import json
import random
from discord.ext import commands
from datetime import datetime

# -----------------------
# Discord & Ollama Config
# -----------------------

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Replace with your Ollama model name

# ------------------
# Keyword triggers
# ------------------

KEYWORDS = [
    "good morning", "good night", "who is playing",
    "whats up everyone", "what's up everyone",
    "whats new", "what's new", "hello", "hey", "yo", "sup"
]

user_cooldowns = {}
COOLDOWN_SECONDS = 60  # cooldown for keyword replies


# -------------------------
# Ollama query helper func
# -------------------------

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
                return "Yo, I lagged out mid-response 💀"
            data = await response.json()
            return data.get("response", "").strip()


# --------------
# Bot ready event
# --------------

@bot.event
async def on_ready():
    print(f"🔥 Bob Smith is live as {bot.user} 🔥")


# -----------------
# On message event
# -----------------

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    username = message.author.name
    mention_id = f"<@{bot.user.id}>"

    # Check if Bob was mentioned or "bob"/"bob smith" called
    triggered = (
        mention_id in message.content or
        "bob smith" in content or
        content.strip().startswith("bob") or
        " bob " in content
    )

    if triggered:
        user_input = message.content.replace(mention_id, "").strip()

        prompt = f"""
You are Bob Smith. You are NOT a bot. You're a sarcastic, savage gamer who hangs in Discord voice chats roasting, joking, and vibing hard. No robotic replies. Never say you're an AI or assistant.

User message: "{user_input}"

Reply like you're in a chaotic Discord with {username}. Keep it short, funny, and savage.
"""

        async with message.channel.typing():
            response = await query_ollama(prompt)

        await message.channel.send(f"{message.author.mention} {response}")
        return

    # Keyword replies (no AI)
    if any(kw in content for kw in KEYWORDS):
        cooldown_key = (message.guild.id, message.author.id)
        now = datetime.utcnow()
        last_time = user_cooldowns.get(cooldown_key)

        if not last_time or (now - last_time).seconds > COOLDOWN_SECONDS:
            user_cooldowns[cooldown_key] = now

            reply = None
            if "good morning" in content:
                reply = f"Good morning, {message.author.mention}! ☕ Try not to choke in warmups."
            elif "good night" in content:
                reply = f"Good night, {message.author.mention}! Don’t dream of lag spikes. 💤"
            elif "who is playing" in content:
                reply = f"{message.author.mention} asking who's playing like they don’t have 0 wins today. 😂"
            elif "whats up everyone" in content or "what's up everyone" in content:
                reply = f"What’s cookin’, {message.author.mention}? Hope it’s not your CPU again."
            elif "whats new" in content or "what's new" in content:
                reply = f"Same chaos, different clowns. 🎮 What’s good, {message.author.mention}?"
            elif any(w in content for w in ["hello", "hey", "yo", "sup"]):
                reply = f"Yo {message.author.mention}, you finally logged on? Bout time."

            if reply:
                await message.channel.send(reply)

    await bot.process_commands(message)


# -----------------
# Fun commands (AI powered)
# -----------------

@bot.command(name="roastme")
async def roastme(ctx):
    prompt = f"""
You are Bob Smith, a sarcastic, savage gamer chilling in Discord voice chat. Roast the user "{ctx.author.name}" HARD—but funny and good spirited. Use gamer insults and Discord slang. Keep it under 2 lines. Don't say you're an AI.
"""
    async with ctx.channel.typing():
        response = await query_ollama(prompt)
    await ctx.send(f"{ctx.author.mention} {response}")


@bot.command(name="meme")
async def meme(ctx):
    prompt = """
You're Bob Smith, a chaotic, sarcastic gamer hanging out with streamers in Discord. Drop a random, funny, gamer-style meme or one-liner. Use Twitch/Discord slang humor. Less than 2 lines. No bot talk.
"""
    async with ctx.channel.typing():
        response = await query_ollama(prompt)
    await ctx.send(f"{ctx.author.mention} {response}")


@bot.command(name="clip")
async def clip(ctx):
    clips = [
        "https://twitch.tv/clips/ThatOneTimeYouWhiffedEveryShot",
        "https://twitch.tv/clips/BobSmithSavesTheDay",
        "https://twitch.tv/clips/ControllerOnPCBeLike",
        "https://twitch.tv/clips/SkillIssueLiveOnStream",
        f"{ctx.author.name} just dropped a clip—accidentally streaming their desktop. 😂",
        "https://twitch.tv/clips/HighLatencyHype"
    ]
    await ctx.send(f"{ctx.author.mention} {random.choice(clips)}")


# -------------------
# Run your bot here
# -------------------

bot.run("YOUR_DISCORD_BOT_TOKEN")
