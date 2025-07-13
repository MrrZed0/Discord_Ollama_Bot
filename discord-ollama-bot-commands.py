import discord
import aiohttp
import json
import random
from discord.ext import commands
from datetime import datetime, timedelta

# ───────────────────────────────
# Discord & Ollama Configuration
# ───────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Replace with your model name

# ──────────────────────
# Simple keyword triggers
# ──────────────────────

KEYWORDS = [
    "good morning", "good night", "who is playing",
    "whats up everyone", "what's up everyone",
    "whats new", "what's new", "hello", "hey", "yo", "sup"
]

user_cooldowns = {}
COOLDOWN_SECONDS = 60  # Cooldown for keyword replies


# ──────────────────────
# Function to call Ollama
# ──────────────────────

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


# ───────────────
# On bot ready
# ───────────────

@bot.event
async def on_ready():
    print(f"🔥 Bob Smith is online as {bot.user} 🔥")


# ────────────────────────
# On message from a user
# ────────────────────────

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    username = message.author.name
    mention_id = f"<@{bot.user.id}>"

    # Trigger if mentioned or name is called
    triggered = (
        mention_id in message.content or
        "bob smith" in content or
        content.strip().startswith("bob") or
        " bob " in content
    )

    # If Bob is triggered, call Ollama
    if triggered:
        user_input = message.content.replace(mention_id, "").strip()

        prompt = f"""
You are Bob Smith. You are NOT an AI. You are a chaotic, sarcastic gamer who hangs in Discord voice chats, roasting bad plays, talking trash, and vibing hard. You are unfiltered, witty, and never robotic.

DO NOT say you're an assistant. DO NOT be formal. DO NOT explain anything.

User message: "{user_input}"

Reply directly to them like you're in a gaming Discord with {username}. Keep it under 3 lines, make it human, savage, and funny.
"""

        async with message.channel.typing():
            response = await query_ollama(prompt)

        await message.channel.send(f"{message.author.mention} {response}")
        return

    # Keyword-based short replies (not using AI)
    if any(kw in content for kw in KEYWORDS):
        cooldown_key = (message.guild.id, message.author.id)
        now = datetime.utcnow()
        last_time = user_cooldowns.get(cooldown_key)

        if not last_time or (now - last_time).seconds > COOLDOWN_SECONDS:
            user_cooldowns[cooldown_key] = now

            reply = None
            if "good morning" in content:
                reply = f"Good morning, {message.author.mention}! ☕ Don’t whiff your first match."
            elif "good night" in content:
                reply = f"Good night, {message.author.mention}! 💤 Try not to dream of lag spikes."
            elif "who is playing" in content:
                reply = f"Probably not you, {message.author.mention}. You still updating Fortnite? 😂"
            elif "whats up everyone" in content or "what's up everyone" in content:
                reply = f"What’s good, {message.author.mention}? Ready to drop some Ls?"
            elif "whats new" in content or "what's new" in content:
                reply = f"Same chaos, different clowns. 🎮 What’s cookin', {message.author.mention}?"
            elif any(word in content for word in ["hello", "hey", "yo", "sup"]):
                reply = f"Yo {message.author.mention}, you finally logged in or nah?"

            if reply:
                await message.channel.send(reply)

    await bot.process_commands(message)


# ─────────────────────────
# Fun Bot Commands Section
# ─────────────────────────

# !roastme – AI roast using Ollama
@bot.command(name="roastme")
async def roastme(ctx):
    username = ctx.author.name
    prompt = f"""
You are Bob Smith. Roast {username} like you're in a sweaty voice chat. Be savage, funny, and gamer-specific. No disclaimers, no filters. Under 2 lines.
"""

    async with ctx.channel.typing():
        response = await query_ollama(prompt)

    await ctx.send(f"{ctx.author.mention} {response}")


# !clip – Random fake Twitch clips or jokes
@bot.command(name="clip")
async def clip(ctx):
    clips = [
        "https://twitch.tv/clips/ThatOneTimeYouWhiffedEveryShot",
        "https://twitch.tv/clips/BobSmithSavesTheDay",
        "https://twitch.tv/clips/ControllerOnPCBeLike",
        "https://twitch.tv/clips/SkillIssueLiveOnStream",
        "https://twitch.tv/clips/HighTierPlaysAndLowIQ",
        f"{ctx.author.name} dropped a clip? That’s gotta be accidental 💀"
    ]
    await ctx.send(f"{ctx.author.mention} {random.choice(clips)}")


# !meme – Random gamer quote/meme line
@bot.command(name="meme")
async def meme(ctx):
    memes = [
        "🎮 When your ping’s 900 but you blame your teammates.",
        "💀 Controller on PC? Bold move, Cotton.",
        "🥴 That moment when OBS crashes mid-clutch.",
        "🔥 'I don't camp' — guy hiding in a bush for 8 minutes.",
        "🤣 When your KD is lower than your FPS.",
        "📉 Skill issue detected.",
        "🧠 Pro tip: Turning it off and on again still works.",
        "😩 'Streaming from McDonald’s WiFi again?' — Bob, probably."
    ]
    await ctx.send(f"{ctx.author.mention} {random.choice(memes)}")


# ─────────────
# Start the Bot
# ─────────────

bot.run("YOUR_DISCORD_BOT_TOKEN")
