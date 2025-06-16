import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import random
import json
import os
import asyncio
from googletrans import Translator

from moodcookies import (
    STANDARD_MODES, GLITCHED_MODES, SEASONAL_MODES,
    MODE_DESCRIPTIONS, MODE_COLORS, MODE_FOOTERS, FORM_PROFILES,
    FORM_EMOJIS, MODE_TEXTS_ENGLISH, MODE_TONE, FLAVOR_TEXTS
)

# ========== CONFIG ==========
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is missing from environment variables.")

LANGUAGE_FILE = "languages.json"

# ========== SETUP ==========
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)
translator = Translator()
tree = bot.tree

# ========== LANGUAGE FILE HANDLING ==========
if os.path.exists(LANGUAGE_FILE):
    with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
        all_languages = json.load(f)
else:
    all_languages = {"guilds": {}}

def save_languages():
    with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_languages, f, indent=2, ensure_ascii=False)

def get_user_language(guild_id: str, user_id: str):
    try:
        return all_languages["guilds"][guild_id]["users"][user_id]
    except KeyError:
        return None

# ========== EVENTS ==========

@bot.event
async def on_ready():
    print(f"✨ Whisperling has fluttered to life as {bot.user}!")
    try:
        synced = await tree.sync()
        print(f"🧚 Synced {len(synced)} fairy commands.")
    except Exception as e:
        print(f"❗ Failed to sync spells: {e}")

    bot.loop.create_task(glitch_reversion_loop())
    bot.loop.create_task(decay_activity_loop())
    bot.loop.create_task(grove_heartbeat(bot))

async def glitch_reversion_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now(timezone.utc)

        for guild_id, timestamp in list(glitch_timestamps_by_guild.items()):
            mode = guild_modes[guild_id]
            guild = bot.get_guild(int(guild_id))

            if mode not in GLITCHED_MODES + SEASONAL_MODES:
                continue

            # Flutterkin expiry
            if mode == "flutterkin" and timestamp and (now - timestamp > timedelta(minutes=30)):
                previous = previous_standard_mode_by_guild[guild_id]
                print(f"🍼 Flutterkin nap time for {guild_id}. Reverting to {previous}.")
                await apply_mode_change(guild, previous)
                glitch_timestamps_by_guild[guild_id] = None

            # Other glitched modes expiry
            elif mode in ["echovoid", "glitchspire", "crepusca"] and timestamp and (now - timestamp > timedelta(minutes=30)):
                previous = previous_standard_mode_by_guild[guild_id]
                print(f"⏳ Glitch expired for {guild_id}. Reverting to {previous}.")
                await apply_mode_change(guild, previous)
                glitch_timestamps_by_guild[guild_id] = None

            # Seasonal mode expired out-of-season
            elif mode in SEASONAL_MODES and not is_current_season_mode(mode):
                previous = previous_standard_mode_by_guild[guild_id]
                print(f"🗓️ {mode} expired for {guild_id}. Reverting to {previous}.")
                await apply_mode_change(guild, previous)
                glitch_timestamps_by_guild[guild_id] = None

        await asyncio.sleep(60)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    register_message_activity(str(message.guild.id), str(message.channel.id))
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)

    if not guild_config:
        print(f"👤 Member joined, but no guild config for {guild_id}.")
        return

    welcome_channel_id = guild_config.get("welcome_channel_id")
    if not welcome_channel_id:
        print(f"👤 Member joined, but no welcome_channel set for {guild_id}.")
        return

    channel = bot.get_channel(welcome_channel_id)
    lang_map = guild_config.get("languages", {})

    if not lang_map:
        await channel.send(f"🌱 {member.mention}, no languages are set up yet.")
        return

    await send_language_selector(member, channel, lang_map, guild_config)

# Per-guild mode tracking
guild_modes = defaultdict(lambda: "dayform")
last_interaction_by_guild = defaultdict(lambda: datetime.now(timezone.utc))
previous_standard_mode_by_guild = defaultdict(lambda: "dayform")
glitch_timestamps_by_guild = defaultdict(lambda: None)
flutterkin_usage_count_by_guild = {}

def maybe_trigger_glitch(guild_id: str):
    """
    Occasionally trigger a glitched mode.
    """
    chance = random.random()

    # Base ~3% chance per interaction
    if chance < 0.03:
        return random.choice(GLITCHED_MODES)
    return None

def get_flavor_text(mode):
    return random.choice(FLAVOR_TEXTS[mode])

from datetime import datetime, timezone

async def grove_heartbeat(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        now = datetime.now(timezone.utc)

        for guild in bot.guilds:
            guild_id = str(guild.id)
            mode = guild_modes.get(guild_id, "dayform")
            activity_level = get_activity_level(guild_id)

            guild_config = all_languages["guilds"].get(guild_id, {})
            whispers_enabled = guild_config.get("whispers_enabled", True)

            if whispers_enabled:
                # 💡 Safely retrieve last flavor time, defaulting to "now minus cooldown" if missing
                last_sent = last_flavor_sent.get(guild_id)
                
                if last_sent is None:
                    # If no record, treat as if cooldown expired
                    last_sent = now - timedelta(hours=3)

                # 💡 Convert to timezone-aware if somehow naive
                if last_sent.tzinfo is None:
                    last_sent = last_sent.replace(tzinfo=timezone.utc)

                time_since_last = (now - last_sent).total_seconds()
                cooldown_seconds = 2 * 60 * 60

                if time_since_last >= cooldown_seconds:
                    base_flavor_chance = 0.03
                    weighted_chance = base_flavor_chance + (activity_level / 300)
                    flavor_chance = min(weighted_chance, 0.15)

                    if random.random() < flavor_chance:
                        flavor = get_flavor_text(mode)
                        channel = (
                            guild.system_channel
                            or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                        )

                        if channel and flavor:
                            lang_map = guild_config.get("languages", {})

                            if lang_map and random.random() < 0.5:
                                possible_langs = list(lang_map.keys())
                                chosen_lang = random.choice(possible_langs)
                                try:
                                    translated = translator.translate(flavor, dest=chosen_lang).text
                                    flavor_to_send = f"{translated} ({chosen_lang})"
                                except Exception as e:
                                    print(f"🌐 Translation failed: {e}")
                                    flavor_to_send = flavor
                            else:
                                flavor_to_send = flavor

                            await channel.send(flavor_to_send)
                            last_flavor_sent[guild_id] = now

            if mode in STANDARD_MODES:
                last_seen = last_interaction_by_guild.get(guild_id, now)
                
                if last_seen.tzinfo is None:
                    last_seen = last_seen.replace(tzinfo=timezone.utc)

                days_idle = (now - last_seen).days

                if days_idle >= 30 and random.random() < 0.25:
                    possible_modes = [m for m in STANDARD_MODES if m != mode]
                    new_mode = random.choice(possible_modes)
                    print(f"🌿 Mood drift for {guild.name} -> {new_mode}")
                    await apply_mode_change(guild, new_mode)

        await asyncio.sleep(600)

@bot.command()
async def formcompendium(ctx):
    embed = discord.Embed(
        title="🌿 Whisperling Form Compendium",
        description="Gently select a form to explore its mood & flavor:",
        color=discord.Color.blurple()
    )
    avatar_url = bot.user.avatar.url if bot.user.avatar else None
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    view = FormCompendiumDropdown(ctx)
    await ctx.send(embed=embed, view=view)


class FormCompendiumDropdown(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx

        # Build dropdown options dynamically from profiles
        options = []
        for key, data in FORM_PROFILES.items():
            label = f"{data['emoji']} {key.title()} ({data['type']})"
            options.append(discord.SelectOption(label=label, value=key))

        self.add_item(FormSelect(options, ctx))


class FormSelect(Select):
    def __init__(self, options, ctx):
        super().__init__(
            placeholder="Choose a form...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        selected_key = self.values[0]
        profile = FORM_PROFILES.get(selected_key)
        emoji_url = FORM_EMOJIS.get(selected_key)

        embed = discord.Embed(
            title=f"{profile['emoji']} {selected_key.title()} — {profile['type']} Form",
            color=discord.Color.blurple()
        )

        embed.add_field(name="Vibe", value=profile['vibe'], inline=False)
        embed.add_field(name="Personality", value=profile['personality'], inline=False)
        embed.add_field(name="Style", value=profile['style'], inline=False)
        embed.add_field(name="Example", value=profile['example'], inline=False)

        if emoji_url:
            embed.set_thumbnail(url=emoji_url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# ================= UTIL FUNCTION =================
def style_text(guild_id, text):
    mode = guild_modes[str(guild_id)]
    return MODE_TONE.get(mode, lambda t: t)(text)

# --- (Season triggers — keep if still used!) ---

def is_spring_equinox():
    today = datetime.now(timezone.utc)
    return today.month == 3 and 17 <= today.day <= 23

def is_autumn_equinox():
    today = datetime.now(timezone.utc)
    return today.month == 9 and 19 <= today.day <= 25

def is_summer_solstice():
    today = datetime.now(timezone.utc)
    return today.month == 6 and 18 <= today.day <= 24

def is_winter_solstice():
    today = datetime.now(timezone.utc)
    return today.month == 12 and 18 <= today.day <= 24

# --- Avatar updates ---

async def update_avatar_for_mode(mode: str):
    avatar_paths = {
        "sunfracture": "avatars/sunfracture.png",
        "yuleshard": "avatars/yuleshard.png",
        "vernalglint": "avatars/vernalglint.png",
        "fallveil": "avatars/fallveil.png",
        "basic": "avatars/basic_whisperling.png"
    }

    avatar_key = mode if mode in SEASONAL_MODES else "basic"
    path = avatar_paths.get(avatar_key)

    if path and os.path.exists(path):
        with open(path, 'rb') as f:
            try:
                await bot.user.edit(avatar=f.read())
                print(f"✨ Avatar updated for mode: {avatar_key}")
            except discord.HTTPException as e:
                print(f"❗ Failed to update avatar: {e}")
    else:
        print(f"⚠️ No avatar found for mode: {avatar_key}")

# --- Apply mode change safely ---

async def apply_mode_change(guild, mode):
    guild_id = str(guild.id)
    now = datetime.now(timezone.utc)

    previous_standard_mode_by_guild[guild_id] = guild_modes.get(guild_id, "dayform")
    guild_modes[guild_id] = mode

    if mode in GLITCHED_MODES or mode in SEASONAL_MODES:
        glitch_timestamps_by_guild[guild_id] = now
    else:
        glitch_timestamps_by_guild[guild_id] = None

    last_interaction_by_guild[guild_id] = now

    await announce_mode_change(guild, mode)

# --- Build embed correctly ---

def build_whisperling_embed(guild_id, title: str, description: str):
    mode = guild_modes.get(str(guild_id), "dayform")  # Pull mode cleanly

    # Build path directly — because you *do* have every file
    avatar_path = f"avatars/{mode}.png"

    embed = discord.Embed(
        title=title,
        description=description,
        color=MODE_COLORS.get(mode, discord.Color.green())
    )

    if os.path.exists(avatar_path):
        file = discord.File(avatar_path, filename="avatar.png")
        embed.set_thumbnail(url="attachment://avatar.png")
        return embed, file
    else:
        # Fallback only if file missing
        return embed, None

async def announce_mode_change(guild, mode):
    embed, file = build_whisperling_embed(
        str(guild.id),  # always cast to string for consistency
        f"✨ Whisperling shifts into {mode.title()}",
        MODE_DESCRIPTIONS.get(mode, "Whisperling gently shifts.")
    )

    channel = (
        guild.system_channel
        or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
    )

    if not channel:
        print(f"⚠️ No writable channel found in {guild.name} for mode announcement.")
        return

    if file:
        await channel.send(embed=embed, file=file)
    else:
        await channel.send(embed=embed)

# ================= ACTIVITY TRACKER =================

# Core activity storage
activity_score_by_guild = defaultdict(int)
last_decay_by_guild = defaultdict(lambda: datetime.utcnow())
last_active_channel_by_guild = {}
last_flavor_sent = defaultdict(lambda: datetime.min)

# Tuning parameters
MESSAGE_WEIGHT = 5
VOICE_WEIGHT = 10
DECAY_AMOUNT = 1
DECAY_INTERVAL = timedelta(minutes=2)
MAX_ACTIVITY_SCORE = 100

# Called whenever a message is sent
def register_message_activity(guild_id: str, channel_id: str):
    activity_score_by_guild[guild_id] = min(
        activity_score_by_guild[guild_id] + MESSAGE_WEIGHT, MAX_ACTIVITY_SCORE
    )
    last_active_channel_by_guild[guild_id] = channel_id

# Called whenever someone joins voice
def register_voice_activity(guild_id: str):
    activity_score_by_guild[guild_id] = min(
        activity_score_by_guild[guild_id] + VOICE_WEIGHT, MAX_ACTIVITY_SCORE
    )

# Activity decay loop
async def decay_activity_loop():
    while True:
        now = datetime.utcnow()
        for guild_id in list(activity_score_by_guild.keys()):
            last_decay = last_decay_by_guild[guild_id]
            if now - last_decay >= DECAY_INTERVAL:
                activity_score_by_guild[guild_id] = max(
                    activity_score_by_guild[guild_id] - DECAY_AMOUNT, 0
                )
                last_decay_by_guild[guild_id] = now
        await asyncio.sleep(60)

# Called by grove heartbeat to read current activity
def get_activity_level(guild_id: str) -> int:
    return activity_score_by_guild[guild_id]

# ================= ADMIN CONTROLS =================

@bot.command(aliases=["backupwhisp"])
@commands.is_owner()
async def backupwhisperling(ctx):
    """📦 Sends the current languages.json as a backup."""
    try:
        file_path = "languages.json"

        if not os.path.exists(file_path):
            await ctx.send("❗ languages.json doesn't exist.")
            return

        await ctx.author.send(
            content="📂 Here is your current `languages.json` backup:",
            file=discord.File(file_path)
        )
        await ctx.send("✅ Sent you the backup in DMs!")

    except discord.Forbidden:
        await ctx.send("❌ I couldn't DM you. Please enable DMs from server members or try again later.")
    except Exception as e:
        await ctx.send(f"❗ Error sending backup: {e}")

@tree.command(name="adminhelp", description="📘 A magical guide to setting up Whisperling (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def adminhelp(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "Whisperling is ready to help your grove bloom 🌷")

    embed = discord.Embed(
        title="📘 Admin Setup Guide – Whisperling's Grove",
        description=(
            "Let me gently guide you through setting up the magical welcome journey:\n"
            "**(Aliases)**: `adminhilfe` 🇩🇪 | `aideadmin` 🇫🇷 | `ayudaadmin` 🇪🇸"
        ),
        color=embed_color
    )

    embed.add_field(
        name="1️⃣ Set the Welcome Channel",
        value="`!setwelcomechannel #channel` – Where new members are greeted.",
        inline=False
    )

    embed.add_field(
        name="2️⃣ Add Languages",
        value=(
            "`!preloadlanguages` – Adds English, German, Spanish, and French\n"
            "`!addlanguage <code> <name>` – Add manually\n"
            "_Example:_ `!addlanguage it Italiano`"
        ),
        inline=False
    )

    embed.add_field(
        name="3️⃣ Custom Welcome Messages",
        value=(
            "`!setwelcome <code> <message>` – Per-language message\n"
            "Use `{user}` for the joining member’s name.\n"
            "_Example:_ `!setwelcome fr Bienvenue, {user} !`"
        ),
        inline=False
    )

    embed.add_field(
        name="4️⃣ Server Rules (Multi-Language)",
        value=(
            "`!setrules <code> <text>` – Per-language rules text\n"
            "_Example:_ `!setrules en Please be kind.`"
        ),
        inline=False
    )

    embed.add_field(
        name="5️⃣ Role Setup",
        value=(
            "`!addroleoption @role <emoji> <label>` – Add a main role\n"
            "`!removeroleoption @role` – Remove a main role\n"
            "`!listroleoptions` – View all added main roles"
        ),
        inline=False
    )

    embed.add_field(
        name="6️⃣ Cosmetic Roles",
        value=(
            "`!addcosmetic @role <emoji> <label>` – Add a cosmetic flair\n"
            "`!removecosmetic @role` – Remove a flair\n"
            "`!listcosmetics` – See added sparkles ✨"
        ),
        inline=False
    )

    embed.add_field(
        name="7️⃣ Manually Start Welcome Flow",
        value=(
            "`!startwelcome @member` – Triggers full welcome (language, rules, roles)\n"
            "Use for existing members who joined before setup."
        ),
        inline=False
    )

    embed.add_field(
        name="8️⃣ Assign a Language",
        value=(
            "`!assignlanguage @member <code>` – Manually set a user’s language\n"
            "_Example:_ `!assignlanguage @luna de`"
        ),
        inline=False
    )

    embed.add_field(
        name="🌐 Language Tools",
        value=(
            "`!listlanguages` – View active\n"
            "`!removelanguage <code>` – Remove\n"
            "`!langcodes` – View common translation codes"
        ),
        inline=False
    )

    embed.add_field(
        name="🌸 Whisperling Mood",
        value=(
            "`!setmode <form>` – Change appearance\n"
            "`!moodcheck` – View current form"
        ),
        inline=False
    )

    embed.add_field(
        name="🚪 Moderation Commands",
        value=(
            "`/kick @member` – Politely remove someone from the grove.\n"
            "`/ban @member` – Permanently banish someone from the grove."
        ),
        inline=False
    )
    embed.add_field(
       name="🌬️ Whisperling’s Chatter",
        value="`!togglewhispers` – Enable or disable her random sighs, whispers, and future collectible drops.",
        inline=False
    )
    embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(aliases=["toggleflavor", "togglechatter"])
@commands.has_permissions(administrator=True)
async def togglewhispers(ctx):
    guild_id = str(ctx.guild.id)
    config = all_languages["guilds"].setdefault(guild_id, {})
    current = config.get("whispers_enabled", True)
    config["whispers_enabled"] = not current
    save_languages()

    status = "enabled" if config["whispers_enabled"] else "disabled"
    await ctx.send(f"🌸 Whisperling's soft whispers are now **{status}**.")

@bot.command(aliases=["formwechsel", "modedeforme", "cambiodemodo"])
async def setmode(ctx, mode: str):
    mode = mode.lower()
    guild = ctx.guild
    guild_id = str(guild.id)

    if mode == "random":
        chosen = random.choice(STANDARD_MODES)
        previous_standard_mode_by_guild[guild_id] = guild_modes[guild_id]
        guild_modes[guild_id] = chosen
        last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)
        await apply_mode_change(guild, chosen)
        await ctx.send(f"🎲 Whisperling closed her eyes and chose **{chosen}**!")
        return

    if mode in GLITCHED_MODES + SEASONAL_MODES:
        await ctx.send("❗ This form cannot be chosen directly. It arrives only when the Grove wills it...")
        return

    if mode not in STANDARD_MODES:
        valid = ", ".join(STANDARD_MODES + ["random"])
        await ctx.send(f"❗ Unknown form. Choose from: {valid}")
        return

    previous_standard_mode_by_guild[guild_id] = guild_modes[guild_id]
    guild_modes[guild_id] = mode
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)
    await apply_mode_change(guild, mode)
    await ctx.send(f"🧚 Whisperling now shifts into **{mode}**!")

# =========================

@bot.command(aliases=["stimmungsprüfung", "humeure", "estadodeanimo"])
async def moodcheck(ctx):
    guild_id = str(ctx.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    description = MODE_DESCRIPTIONS.get(mode, "A gentle presence stirs in the grove...")
    footer = MODE_FOOTERS.get(mode, "")

    embed, file = build_whisperling_embed(guild_id, f"🌿 Whisperling’s Current Mood: **{mode}**", description)
    embed.set_footer(text=footer)

    if file:
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed)

@bot.command(aliases=["sprachenvorladen", "prélangues", "precargaridiomas"])
@commands.has_permissions(administrator=True)
async def preloadlanguages(ctx):
    guild_id = str(ctx.guild.id)

    # Make sure guild config exists
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    # Create 'languages' if missing
    all_languages["guilds"][guild_id]["languages"] = {
        "en": {"name": "English", "welcome": "Welcome, {user}!"},
        "de": {"name": "Deutsch", "welcome": "Willkommen, {user}!"},
        "es": {"name": "Español", "welcome": "¡Bienvenido, {user}!"},
        "fr": {"name": "Français", "welcome": "Bienvenue, {user}!"}
    }

    # Also make sure 'users' exists (for smoother translation system later)
    if "users" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["users"] = {}

    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "Whisperling tends the grove 🌱")

    embed = discord.Embed(
        title="🦋 Languages Preloaded",
        description="English, German, Spanish, and French have been added for your grove.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["setwillkommenskanal", "canalaccueil", "canalbienvenida"])
@commands.has_permissions(administrator=True)
async def setwelcomechannel(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)

    # Make sure guild config exists
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    # Safeguard nested structures
    if "languages" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["languages"] = {}
    if "users" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["users"] = {}

    all_languages["guilds"][guild_id]["welcome_channel_id"] = channel.id
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "Whisperling tends the grove 🌱")

    embed = discord.Embed(
        title="🕊️ Whisper Channel Chosen",
        description=f"New members will now be greeted in {channel.mention}.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["addsprache", "ajouterlangue", "agregaridioma"])
@commands.has_permissions(administrator=True)
async def addlanguage(ctx, code: str, *, name: str):
    guild_id = str(ctx.guild.id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    if "languages" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["languages"] = {}
    if "users" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["users"] = {}

    languages = all_languages["guilds"][guild_id]["languages"]

    if code in languages:
        await ctx.send(f"❗ Language `{code}` already exists. Use `!setwelcome` to update it.")
        return

    languages[code] = {
        "name": name,
        "welcome": f"Welcome, {{user}}!"
    }

    save_languages()
    await ctx.send(f"🦋 Added language: `{name}` with code `{code}`.")


@bot.command(aliases=["sprachentfernen", "supprimerlangue", "eliminaridioma"])
@commands.has_permissions(administrator=True)
async def removelanguage(ctx, code: str):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)

    if not guild_config:
        await ctx.send(f"❗ No languages found for this server.")
        return

    if "languages" not in guild_config or code not in guild_config["languages"]:
        await ctx.send(f"❗ Language `{code}` not found for this server.")
        return

    del all_languages["guilds"][guild_id]["languages"][code]
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "Whisperling watches over the grove 🌿")

    embed = discord.Embed(
        title="🗑️ Language Removed",
        description=f"The language with code `{code}` has been successfully removed.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["sprachefestlegen", "assignlangue", "asignaridioma"])
@commands.has_permissions(administrator=True)
async def assignlanguage(ctx, member: discord.Member, lang_code: str):
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    # Defensive: Ensure full guild structure always exists
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {"languages": {}, "users": {}}

    guild_config = all_languages["guilds"][guild_id]

    if "languages" not in guild_config:
        guild_config["languages"] = {}
    if "users" not in guild_config:
        guild_config["users"] = {}

    lang_map = guild_config["languages"]

    if not lang_map:
        return await ctx.send("❗ This server has no languages configured yet.")

    if lang_code not in lang_map:
        available = ", ".join(lang_map.keys())
        return await ctx.send(f"❗ Invalid language code. Available codes: `{available}`")

    # Actually assign language
    guild_config["users"][user_id] = lang_code
    save_languages()

    # 🌿 Mood-flavored embed
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.green())
    footer = MODE_FOOTERS.get(mode, "Whisperling watches over the grove 🌿")

    lang_name = lang_map[lang_code].get("name", lang_code)
    embed = discord.Embed(
        title="🌐 Language Assigned",
        description=f"{member.mention}'s language has been set to **{lang_name}**.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["begrüßungsetzen", "definirbienvenue", "establecerbienvenida"])
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, code: str, *, message: str):
    guild_id = str(ctx.guild.id)

    # Ensure full guild structure exists
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {"languages": {}, "users": {}}

    guild_config = all_languages["guilds"][guild_id]
    languages = guild_config.get("languages", {})

    if code not in languages:
        await ctx.send(f"❗ Language `{code}` is not set up for this server.")
        return

    languages[code]["welcome"] = message
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🌼 Welcome Message Updated",
        description=f"The welcome message for `{code}` is now:\n\n```{message}```",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["regelnsetzen", "règlesdefinir", "definirreglas"])
@commands.has_permissions(administrator=True)
async def setrules(ctx, lang_code: str, *, rules: str):
    guild_id = str(ctx.guild.id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {"languages": {}, "rules": {}, "users": {}}

    if "rules" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["rules"] = {}

    all_languages["guilds"][guild_id]["rules"][lang_code] = rules
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.green())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="📜 Grove Rules Updated",
        description=f"The rules for `{lang_code}` have been etched into the grove’s stones.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["rollehinzufügen", "ajouterrôle", "agregarrol"])
@commands.has_permissions(administrator=True)
async def addroleoption(ctx, role: discord.Role, emoji: str, *, label: str):
    guild_id = str(ctx.guild.id)

    # Ensure proper structure exists
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {"languages": {}, "role_options": {}, "users": {}}

    role_options = all_languages["guilds"][guild_id].setdefault("role_options", {})
    role_options[str(role.id)] = {"emoji": emoji, "label": label}

    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🌸 Role Added",
        description=f"Role `{label}` with emoji {emoji} is now selectable by newcomers.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)


@bot.command(aliases=["rollentfernen", "supprimerrôle", "eliminarrol"])
@commands.has_permissions(administrator=True)
async def removeroleoption(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)

    role_options = all_languages["guilds"].get(guild_id, {}).get("role_options", {})
    if str(role.id) not in role_options:
        await ctx.send("❗ That role is not in the current selection list.")
        return

    del role_options[str(role.id)]
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🗑️ Role Removed",
        description=f"Role `{role.name}` has been removed from the selection list.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)


@bot.command(aliases=["rollenliste", "listerôles", "listarroles"])
@commands.has_permissions(administrator=True)
async def listroleoptions(ctx):
    guild_id = str(ctx.guild.id)

    role_options = all_languages["guilds"].get(guild_id, {}).get("role_options", {})
    if not role_options:
        await ctx.send("📭 No roles are currently configured for selection.")
        return

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🌸 Selectable Roles",
        description="These are the roles members can choose after joining:",
        color=embed_color
    )
    embed.set_footer(text=footer)

    for role_id, data in role_options.items():
        role = ctx.guild.get_role(int(role_id))
        if role:
            embed.add_field(name=f"{data['emoji']} {data['label']}", value=f"<@&{role.id}>", inline=False)

    await ctx.send(embed=embed)

@bot.command(aliases=["Kosmetikhinzufügen", "ajouterrolecosmetique", "agregarrolcosmetico"])
@commands.has_permissions(administrator=True)
async def addcosmetic(ctx, role: discord.Role, emoji: str, *, label: str):
    guild_id = str(ctx.guild.id)

    config = all_languages["guilds"].setdefault(guild_id, {"languages": {}, "cosmetic_role_options": {}, "users": {}})
    cosmetic_roles = config.setdefault("cosmetic_role_options", {})
    cosmetic_roles[str(role.id)] = {"emoji": emoji, "label": label}

    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.purple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="✨ Cosmetic Role Added",
        description=f"Role `{label}` with emoji {emoji} is now a sparkly option.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)


@bot.command(aliases=["Kosmetikentfernen", "supprimerrolecosmetique", "eliminarrolcosmetico"])
@commands.has_permissions(administrator=True)
async def removecosmetic(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    cosmetic_roles = all_languages["guilds"].get(guild_id, {}).get("cosmetic_role_options", {})

    if str(role.id) not in cosmetic_roles:
        await ctx.send("❗ That cosmetic role is not currently configured.")
        return

    del cosmetic_roles[str(role.id)]
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.purple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🗑️ Cosmetic Role Removed",
        description=f"The role `{role.name}` has been removed from cosmetic options.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)


@bot.command(aliases=["Kosmetikliste", "listerolescosmetiques", "listarrolescosmeticos"])
@commands.has_permissions(administrator=True)
async def listcosmetics(ctx):
    guild_id = str(ctx.guild.id)
    cosmetic_roles = all_languages["guilds"].get(guild_id, {}).get("cosmetic_role_options", {})

    if not cosmetic_roles:
        await ctx.send("📭 No cosmetic roles are currently configured.")
        return

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.purple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="✨ Cosmetic Roles",
        description="These roles add flair without affecting permissions:",
        color=embed_color
    )
    embed.set_footer(text=footer)

    for role_id, data in cosmetic_roles.items():
        role = ctx.guild.get_role(int(role_id))
        if role:
            embed.add_field(
                name=f"{data['emoji']} {data['label']}",
                value=f"<@&{role.id}>",
                inline=False
            )

    await ctx.send(embed=embed)

@bot.command(aliases=["sprachliste", "listelangues", "listaridiomas"])
@commands.has_permissions(administrator=True)
async def listlanguages(ctx):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id, {})
    languages = guild_config.get("languages", {})

    if not languages:
        await ctx.send("❗ No languages configured for this server.")
        return

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🌍 Configured Languages",
        description="These are the whispering tongues your grove understands:",
        color=embed_color
    )
    embed.set_footer(text=footer)

    for code, data in languages.items():
        name = data.get("name", f"Unknown ({code})")
        embed.add_field(name=name, value=f"`{code}`", inline=True)

    await ctx.send(embed=embed)

@bot.command(aliases=["willkommenstart", "demarreraccueil", "iniciarbienvenida"])
@commands.has_permissions(administrator=True)
async def startwelcome(ctx, member: discord.Member):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)

    if not guild_config:
        await ctx.send("❗ This server hasn’t been configured for Whisperling yet.")
        return

    welcome_channel_id = guild_config.get("welcome_channel_id")
    if not welcome_channel_id:
        await ctx.send("❗ No welcome channel is set for this server.")
        return

    lang_map = guild_config.get("languages", {})
    if not lang_map:
        await ctx.send("❗ No languages are configured yet.")
        return

    channel = ctx.guild.get_channel(welcome_channel_id)
    if not channel:
        await ctx.send("❗ The configured welcome channel doesn’t exist or can’t be accessed.")
        return

    await send_language_selector(member, channel, lang_map, guild_config)
    await ctx.send(f"🌿 Manually started the welcome flow for {member.mention}.")

async def softly_remove_member(member, action="kick", interaction=None):
    guild = member.guild
    guild_id = str(guild.id)
    mode = guild_modes.get(guild_id, "dayform")

    mode_messages = {
        "dayform": {
            "kick": f"☀️ You have been removed from **{guild.name}**. Get some tea, and take your crackers elsewhere.",
            "ban": f"☀️ You have been permanently removed from **{guild.name}**. The Grove will not open to you again."
        },
        "nightform": {
            "kick": f"🌙 The night whispers you away from **{guild.name}**.",
            "ban": f"🌙 The stars forget your name. You are sealed away from **{guild.name}**."
        },
        "cosmosform": {
            "kick": f"🌌 You’ve drifted too far from **{guild.name}**.",
            "ban": f"🌌 You are lost beyond the furthest stars. **{guild.name}** will not call you back."
        },
        "seaform": {
            "kick": f"🌊 You’ve been swept from **{guild.name}** to calmer tides.",
            "ban": f"🌊 The depths close. **{guild.name}** will not see you resurface."
        },
        "hadesform": {
            "kick": f"🔥 You have been *politely yeeted* from **{guild.name}**.",
            "ban": f"🔥 The flames consume your path. **{guild.name}** is no longer yours to enter."
        },
        "forestform": {
            "kick": f"🍃 The Grove gently closes its branches around **{guild.name}**.",
            "ban": f"🍃 The roots reject you fully. You shall not return to **{guild.name}**."
        },
        "auroraform": {
            "kick": f"❄️ Your light fades softly from **{guild.name}**.",
            "ban": f"❄️ The aurora no longer glows for you. You are frozen outside **{guild.name}**."
        },
        "vernalglint": {
            "kick": f"🌸 Shoo shoo! You’ve been brushed from **{guild.name}**.",
            "ban": f"🌸 Spring blooms without you. **{guild.name}** will not open its petals again."
        },
        "fallveil": {
            "kick": f"🍁 You are gently sent away from **{guild.name}** to rest elsewhere.",
            "ban": f"🍁 The veil falls completely. **{guild.name}** will not reopen its warmth to you."
        },
        "sunfracture": {
            "kick": f"🔆 You’ve fractured from **{guild.name}**.",
            "ban": f"🔆 The Grove's light shatters and seals behind you. **{guild.name}** is closed."
        },
        "yuleshard": {
            "kick": f"❄️ You are frozen out of **{guild.name}**.",
            "ban": f"❄️ The crystalline breath seals you entirely. No thaw awaits you in **{guild.name}**."
        },
        "echovoid": {
            "kick": f"🕳️ You vanish quietly from **{guild.name}**.",
            "ban": f"🕳️ Even the echoes release you. **{guild.name}** forgets your shape entirely."
        },
        "glitchspire": {
            "kick": f"🧬 Your fragment was rejected from **{guild.name}**.",
            "ban": f"🧬 Your data is corrupted and purged. You are locked from **{guild.name}**."
        },
        "crepusca": {
            "kick": f"💫 You fade quietly from **{guild.name}** into dusk.",
            "ban": f"💫 The dusk seals behind you. The Grove no longer dreams of you in **{guild.name}**."
        },
        "flutterkin": {
            "kick": f"🤫 No more bouncy time in **{guild.name}** — bye bye now!",
            "ban": f"🤫 All the giggles stop. You can't come back to play in **{guild.name}**."
        }
    }

    public_messages = {
        "dayform": f"☀️ {member.mention} has been escorted gently from the Grove.",
        "nightform": f"🌙 A hush falls. {member.mention} is no longer among us.",
        "cosmosform": f"🌌 {member.mention} drifts into the distant void.",
        "seaform": f"🌊 {member.mention} has been swept beyond the Grove's tides.",
        "hadesform": f"🔥 The embers flash — {member.mention} is gone.",
        "forestform": f"🍃 The Grove closes around {member.mention}.",
        "auroraform": f"❄️ The lights dim for {member.mention}.",
        "vernalglint": f"🌸 {member.mention} has been shooed away from the Grove.",
        "fallveil": f"🍁 {member.mention} now rests far beyond the Grove's reach.",
        "sunfracture": f"🔆 {member.mention} fractures from the Grove.",
        "yuleshard": f"❄️ {member.mention} is frozen out of the Grove entirely.",
        "echovoid": f"🕳️ The echoes fade as {member.mention} vanishes.",
        "glitchspire": f"🧬 The code purges {member.mention} from existence.",
        "crepusca": f"💫 {member.mention} dissolves into the dreaming dusk.",
        "flutterkin": f"🤫 No more bouncy play for {member.mention} — bye bye~"
    }

    try:
        if action == "ban":
            await guild.ban(member, reason="Whisperling’s grove remains peaceful.")
        else:
            await guild.kick(member, reason="Whisperling’s grove remains peaceful.")

        # DM the user
        try:
            message = mode_messages.get(mode, {}).get(action, f"🍃 You have been removed from **{guild.name}**.")
            await member.send(message)
        except discord.Forbidden:
            print(f"DM failed for {member}.")

        # Public message (if slash interaction provided)
        if interaction:
            public_notice = public_messages.get(mode, f"🍃 {member.mention} has been removed.")
            await interaction.channel.send(public_notice)

    except discord.Forbidden:
        print(f"❗ Whisperling lacked permission to remove {member}.")

# SLASH KICK
@tree.command(
    name="kick",
    description="Politely remove someone from the grove."
)
@app_commands.describe(member="The member to kick")
@app_commands.default_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member):
    await softly_remove_member(member, action="kick", interaction=interaction)
    await interaction.response.send_message(f"🪶 {member.mention} has been politely shown the door.")

# SLASH BAN
@tree.command(
    name="ban",
    description="Permanently remove someone from the grove."
)
@app_commands.describe(member="The member to ban")
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member):
    await softly_remove_member(member, action="ban", interaction=interaction)
    await interaction.response.send_message(f"🪶 {member.mention} has been permanently banished from the grove.")

# ========== FLOW HELPERS ==========

async def send_language_selector(member, channel, lang_map, guild_config):
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")

    # 🎀 Flutterkin glitch chance
    if mode in STANDARD_MODES and random.random() < 0.04:
        previous_standard_mode_by_guild[guild_id] = mode
        guild_modes[guild_id] = "flutterkin"
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        mode = "flutterkin"

    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    intro_title = get_translated_mode_text(guild_id, user_id, mode, "language_intro_title", user=member.mention)
    intro_desc = get_translated_mode_text(guild_id, user_id, mode, "language_intro_desc", user=member.mention)

    class LanguageView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for code, data in lang_map.items():
                button = Button(label=data['name'], style=discord.ButtonStyle.primary, custom_id=code)
                self.add_item(button)
            cancel_button = Button(label="❌ Cancel", style=discord.ButtonStyle.danger, custom_id="cancel")
            self.add_item(cancel_button)

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                timeout_msg = get_translated_mode_text(
                    guild_id, user_id, mode, "timeout_language",
                    fallback=f"⏳ {member.mention} Time ran out for language selection.",
                    user=member.mention
                )
                await channel.send(timeout_msg)
            except Exception as e:
                print(f"Timeout error: {e}")

    async def handle_language(interaction: discord.Interaction):
        selected_code = interaction.data['custom_id']
        if selected_code == "cancel":
            await interaction.response.send_message("❌ Cancelled language selection.", ephemeral=True)
            view.stop()
            return

        if selected_code not in lang_map:
            await interaction.response.send_message("❗ Invalid language code.", ephemeral=True)
            return

        guild_config.setdefault("users", {})[user_id] = selected_code
        save_languages()

        confirm_title = get_translated_mode_text(guild_id, user_id, mode, "language_confirm_title", user=member.mention)
        confirm_desc = get_translated_mode_text(guild_id, user_id, mode, "language_confirm_desc", user=member.mention)
        confirm_embed = discord.Embed(title=confirm_title, description=confirm_desc, color=embed_color)
        await channel.send(content=member.mention, embed=confirm_embed)

        view.stop()

        await asyncio.sleep(2)

        # 🧚 Continue flow
        if guild_config.get("rules"):
            await send_rules_embed(member, channel, selected_code, lang_map, guild_config)
        else:
            await send_role_selector(member, channel, guild_config)

    view = LanguageView()

    # Assign callbacks after building view safely
    for item in view.children:
        if isinstance(item, Button):
            item.callback = handle_language

    embed = discord.Embed(title=intro_title, description=intro_desc, color=embed_color)
    await channel.send(content=member.mention, embed=embed, view=view)

async def send_rules_embed(member, channel, lang_code, lang_map, guild_config):
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.teal())

    # Pull rules text if configured, else fallback flavored message
    rules_text = guild_config.get("rules", {}).get(lang_code)
    if not rules_text:
        rules_text = get_translated_mode_text(
            guild_id, user_id, mode, "rules_none",
            fallback="📜 No rules have been set for this grove. Whisperling trusts your good heart, {user}."
        )

    class AcceptRulesView(View):
        def __init__(self):
            super().__init__(timeout=90)
            button = Button(
                label="✅ I Accept",
                style=discord.ButtonStyle.success,
                custom_id="accept_rules"
            )
            self.add_item(button)

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                timeout_msg = get_translated_mode_text(
                    guild_id, user_id, mode, "timeout_rules",
                    fallback=f"⏳ {member.mention} Time ran out to accept the rules.",
                    user=member.mention
                )
                await channel.send(timeout_msg)
            except Exception as e:
                print(f"Timeout error on rules: {e}")

    async def handle_accept(interaction: discord.Interaction):
        confirm_title = get_translated_mode_text(
            guild_id, user_id, mode, "rules_confirm_title", user=member.mention
        )
        confirm_desc = get_translated_mode_text(
            guild_id, user_id, mode, "rules_confirm_desc", user=member.mention
        )

        confirm_embed = discord.Embed(title=confirm_title, description=confirm_desc, color=embed_color)
        await channel.send(content=member.mention, embed=confirm_embed)

        view.stop()

        await asyncio.sleep(2)
        await send_role_selector(member, channel, guild_config)

    view = AcceptRulesView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = handle_accept

    embed = discord.Embed(
        title=get_translated_mode_text(guild_id, user_id, mode, "rules_intro_title", fallback="📜 Grove Guidelines"),
        description=rules_text,
        color=embed_color
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_role_selector(member, channel, guild_config):
    role_options = guild_config.get("role_options", {})

    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.gold())

    # 🌿 If no role options are configured, send graceful fallback
    if not role_options:
        fallback_desc = get_translated_mode_text(
            guild_id, user_id, mode, "role_none",
            fallback="✨ No roles have been configured for you to pick."
        )
        embed = discord.Embed(
            title="🎭 Roles",
            description=fallback_desc,
            color=embed_color
        )
        await channel.send(content=member.mention, embed=embed)
        await asyncio.sleep(1)

        # 🌸 Continue onward to cosmetics
        cosmetic_shown = await send_cosmetic_selector(member, channel, guild_config)
        if not cosmetic_shown:
            lang_code = all_languages["guilds"][guild_id]["users"].get(user_id, "en")
            lang_map = all_languages["guilds"][guild_id]["languages"]
            await send_final_welcome(member, channel, lang_code, lang_map)
        return

    # 🖐️ If roles exist, build the selector normally
    class RoleSelectView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in role_options.items():
                button = Button(
                    label=data['label'],
                    emoji=data['emoji'],
                    style=discord.ButtonStyle.primary,
                    custom_id=role_id
                )
                self.add_item(button)

        async def interaction_check(self, interaction: discord.Interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                timeout_msg = get_translated_mode_text(
                    guild_id, user_id, mode, "timeout_role",
                    fallback=f"⏳ {member.mention}, time ran out to choose a role.",
                    user=member.mention
                )
                await channel.send(timeout_msg)
            except Exception as e:
                print("⚠️ Timeout error (role selector):", e)

    async def role_button_callback(interaction: discord.Interaction):
        role_id = interaction.data['custom_id']
        role = member.guild.get_role(int(role_id))
        if role:
            try:
                await member.add_roles(role)
                role_msg = get_translated_mode_text(
                    guild_id, user_id, mode, "role_granted",
                    role=role.name, user=member.mention
                )
                await interaction.response.send_message(role_msg, ephemeral=True)
                view.stop()

                await asyncio.sleep(1)

                # 🌸 After role, attempt cosmetic selector
                cosmetic_shown = await send_cosmetic_selector(member, channel, guild_config)
                if not cosmetic_shown:
                    lang_code = all_languages["guilds"][guild_id]["users"].get(user_id, "en")
                    lang_map = all_languages["guilds"][guild_id]["languages"]
                    await send_final_welcome(member, channel, lang_code, lang_map)

            except Exception as e:
                print("⚠️ Role assign error:", e)
                await interaction.response.send_message(
                    "❗ I couldn’t assign that role. Please contact a mod.",
                    ephemeral=True
                )

    view = RoleSelectView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = role_button_callback

    embed = discord.Embed(
        title=get_translated_mode_text(guild_id, user_id, mode, "role_intro_title", user=member.mention),
        description=get_translated_mode_text(guild_id, user_id, mode, "role_intro_desc", user=member.mention),
        color=embed_color
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_cosmetic_selector(member, channel, guild_config):
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")
    lang_code = all_languages["guilds"][guild_id]["users"].get(user_id, "en")
    lang_map = all_languages["guilds"][guild_id]["languages"]
    cosmetic_options = guild_config.get("cosmetic_role_options", {})
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())

    # 🌿 Graceful fallback if no cosmetic options configured
    if not cosmetic_options:
        fallback_desc = get_translated_mode_text(
            guild_id, user_id, mode, "cosmetic_none",
            fallback="💎 No cosmetics have been configured. You shine just fine!"
        )
        embed = discord.Embed(
            title="💎 Cosmetic Sparkles",
            description=fallback_desc,
            color=embed_color
        )
        await channel.send(content=member.mention, embed=embed)
        await asyncio.sleep(1)
        await send_final_welcome(member, channel, lang_code, lang_map)
        return False  # Still return False for consistent flow handling

    class CosmeticRoleView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in cosmetic_options.items():
                button = Button(
                    label=data['label'],
                    emoji=data['emoji'],
                    style=discord.ButtonStyle.primary,
                    custom_id=role_id
                )
                self.add_item(button)

            skip_button = Button(
                label="Skip",
                style=discord.ButtonStyle.secondary,
                custom_id="skip_cosmetic"
            )
            self.add_item(skip_button)

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                timeout_msg = get_translated_mode_text(
                    guild_id, user_id, mode, "timeout_cosmetic",
                    fallback=f"⏳ {member.mention}, we didn’t see your sparkle. Come back when you’re ready to glow!",
                    user=member.mention
                )
                await channel.send(timeout_msg)
                await asyncio.sleep(1)
                await send_final_welcome(member, channel, lang_code, lang_map)
            except Exception as e:
                print("⚠️ Timeout error (cosmetic selector):", e)

    async def cosmetic_button_callback(interaction):
        selected = interaction.data["custom_id"]

        if selected == "skip_cosmetic":
            skip_msg = get_translated_mode_text(
                guild_id, user_id, mode, "cosmetic_skipped", user=member.mention
            )
            await interaction.response.send_message(skip_msg, ephemeral=True)
        else:
            role = member.guild.get_role(int(selected))
            if role:
                try:
                    await member.add_roles(role)
                    grant_msg = get_translated_mode_text(
                        guild_id, user_id, mode, "cosmetic_granted", role=role.name, user=member.mention
                    )
                    await interaction.response.send_message(grant_msg, ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message("❗ Couldn’t assign that sparkle.", ephemeral=True)
                    print("⚠️ Cosmetic role assign error:", e)

        view.stop()

        await asyncio.sleep(1)
        await send_final_welcome(member, channel, lang_code, lang_map)

    view = CosmeticRoleView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = cosmetic_button_callback

    embed = discord.Embed(
        title=get_translated_mode_text(guild_id, user_id, mode, "cosmetic_intro_title", user=member.mention),
        description=get_translated_mode_text(guild_id, user_id, mode, "cosmetic_intro_desc", user=member.mention),
        color=embed_color
    )

    await channel.send(content=member.mention, embed=embed, view=view)
    return True

async def send_final_welcome(member, channel, lang_code, lang_map):
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")

    # ✨ Pull translated welcome title
    welcome_title = get_translated_mode_text(
        guild_id, user_id, mode, "welcome_title", fallback="🌿 Welcome!"
    )

    # 💬 Pull custom welcome (guild-defined), fallback to mode-translated default
    admin_welcome = lang_map.get(lang_code, {}).get("welcome")
    if admin_welcome:
        welcome_desc = admin_welcome.replace("{user}", member.mention)
    else:
        welcome_desc = get_translated_mode_text(
            guild_id, user_id, mode, "welcome_desc",
            fallback="Welcome, {user}!", user=member.mention
        )

    # 🌿 Build embed with proper ID cast
    embed, file = build_whisperling_embed(str(guild_id), welcome_title, welcome_desc)

    if file:
        await channel.send(content=member.mention, embed=embed, file=file)
    else:
        await channel.send(content=member.mention, embed=embed)

# ========== FLUTTERKIN ==========

flutterkin_last_triggered = {}  # guild_id -> datetime

@bot.command(aliases=[
    "babywish", "sparkleshift", "fluttertime", "snacktime", "glitterpuff", "bloop", "peekaboo",
    "glitzerfee", "petitpapillon", "chispa", "nibnib", "piccolina", "snugglezap", "twinkleflit",
    "pünktchen", "shirokuma", "cocotín", "cucciolotta", "snuzzlepuff", "sparkleboop", "miniblossom"
])
async def whisper(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    now = datetime.now(timezone.utc)
    current_mode = guild_modes.get(guild_id, "dayform")

    # ⏳ Check/reset daily limit
    usage_data = flutterkin_usage_count_by_guild.get(guild_id)
    if not usage_data or now >= usage_data["reset_time"]:
        flutterkin_usage_count_by_guild[guild_id] = {
            "count": 0,
            "reset_time": now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        }
    elif usage_data["count"] >= 3 and current_mode != "flutterkin":
        await ctx.send("🍼 Flutterkin is all tuckered out... try again tomorrow!")
        return

    # 🌸 Activate Flutterkin mode
    if current_mode != "flutterkin":
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = "flutterkin"
        glitch_timestamps_by_guild[guild_id] = now
        await update_avatar_for_mode("flutterkin")
        flutterkin_usage_count_by_guild[guild_id]["count"] += 1

    # 🗓️ Update interaction trackers
    flutterkin_last_triggered[guild_id] = now
    last_interaction_by_guild[guild_id] = now

    # 🌼 Sparkle intro
    intro = get_translated_mode_text(
        guild_id, user_id, "flutterkin", "language_confirm_desc",
        user=ctx.author.mention
    )
    embed, file = build_whisperling_embed(
        guild_id, "✨ Bouncy Bloom Activated!", intro
    )

    if file:
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed)

    # 🌈 Translation if used as reply
    if ctx.message.reference:
        try:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            content = replied_msg.content

            if not content:
                await ctx.send("🧺 That message is empty... no words to sparkle~ ✨")
                return

            user_lang = get_user_language(guild_id, user_id)
            if not user_lang:
                await ctx.send("🤔 You haven’t chosen a language yet! Pick one first~ 🐞")
                return

            translated = translator.translate(content, dest=user_lang).text
            styled_translated = style_text(guild_id, translated)

            await ctx.send(f"💫 Sparkled up for you:\n> {styled_translated}")

        except Exception as e:
            print("⚠️ Flutterkin translation error:", e)
            await ctx.send("😥 Uh oh... Flutterkin stumbled. Try again in a moment?")

# ========== GENERAL COMMANDS ==========

async def build_help_embed(interaction_or_ctx):
    guild = interaction_or_ctx.guild
    guild_id = str(guild.id)

    # 🌒 Handle glitch logic if needed (only once, when first called)
    if isinstance(interaction_or_ctx, discord.Interaction):
        maybe_glitch = maybe_trigger_glitch(guild_id)
        current_mode = guild_modes.get(guild_id, "dayform")

        if maybe_glitch and current_mode in STANDARD_MODES:
            await apply_mode_change(guild, maybe_glitch)
            current_mode = maybe_glitch

        last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)
    else:
        # For non-interaction context (regular !help), skip glitch checks
        current_mode = guild_modes.get(guild_id, "dayform")

    embed_color = MODE_COLORS.get(current_mode, discord.Color.blurple())
    description = MODE_DESCRIPTIONS.get(current_mode, "Whisperling shimmers softly in the grove.")
    footer = MODE_FOOTERS.get(current_mode, "Whisperling watches the grove gently...")

    embed = discord.Embed(
        title="📖 Whisperling's Grimoire",
        description=description,
        color=embed_color
    )

    embed.add_field(
        name="🧚 Commands for Wanderers",
        value=(
            "`!translate` – Translate a replied message into your chosen language (auto-deletes)\n"
            "`?` – React with ❓ to translate a message to your DMs\n"
            "`!chooselanguage` – Pick or change your preferred language\n"
            "`!setmode` – Shift Whisperling into a different form\n"
            "`!formcompendium` – Browse Whisperling’s available forms\n"
            "`!... there is a hidden command ...` – If the winds allow, Flutterkin may awaken 🍼✨"
        ),
        inline=False
    )

    lang_map = all_languages["guilds"].get(guild_id, {}).get("languages", {})
    if lang_map:
        langs = [f"{data['name']}" for code, data in lang_map.items()]
        embed.add_field(
            name="🌍 Available Languages",
            value=", ".join(langs),
            inline=False
        )

    embed.set_footer(text=footer)
    return embed

@tree.command(name="help", description="📖 See the magical things Whisperling can do (for all users).")
async def help(interaction: discord.Interaction):
    embed = await build_help_embed(interaction)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="help")
async def help_command(ctx):
    embed = await build_help_embed(ctx)
    await ctx.send(embed=embed)

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if str(payload.emoji) != "❓":
        return  # Only respond to the ❓ emoji

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return  # Ignore bots

    channel = guild.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except Exception as e:
        print(f"❗ Failed to fetch message for translation: {e}")
        return

    content = message.content
    if not content:
        return

    guild_id = str(guild.id)
    user_id = str(member.id)
    user_lang = get_user_language(guild_id, user_id)
    if not user_lang:
        try:
            await channel.send(
                f"{member.mention} 🕊️ You haven’t chosen a language yet. Use `!chooselanguage` first!",
                delete_after=10
            )
        except:
            pass
        return

    # 🌒 Handle potential glitch trigger
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes.get(guild_id, "dayform")

    if maybe_glitch and current_mode in STANDARD_MODES:
        await apply_mode_change(guild, maybe_glitch)
        current_mode = maybe_glitch  # <-- Refresh mode after glitch

    # 🕰️ Update interaction timestamp
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    try:
        result = translator.translate(content, dest=user_lang)
        styled_output = style_text(guild_id, result.text)

        embed_color = MODE_COLORS.get(current_mode, discord.Color.blurple())
        footer = MODE_FOOTERS.get(current_mode, "")

        embed = discord.Embed(
            title=f"❓ Whispered Translation to `{user_lang}`",
            description=f"> {styled_output}",
            color=embed_color
        )
        if footer:
            embed.set_footer(text=footer)

        # Send as ephemeral via DM
        await member.send(embed=embed)

    except Exception as e:
        print("Translation error (reaction):", e)
        try:
            await channel.send(f"{member.mention} ❗ Something went wrong with the translation.", delete_after=10)
        except:
            pass

@bot.command(aliases=["übersetzen", "traduire", "traducir"])
async def translate(ctx):
    # 💬 Delete the command message after 60s regardless
    try:
        await ctx.message.delete(delay=60)
    except discord.Forbidden:
        print("❗ Missing permission to delete the user's !translate command.")

    if not ctx.message.reference:
        await ctx.send("🌸 Please reply to the message you want translated.", delete_after=10)
        return

    try:
        original_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        content = original_msg.content
        if not content:
            await ctx.send("🧺 That message carries no words to whisper.", delete_after=10)
            return
    except Exception as e:
        print("Fetch error:", e)
        await ctx.send("❗ I couldn’t find the message you replied to.", delete_after=10)
        return

    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    user_lang = get_user_language(guild_id, user_id)

    if not user_lang:
        await ctx.send("🕊️ You haven’t chosen a language yet, gentle one.", delete_after=10)
        return

    # 🌒 Handle potential glitch trigger
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes.get(guild_id, "dayform")

    if maybe_glitch and current_mode in STANDARD_MODES:
        await apply_mode_change(ctx.guild, maybe_glitch)
        current_mode = maybe_glitch  # <-- Update after glitch

    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    try:
        result = translator.translate(content, dest=user_lang)
        styled_output = style_text(guild_id, result.text)

        embed_color = MODE_COLORS.get(current_mode, discord.Color.blurple())
        footer = MODE_FOOTERS.get(current_mode, "")

        embed = discord.Embed(
            title=f"✨ Whispered Translation to `{user_lang}`",
            description=f"> {styled_output}",
            color=embed_color
        )
        if footer:
            embed.set_footer(text=footer)

        await ctx.send(embed=embed, delete_after=60)

    except Exception as e:
        print("Translation error:", e)
        await ctx.send("❗ The winds failed to carry the words. Please try again.", delete_after=10)

@bot.command(aliases=["wählesprache", "choisirlalangue", "eligelenguaje"])
async def chooselanguage(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    member = ctx.author
    guild_config = all_languages["guilds"].get(guild_id)

    # 🌒 Handle potential glitch trigger
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes.get(guild_id, "dayform")

    if maybe_glitch and current_mode in STANDARD_MODES:
        await apply_mode_change(ctx.guild, maybe_glitch)
        current_mode = maybe_glitch  # update mode for embed theming

    # 🌿 Update last interaction timestamp
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    if not guild_config:
        return await ctx.send("❗ This server isn't set up for Whisperling yet.")

    welcome_channel_id = guild_config.get("welcome_channel_id")
    if not welcome_channel_id:
        return await ctx.send("❗ No welcome channel has been set for this server.")

    if ctx.channel.id != welcome_channel_id:
        return await ctx.send(
            f"🌸 Please use this command in the <#{welcome_channel_id}> channel where fairy winds can guide it."
        )

    lang_map = guild_config.get("languages", {})
    if not lang_map:
        return await ctx.send("❗ No languages are configured yet.")

    embed_color = MODE_COLORS.get(current_mode, discord.Color.purple())
    voice = MODE_TEXTS_ENGLISH.get(current_mode, {})

    embed = discord.Embed(
        title=voice.get("language_intro_title", "🧚 Choose Your Whispering Tongue"),
        description=voice.get("language_intro_desc", "").replace("{user}", member.mention),
        color=embed_color
    )

    class LanguageView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for code, data in lang_map.items():
                self.add_item(Button(label=data['name'], custom_id=code, style=discord.ButtonStyle.primary))
            self.add_item(Button(label="❌ Cancel", style=discord.ButtonStyle.danger, custom_id="cancel"))

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                await message.edit(content="⏳ Time ran out for language selection.", embed=None, view=None)
            except:
                pass

    async def button_callback(interaction):
        selected_code = interaction.data['custom_id']
        if selected_code == "cancel":
            await interaction.response.edit_message(content="❌ Cancelled.", embed=None, view=None)
            return

        if "users" not in guild_config:
            guild_config["users"] = {}

        guild_config["users"][user_id] = selected_code
        save_languages()

        lang_name = lang_map[selected_code]["name"]
        await interaction.response.edit_message(
            content=f"✨ Your whisper has been tuned to **{lang_name}**.", embed=None, view=None
        )

    view = LanguageView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = button_callback

    message = await ctx.send(embed=embed, view=view)

@bot.command(aliases=["sprachenkürzel", "codeslangues", "codigosidioma"])
async def langcodes(ctx):
    guild_id = str(ctx.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "🌍 Whisperling is fluent in many tongues...")

    codes = {
        "en": "English 🌐",
        "de": "Deutsch 🇩🇪",
        "fr": "Français 🇫🇷",
        "es": "Español 🇪🇸",
        "it": "Italiano 🇮🇹",
        "nl": "Nederlands 🇳🇱",
        "pt": "Português 🇵🇹",
        "ru": "Русский 🇷🇺",
        "ja": "日本語 🇯🇵",
        "zh-cn": "中文 (Simplified) 🇨🇳",
        "pl": "Polski 🇵🇱",
        "tr": "Türkçe 🇹🇷"
    }

    embed = discord.Embed(
        title="📚 Whisperling’s Language Codes",
        description="Use these with `!translate` or for admin language setup commands.\n\n"
                    "[🌐 Full list of supported codes (Google Translate)](https://cloud.google.com/translate/docs/languages)",
        color=embed_color
    )

    for code, name in codes.items():
        embed.add_field(name=f"`{code}`", value=name, inline=True)

    embed.set_footer(text=footer)
    await ctx.send(embed=embed)

bot.run(TOKEN)
