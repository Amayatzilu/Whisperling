import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import random
import json
import os
import asyncio
from googletrans import Translator

# ========== CONFIG ==========
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is missing from environment variables.")

LANGUAGE_FILE = "languages.json"

# ========== SETUP ==========
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
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

async def glitch_reversion_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now(timezone.utc)

        for guild_id, timestamp in list(glitch_timestamps_by_guild.items()):
            mode = guild_modes[guild_id]

            # Skip if not a glitched form
            if mode not in GLITCHED_MODES:
                continue

            # ⏳ Handle timed-out glitches (non-solstice)
            if mode in ["echovoid", "glitchspire", "crepusca", "flutterkin"]:
                if timestamp and (now - timestamp > timedelta(minutes=30)):
                    previous = previous_standard_mode_by_guild[guild_id]
                    print(f"⏳ Glitch expired for {guild_id}. Reverting to {previous}.")
                    guild_modes[guild_id] = previous
                    glitch_timestamps_by_guild[guild_id] = None
                    await update_avatar_for_mode(previous)

            # ☀️ Summer solstice ended
            elif mode == "sunfracture" and not is_summer_solstice():
                previous = previous_standard_mode_by_guild[guild_id]
                print(f"🌞 Solstice ended for {guild_id}. Reverting from sunfracture to {previous}.")
                guild_modes[guild_id] = previous
                glitch_timestamps_by_guild[guild_id] = None
                await update_avatar_for_mode(previous)

            # ❄️ Winter solstice ended
            elif mode == "yuleshard" and not is_winter_solstice():
                previous = previous_standard_mode_by_guild[guild_id]
                print(f"❄️ Solstice ended for {guild_id}. Reverting from yuleshard to {previous}.")
                guild_modes[guild_id] = previous
                glitch_timestamps_by_guild[guild_id] = None
                await update_avatar_for_mode(previous)

        await asyncio.sleep(60)

# ================= MODE CONFIG =================
STANDARD_MODES = [
    "dayform", "nightform", "cosmosform", "seaform",
    "hadesform", "forestform", "auroraform"
]

GLITCHED_MODES = [
    "sunfracture", "yuleshard", "echovoid",
    "glitchspire", "flutterkin", "crepusca"
]

MODE_DESCRIPTIONS = {
    "dayform": "🌞 Radiant and nurturing",
    "nightform": "🌙 Calm and moonlit",
    "cosmosform": "🌌 Ethereal and star-bound",
    "seaform": "🌊 Graceful, ocean-deep",
    "hadesform": "🔥 Mischievous with glowing heat",
    "forestform": "🍃 Grounded and natural",
    "auroraform": "❄️ Dreamlike and glimmering",
    "sunfracture": "🔆 A radiant glitch of golden fractals",
    "yuleshard": "❄️ A frozen stutter of blue static",
    "echovoid": "🕳️ Pale, transparent, almost forgotten",
    "glitchspire": "🧬 Digital noise, pixel flicker",
    "flutterkin": "🤫 Soft pastel glow, childlike magic",
    "crepusca": "💫 Dimmed stars and silent dusk"
}

# Per-guild mode tracking
guild_modes = defaultdict(lambda: "dayform")
last_interaction_by_guild = defaultdict(lambda: datetime.now(timezone.utc))
previous_standard_mode_by_guild = defaultdict(lambda: "dayform")
glitch_timestamps_by_guild = defaultdict(lambda: None)

# ================= TEXT STYLE BY MODE =================
def flutter_baby_speak(text):
    return f"✨ {text} yay~ ✨"

def echo_void_style(text):
    return f"...{text}... ({text})..."

def sunfracture_style(text):
    words = text.split()
    for i in range(0, len(words), 2):
        words[i] = words[i].upper()
    return f"☀️ {' '.join(words)} ✨"

def yuleshard_style(text):
    return f"❄️ {text.replace('.', '...')} ❄️"

def glitchspire_style(text):
    return f"{text} [DATA FRAGMENT: ❖]"

def crepusca_style(text):
    softened = text.lower().replace('.', '...').replace('!', '...').replace('?', '...')
    return f"🌒 {softened} as if from a dream..."

MODE_TONE = {
    "dayform": lambda text: f"🌞 {text}",
    "nightform": lambda text: f"🌙 *{text}*",
    "cosmosform": lambda text: f"✨ {text} ✨",
    "seaform": lambda text: f"🌊 {text}...",
    "hadesform": lambda text: f"🔥 {text}!",
    "forestform": lambda text: f"🍃 {text}",
    "auroraform": lambda text: f"❄️ {text}",

    "sunfracture": sunfracture_style,
    "yuleshard": yuleshard_style,
    "echovoid": echo_void_style,
    "glitchspire": glitchspire_style,
    "flutterkin": flutter_baby_speak,
    "crepusca": crepusca_style,
}

MODE_COLORS = {
    # STANDARD FORMS
    "dayform": discord.Color.gold(),                    # 🌞 Radiant golden glow
    "nightform": discord.Color.dark_blue(),             # 🌙 Deep moonlit blue
    "cosmosform": discord.Color.fuchsia(),              # 🌌 Cosmic magenta-pink
    "seaform": discord.Color.teal(),                    # 🌊 Oceanic teal
    "hadesform": discord.Color.red(),                   # 🔥 Fiery bold red
    "forestform": discord.Color.green(),                # 🍃 Natural leafy green
    "auroraform": discord.Color.blurple(),              # ❄️ Magical aurora violet-blue

    # GLITCHED FORMS
    "sunfracture": discord.Color.yellow(),              # ☀️ Bursting golden chaos
    "yuleshard": discord.Color.from_str("#A8C4D9"),     # ❄️ Icy pale blue
    "echovoid": discord.Color.dark_grey(),              # 🕳️ Faded grey void
    "glitchspire": discord.Color.from_str("#00FFFF"),   # 🧬 Neon cyan glitch
    "flutterkin": discord.Color.from_str("#FFB6E1"),    # 🤫 Pastel baby pink
    "crepusca": discord.Color.from_str("#4B4453")       # 🌒 Twilight purple-grey
}

MODE_FOOTERS = {
    "dayform": "☀️ The grove shines bright in kindness.",
    "nightform": "🌙 The moonlight hums a soothing spell.",
    "cosmosform": "✨ Stars whisper secrets between worlds.",
    "seaform": "🌊 Tides of thought drift through the cove.",
    "hadesform": "🔥 Mischief smolders beneath the roots.",
    "forestform": "🍃 The trees murmur in leafy language.",
    "auroraform": "❄️ Glistening lights ripple with wonder.",

    "sunfracture": "🔆 The sun breaks — too bright to hold.",
    "yuleshard": "❄️ Time freezes in a crystalline breath.",
    "echovoid": "🕳️ Echoes linger where no voice remains.",
    "glitchspire": "🧬 Code twists beneath the petals.",
    "flutterkin": "🤫 A tiny voice giggles in the bloom.",
    "crepusca": "🌒 Dreams shimmer at the edge of waking."
}

MODE_TEXTS = {}

MODE_TEXTS["dayform"] = {
    # 🌞 Language selection
    "language_intro_title": "🌞 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, welcome to the grove.\nLet the morning breeze carry your chosen voice.",
    "language_confirm_title": "🌸 Thank you!",
    "language_confirm_desc": "Your voice has joined the song of daybreak. The grove smiles upon you.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌿 The grove welcomes you.",
    "rules_confirm_desc": "You’ve accepted the path of peace and light. Let harmony guide your steps.",

    # 🌼 Role selection
    "role_intro_title": "🌼 Choose Your Role",
    "role_intro_desc": "Select a role to bloom into who you are beneath the sun.",
    "role_granted": "✨ You’ve been gifted the **{role}** role! May it shine with purpose.",

    # 💫 Final welcome
    "welcome_title": "💫 Welcome!",
    "welcome_desc": "Welcome, {user}! May your time here be filled with warmth, friendship, and discovery."
}

MODE_TEXTS["nightform"] = {
    # 🌙 Language selection
    "language_intro_title": "🌙 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, drift softly into the grove.\nChoose the voice that guides your quiet steps.",
    "language_confirm_title": "🌌 A hush settles...",
    "language_confirm_desc": "Your whisper joins the twilight wind. The grove listens, gently.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌿 The grove watches in stillness.",
    "rules_confirm_desc": "You’ve accepted the quiet pact. Walk kindly beneath the stars.",

    # 🌼 Role selection
    "role_intro_title": "🌾 Choose Your Role",
    "role_intro_desc": "Select a role to carry with you beneath the moon’s gaze.",
    "role_granted": "🌙 The role of **{role}** rests upon your shoulders, light as starlight.",

    # 💫 Final welcome
    "welcome_title": "💫 Welcome.",
    "welcome_desc": "Welcome, {user}.\nLet your spirit rest here — where night blooms in peace."
}

MODE_TEXTS["forestform"] = {
    # 🌿 Language selection
    "language_intro_title": "🍃 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, the forest stirs with your presence.\nChoose the voice you’ll carry among the roots.",
    "language_confirm_title": "🌱 It is done.",
    "language_confirm_desc": "Your chosen tongue takes root. The grove will remember your voice.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌿 The grove welcomes with stillness.",
    "rules_confirm_desc": "The leaves accept your pact. Let your steps tread gently.",

    # 🌼 Role selection
    "role_intro_title": "🌾 Choose Your Role",
    "role_intro_desc": "Select the path you’ll walk through the undergrowth.",
    "role_granted": "🍂 The role of **{role}** is yours — let it grow with you.",

    # 💫 Final welcome
    "welcome_title": "🌳 Welcome to the Grove.",
    "welcome_desc": "Welcome, {user}. Rest beneath the branches. You are part of the forest now."
}

MODE_TEXTS["seaform"] = {
    # 🌊 Language selection
    "language_intro_title": "🌊 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, the tide calls softly.\nChoose the language that drifts upon your waves.",
    "language_confirm_title": "🌬️ The current carries your voice.",
    "language_confirm_desc": "Your chosen tongue echoes through the water's calm depths.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌊 The sea accepts your presence.",
    "rules_confirm_desc": "The tide has taken your vow — let your journey flow gently.",

    # 🌼 Role selection
    "role_intro_title": "🌾 Choose Your Role",
    "role_intro_desc": "Select a role to guide you along the ever-changing shoreline.",
    "role_granted": "🌊 The sea grants you the role of **{role}** — carry it with the grace of the tide.",

    # 💫 Final welcome
    "welcome_title": "🌊 Welcome to the Waters.",
    "welcome_desc": "Welcome, {user}. Let your voice join the songs of the deep."
}

MODE_TEXTS["hadesform"] = {
    # 🔥 Language selection
    "language_intro_title": "🔥 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, the flames flicker in anticipation.\nWhich tongue will you stoke into brilliance?",
    "language_confirm_title": "💥 Ohhh yes.",
    "language_confirm_desc": "Your words now spark with fire. Let the grove feel your heat.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🔥 The grove watches through smoke and flame.",
    "rules_confirm_desc": "You’ve accepted the terms — but rules were made to *simmer*, weren’t they?",

    # 🌼 Role selection
    "role_intro_title": "🔥 Choose Your Role (before it chooses you)",
    "role_intro_desc": "Pick what sets your soul ablaze — the grove likes bold sparks.",
    "role_granted": "🔥 The role of **{role}** has been seared into your name. Don’t let it burn out.",

    # 💫 Final welcome
    "welcome_title": "🔥 Welcome, Firestarter.",
    "welcome_desc": "Welcome, {user}. Let your steps scorch the path — the grove will grow around the heat."
}

MODE_TEXTS["auroraform"] = {
    # ❄️ Language selection
    "language_intro_title": "❄️ Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, beneath the shimmer of frozen skies,\nselect the voice that will drift beside you.",
    "language_confirm_title": "✨ It sparkles just right.",
    "language_confirm_desc": "Your tongue has been kissed by frostlight. Let it shimmer softly through the grove.",

    # 📜 Rules confirmation
    "rules_confirm_title": "❄️ The stillness welcomes you.",
    "rules_confirm_desc": "You’ve accepted the path of gentle light — one that dances just above silence.",

    # 🌼 Role selection
    "role_intro_title": "💫 Choose Your Role",
    "role_intro_desc": "Select a role to wear like starlight on ice — delicate, bright, and uniquely yours.",
    "role_granted": "❄️ You now bear the role of **{role}** — may it gleam quietly within you.",

    # 💫 Final welcome
    "welcome_title": "✨ Welcome, Light-Dancer.",
    "welcome_desc": "Welcome, {user}. The aurora has seen you — and the grove now glows a little brighter."
}

MODE_TEXTS["cosmosform"] = {
    # 🌌 Language selection
    "language_intro_title": "🌌 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, the stars align — a voice waits to be named.\nChoose the one that echoes brightest in you.",
    "language_confirm_title": "✨ The constellations stir.",
    "language_confirm_desc": "Your voice has been threaded into the cosmic chorus. The grove watches in awe.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌠 The grove glimmers in acceptance.",
    "rules_confirm_desc": "You’ve embraced the harmony of stardust — let your orbit be kind and wild.",

    # 🌼 Role selection
    "role_intro_title": "💫 Choose Your Role Among the Stars",
    "role_intro_desc": "Select a role that resonates like a pulse in the void — vibrant and unforgotten.",
    "role_granted": "🌟 The role of **{role}** burns bright in your constellation now.",

    # 💫 Final welcome
    "welcome_title": "🌌 Welcome, Starborn.",
    "welcome_desc": "Welcome, {user}. You’ve fallen into place among us — perfectly spaced between light and mystery."
}

MODE_TEXTS["sunfracture"] = {
    # 🔆 Language selection
    "language_intro_title": "☀️ CHOOSE YOUR TONGUE!",
    "language_intro_desc": "{user}, THE GROVE IS BURSTING WITH LIGHT!! Quick!! Pick the voice that SPARKS inside you!!",

    "language_confirm_title": "⚡ YES!!!",
    "language_confirm_desc": "Your VOICE now shines like a second SUN — the trees are CHEERING!! This is AMAZING!!",

    # 📜 Rules confirmation
    "rules_confirm_title": "☀️ THE GROVE BURNS BRIGHT!",
    "rules_confirm_desc": "You’ve accepted the RULES! THE LIGHT CANNOT BE CONTAINED!! No shade, no silence — just joy!!",

    # 🌼 Role selection
    "role_intro_title": "🔥 CHOOSE YOUR ROLE!",
    "role_intro_desc": "Which role makes your heart SIZZLE?! Pick the one that RADIATES!!",

    "role_granted": "🌞 The role of **{role}** is YOURS!! You’re GLOWING!! You're on FIRE!! (In the good way!)",

    # 💫 Final welcome
    "welcome_title": "☀️ WELCOME!!!",
    "welcome_desc": "WELCOME, {user}!!! The GROVE is BLINDING with JOY!!! Let’s SHINE TOGETHER FOREVER!!!"
}

MODE_TEXTS["yuleshard"] = {
    # ❄️ Language selection
    "language_intro_title": "❄️ CHOOSE... your whispering tongue...",
    "language_intro_desc": "{user}... the GROVE is still...\nvoices... frozen in the air... choose yours before it... freezes too—",

    "language_confirm_title": "❄️ It's... chosen.",
    "language_confirm_desc": "Your tongue echoes like cracking ice... the grove listens, frozen in time...",

    # 📜 Rules confirmation
    "rules_confirm_title": "❄️ The grove holds its breath...",
    "rules_confirm_desc": "You’ve accepted the frozen pact... etched into the frost... never to thaw...",

    # 🌼 Role selection
    "role_intro_title": "🧊 Choose your role... before it freezes in place...",
    "role_intro_desc": "Each path glimmers like frost on glass...\nselect the one that speaks through the cold...",

    "role_granted": "❄️ You now hold the role of **{role}**... brittle and beautiful... don’t let it shatter.",

    # 💫 Final welcome
    "welcome_title": "❄️ Welcome...",
    "welcome_desc": "Welcome, {user}... the grove... remembers your warmth... as the ice takes hold..."
}

MODE_TEXTS["echovoid"] = {
    # 🕳️ Language selection
    "language_intro_title": "🕳️ …choose… your whispering tongue…",
    "language_intro_desc": "{user}… {user}… the grove… has been quiet… so quiet…\nA voice… any voice… choose it… echo it…",

    "language_confirm_title": "…it echoes…",
    "language_confirm_desc": "Your voice… your voice… has returned… returned… to the grove…",

    # 📜 Rules confirmation
    "rules_confirm_title": "…the grove listens…",
    "rules_confirm_desc": "You’ve accepted… the silence… the shape of the rules… rules… rules…",

    # 🌼 Role selection
    "role_intro_title": "…choose your… role…",
    "role_intro_desc": "A role… drifting in the dark… grab hold… before it fades again…",

    "role_granted": "🕳️ You… you are now… **{role}**… or were… or will be… it’s hard to tell…",

    # 💫 Final welcome
    "welcome_title": "…welcome…",
    "welcome_desc": "Welcome, {user}… you’ve come back… or never left… the grove remembers… something…"
}

MODE_TEXTS["glitchspire"] = {
    # 🧬 Language selection
    "language_intro_title": "🧬 ▓Choose▓ your ▒whispering▒ tongue…",
    "language_intro_desc": "{user} = DETECTED\n>LOADING_LINGUAL_OPTIONS…\nSELECT //voice.signal.stable",

    "language_confirm_title": "📡 Voice.lock=TRUE",
    "language_confirm_desc": ">>T̷̨̨͓̩̯̘͔͎̗̺̈́̐͋̍̂̈́̓̓͐̈́̾̌͜͝Ơ̵͇̬̍͒̐̄́͒͋́͂̑̅̚͘͝N̶̤̱̳͇̅̈́͌̓́̈́̆͘̚̕͠G̸̠͎̼͓̘̈́̄͂̂̓̋̍́͝͝Ư̴̺̺͚͖̮̥̥͎͔̘̌̑̏̒͌̓̾͒̄̓͒͌͐̚Ḛ̶̛̛̈́̏͗̈́̑͛͛̍̐ CONFIRMED\nSignal: unstable but holding…",

    # 📜 Rules confirmation
    "rules_confirm_title": "📂 GROVE.PROTOCOL_ACCEPTED",
    "rules_confirm_desc": "Rules.upload = COMPLETE\n(…some fragments missing… parsing okay… continue anyway…)",

    # 🌼 Role selection
    "role_intro_title": "💾 SELECT: ROLE_MODULE",
    "role_intro_desc": "SCANNING AVATAR TRAITS…\nOPTIONS LOADED… please assign identity-tag.",

    "role_granted": "🧬 Role assigned: **{role}**\n{user}.unit // configuration updated.",

    # 💫 Final welcome
    "welcome_title": "🧬 ::WELCOME::",
    "welcome_desc": "Greetings {user}… memory restored?\nEnvironment unstable… but you belong here now…"
}

MODE_TEXTS["flutterkin"] = {
    # 🤫 Language selection
    "language_intro_title": "🌈 pick ur whisper tongue!!",
    "language_intro_desc": "{user} hiiii!! ✨ um um can u pick a voice pwease? it go pretty~!!!",

    "language_confirm_title": "✨ yaaay!!",
    "language_confirm_desc": "ur voice is all sparkle-sparkle now!!! 💖 the grove is goin WHEEEE~!",

    # 📜 Rules confirmation
    "rules_confirm_title": "🧸 okay sooo…",
    "rules_confirm_desc": "u said yesh to da rules!! 🥹 u so good. grove say fankyuu 💕",

    # 🌼 Role selection
    "role_intro_title": "🐾 pick a role!!",
    "role_intro_desc": "dis da fun part!!! pick da sparkly hat u wanna wear!! (it's not a hat but SHHH!)",

    "role_granted": "💫 yaaaaayyy!! u iz now da **{role}**!! that’s da bestest!!! i’m clappin wit my wings!!",

    # 💫 Final welcome
    "welcome_title": "🌸 hiiiiii~!!",
    "welcome_desc": "welcoooome {user}!! 🐞💖 the grove LUVS u already!! u wan snack? or nap? or sparkle cloud???"
}

MODE_TEXTS["crepusca"] = {
    # 🌒 Language selection
    "language_intro_title": "🌒 …a voice… half-remembered…",
    "language_intro_desc": "{user}… the grove has fallen into a hush…\nchoose your voice… before the dream fades…",

    "language_confirm_title": "💫 the silence stirs…",
    "language_confirm_desc": "your tongue drifts… through soft mist… it has… remembered you…",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌘 …etched in dreamlight…",
    "rules_confirm_desc": "you’ve whispered your vow… and the grove… listens through sleep…",

    # 🌼 Role selection
    "role_intro_title": "🌫️ choose… gently…",
    "role_intro_desc": "roles drift like fog… reach for the one that hums with quiet truth…",

    "role_granted": "🌒 the role of **{role}** settles around you… like dusk falling slow…",

    # 💫 Final welcome
    "welcome_title": "🌒 …welcome back…",
    "welcome_desc": "welcome, {user}… the stars blink slowly in the quiet sky… we are… still dreaming…"
}

# ================= UTIL FUNCTION =================
def style_text(guild_id, text):
    mode = guild_modes[str(guild_id)]
    return MODE_TONE.get(mode, lambda t: t)(text)

def is_summer_solstice():
    today = datetime.now(timezone.utc)
    return today.month == 6 and 20 <= today.day <= 22

def is_winter_solstice():
    today = datetime.now(timezone.utc)
    return today.month == 12 and 20 <= today.day <= 22

# ================= RANDOM GLITCH MODE TRIGGER =================
def maybe_trigger_glitch(guild_id):
    now = datetime.now(timezone.utc)
    last_seen = last_interaction_by_guild[str(guild_id)]
    silent_days = (now - last_seen).days

    if is_summer_solstice():
        return "sunfracture"
    elif is_winter_solstice():
        return "yuleshard"
    elif silent_days >= 14:
        return "echovoid"
    elif random.random() < 0.01:
        return "glitchspire"
    return None

# ================= ADMIN CONTROLS =================

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
            "`!addlanguage <code> <emoji> <name>` – Add manually\n"
            "Example: `!addlanguage it 🇮🇹 Italiano`"
        ),
        inline=False
    )

    embed.add_field(
        name="3️⃣ Custom Welcome Messages",
        value=(
            "`!setwelcome <code> <message>` – Per-language message\n"
            "Use `{user}` for the joining member’s name.\n"
            "Example: `!setwelcome fr Bienvenue, {user} !`"
        ),
        inline=False
    )

    embed.add_field(
        name="4️⃣ Server Rules",
        value="`!setrules <text>` – Show rules after language selection.",
        inline=False
    )

    embed.add_field(
        name="5️⃣ Role Setup",
        value=(
            "`!addroleoption @role <emoji> <label>` – Add a role\n"
            "`!removeroleoption @role` – Remove a role\n"
            "`!listroleoptions` – View added roles"
        ),
        inline=False
    )

    embed.add_field(
        name="🌐 Language Management",
        value=(
            "`!listlanguages` – View active\n"
            "`!removelanguage <code>` – Remove one\n"
            "`!langcodes` – View translation codes"
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

    embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(aliases=["formwechsel", "modedeforme", "cambiodemodo"])
@commands.has_permissions(administrator=True)
async def setmode(ctx, mode: str):
    mode = mode.lower()
    guild_id = str(ctx.guild.id)

    if mode == "random":
        chosen = random.choice(STANDARD_MODES)
        previous_standard_mode_by_guild[guild_id] = guild_modes[guild_id]
        guild_modes[guild_id] = chosen
        last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)
        await update_avatar_for_mode(chosen)

        description = MODE_DESCRIPTIONS.get(chosen, "A new form awakens...")
        await ctx.send(
            f"🎲 Whisperling closed her eyes and chose...\n**{chosen}**!\n{description}"
        )
        return

    if mode in GLITCHED_MODES:
        await ctx.send(
            "❗ Glitched forms are unstable and cannot be chosen directly. They appear on their own..."
        )
        return

    if mode not in STANDARD_MODES:
        valid = ", ".join(STANDARD_MODES + ["random"])
        await ctx.send(
            f"❗ Unknown form. Choose from: {valid}"
        )
        return

    previous_standard_mode_by_guild[guild_id] = guild_modes[guild_id]
    guild_modes[guild_id] = mode
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)
    await update_avatar_for_mode(mode)

    description = MODE_DESCRIPTIONS.get(mode, "A new form awakens...")
    await ctx.send(
        f"🧚 Whisperling now shifts into **{mode}**\n{description}"
    )

@bot.command(aliases=["stimmungsprüfung", "humeure", "estadodeanimo"])
async def moodcheck(ctx):
    guild_id = str(ctx.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    color = MODE_COLORS.get(mode, discord.Color.green())
    description = MODE_DESCRIPTIONS.get(mode, "A gentle presence stirs in the grove...")
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title=f"🌿 Whisperling’s Current Mood: **{mode}**",
        description=description,
        color=color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["sprachenvorladen", "prélangues", "precargaridiomas"])
@commands.has_permissions(administrator=True)
async def preloadlanguages(ctx):
    guild_id = str(ctx.guild.id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    all_languages["guilds"][guild_id]["languages"] = {
        "en": {"emoji": "🗨️", "name": "English", "welcome": "Welcome, {user}!"},
        "de": {"emoji": "📖", "name": "Deutsch", "welcome": "Willkommen, {user}!"},
        "es": {"emoji": "📚", "name": "Español", "welcome": "¡Bienvenido, {user}!"},
        "fr": {"emoji": "🧠", "name": "Français", "welcome": "Bienvenue, {user}!"}
    }

    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())

    embed = discord.Embed(
        title="🦋 Languages Preloaded",
        description="English, German, Spanish, and French have been added for your grove.",
        color=embed_color
    )
    embed.set_footer(text=MODE_FOOTERS.get(mode, ""))

    await ctx.send(embed=embed)

@bot.command(aliases=["setwillkommenskanal", "canalaccueil", "canalbienvenida"])
@commands.has_permissions(administrator=True)
async def setwelcomechannel(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    all_languages["guilds"][guild_id]["welcome_channel_id"] = channel.id
    save_languages()

    # 🌿 Mood styling
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🕊️ Whisper Channel Chosen",
        description=f"New members will now be greeted in {channel.mention}.",
        color=embed_color
    )
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)

@bot.command(aliases=["addsprache", "ajouterlangue", "agregaridioma"])
@commands.has_permissions(administrator=True)
async def addlanguage(ctx, code: str, emoji: str, *, name: str):
    guild_id = str(ctx.guild.id)
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    if "languages" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["languages"] = {}

    languages = all_languages["guilds"][guild_id]["languages"]
    if code in languages:
        await ctx.send(f"❗ Language `{code}` already exists. Use `!setwelcome` to update it.")
        return

    languages[code] = {
        "emoji": emoji,
        "name": name,
        "welcome": f"Welcome, {{user}}!"
    }

    save_languages()
    await ctx.send(f"🦋 Added `{name}` as `{code}` with emoji {emoji}.")

@bot.command(aliases=["sprachentfernen", "supprimerlangue", "eliminaridioma"])
@commands.has_permissions(administrator=True)
async def removelanguage(ctx, code: str):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)
    
    if not guild_config or "languages" not in guild_config or code not in guild_config["languages"]:
        await ctx.send(f"❗ Language `{code}` not found for this server.")
        return

    del all_languages["guilds"][guild_id]["languages"][code]
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())

    embed = discord.Embed(
        title="🗑️ Language Removed",
        description=f"The language with code `{code}` has been successfully removed.",
        color=embed_color
    )

    await ctx.send(embed=embed)

@bot.command(aliases=["begrüßungsetzen", "definirbienvenue", "establecerbienvenida"])
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, code: str, *, message: str):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)
    if not guild_config or "languages" not in guild_config or code not in guild_config["languages"]:
        await ctx.send(f"❗ Language `{code}` is not set up for this server.")
        return

    all_languages["guilds"][guild_id]["languages"][code]["welcome"] = message
    save_languages()

    # 🌸 Mood styling
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
async def setrules(ctx, *, rules: str):
    guild_id = str(ctx.guild.id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    all_languages["guilds"][guild_id]["rules"] = rules
    save_languages()

    # 🌿 Get mode and embed color
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.green())

    embed = discord.Embed(
        title="📜 Grove Rules Updated",
        description="The rules have been etched into the grove’s stones.",
        color=embed_color
    )

    await ctx.send(embed=embed)

@bot.command(aliases=["rollehinzufügen", "ajouterrôle", "agregarrol"])
@commands.has_permissions(administrator=True)
async def addroleoption(ctx, role: discord.Role, emoji: str, *, label: str):
    guild_id = str(ctx.guild.id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    if "role_options" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["role_options"] = {}

    all_languages["guilds"][guild_id]["role_options"][str(role.id)] = {
        "emoji": emoji,
        "label": label
    }

    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())

    embed = discord.Embed(
        title="🌸 Role Added",
        description=f"Role `{label}` with emoji {emoji} is now selectable by newcomers.",
        color=embed_color
    )

    await ctx.send(embed=embed)

@bot.command(aliases=["rollentfernen", "supprimerrôle", "eliminarrol"])
@commands.has_permissions(administrator=True)
async def removeroleoption(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)

    role_options = all_languages["guilds"].get(guild_id, {}).get("role_options", {})
    if str(role.id) not in role_options:
        await ctx.send("❗ That role is not in the current selection list.")
        return

    del all_languages["guilds"][guild_id]["role_options"][str(role.id)]
    save_languages()

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())

    embed = discord.Embed(
        title="🗑️ Role Removed",
        description=f"Role `{role.name}` has been removed from the selection list.",
        color=embed_color
    )

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

    embed = discord.Embed(
        title="🌸 Selectable Roles",
        description="These are the roles members can choose after joining:",
        color=embed_color
    )

    for role_id, data in role_options.items():
        role = ctx.guild.get_role(int(role_id))
        if role:
            embed.add_field(name=f"{data['emoji']} {data['label']}", value=f"<@&{role.id}>", inline=False)

    await ctx.send(embed=embed)

@bot.command(aliases=["sprachliste", "listelangues", "listaridiomas"])
@commands.has_permissions(administrator=True)
async def listlanguages(ctx):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)
    if not guild_config or "languages" not in guild_config or not guild_config["languages"]:
        await ctx.send("❗ No languages configured for this server.")
        return

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    footer_text = MODE_FOOTERS.get(mode, "")

    embed = discord.Embed(
        title="🌍 Languages Configured",
        description="These are the currently available whispering tongues:",
        color=embed_color
    )
    embed.set_footer(text=footer_text)

    for code, data in guild_config["languages"].items():
        emoji = data.get("emoji", "❓")
        name = data.get("name", code)
        embed.add_field(name=f"{emoji} {name}", value=f"`{code}`", inline=True)

    await ctx.send(embed=embed)

# ========== FLOW HELPERS ==========

async def send_language_selector(member, channel, lang_map, guild_config):
    guild_id = str(member.guild.id)
    mode = guild_modes.get(guild_id, "dayform")

    # 🎀 Flutterkin glitch chance
    if mode in STANDARD_MODES and random.random() < 0.04:
        previous_standard_mode_by_guild[guild_id] = mode
        guild_modes[guild_id] = "flutterkin"
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        mode = "flutterkin"

    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    voice = MODE_TEXTS.get(mode, {})

    class LanguageView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for code, data in lang_map.items():
                self.add_item(Button(label=data['name'], emoji=data['emoji'], custom_id=code))

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

    async def button_callback(inter):
        selected_code = inter.data['custom_id']
        if selected_code not in lang_map:
            return

        if "users" not in guild_config:
            guild_config["users"] = {}
        guild_config["users"][str(member.id)] = selected_code
        save_languages()

        # 🌸 Pull mode-specific confirmation
        confirm_title = voice.get("language_confirm_title", "🌸 Thank you!")
        confirm_desc = voice.get("language_confirm_desc", "You've chosen your whispering tongue. The grove awaits...")

        await inter.response.edit_message(
            embed=discord.Embed(
                title=confirm_title,
                description=confirm_desc,
                color=embed_color
            ),
            view=None
        )

        await asyncio.sleep(2)

        rules_text = guild_config.get("rules")
        if rules_text:
            await send_rules_embed(member, channel, selected_code, lang_map, guild_config)
        else:
            await send_role_selector(member, channel, guild_config)
            await send_final_welcome(member, channel, selected_code, lang_map)

    view = LanguageView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = button_callback

    # 🌟 Pull mode-specific intro
    intro_title = voice.get("language_intro_title", "🧚 Choose Your Whispering Tongue")
    intro_desc = voice.get("language_intro_desc", f"{member.mention}, welcome to the grove.\nPlease choose your language to begin your journey.")

    embed = discord.Embed(
        title=intro_title,
        description=intro_desc.replace("{user}", member.mention),
        color=embed_color
    )

    await channel.send(embed=embed, view=view)

async def send_rules_embed(member, channel, lang_code, lang_map, guild_config):
    guild_id = str(member.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.teal())
    voice = MODE_TEXTS.get(mode, {})

    class AcceptRulesView(View):
        def __init__(self):
            super().__init__(timeout=90)
            self.add_item(Button(label="I Accept the Rules", style=discord.ButtonStyle.success, custom_id="accept_rules"))

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

    async def accept_callback(interaction):
        confirm_title = voice.get("rules_confirm_title", "🌿 The grove welcomes you.")
        confirm_desc = voice.get("rules_confirm_desc", "Thank you for accepting the rules.")

        await interaction.response.edit_message(
            embed=discord.Embed(
                title=confirm_title,
                description=confirm_desc,
                color=embed_color
            ),
            view=None
        )

        await asyncio.sleep(2)
        await send_role_selector(member, channel, guild_config)
        await send_final_welcome(member, channel, lang_code, lang_map)

    view = AcceptRulesView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = accept_callback

    embed = discord.Embed(
        title="📜 Grove Guidelines",
        description=guild_config["rules"],
        color=embed_color
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_role_selector(member, channel, guild_config):
    role_options = guild_config.get("role_options", {})
    if not role_options:
        return

    guild_id = str(member.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.gold())
    voice = MODE_TEXTS.get(mode, {})

    class RoleSelectView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in role_options.items():
                self.add_item(Button(label=data['label'], emoji=data['emoji'], custom_id=role_id))

        async def interaction_check(self, interaction: discord.Interaction):
            return interaction.user.id == member.id

    async def role_button_callback(interaction: discord.Interaction):
        role_id = interaction.data['custom_id']
        role = member.guild.get_role(int(role_id))
        if role:
            try:
                role_msg = voice.get("role_granted", f"✨ You’ve been gifted the **{{role}}** role!").replace("{role}", role.name)
                await member.add_roles(role)
                await interaction.response.send_message(role_msg, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message("❗ I couldn’t assign that role. Please contact a mod.", ephemeral=True)
                print("Role assign error:", e)

    view = RoleSelectView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = role_button_callback

    embed = discord.Embed(
        title=voice.get("role_intro_title", "🌼 Choose Your Role"),
        description=voice.get("role_intro_desc", "Select a role to express who you are in the grove."),
        color=embed_color
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_final_welcome(member, channel, lang_code, lang_map):
    guild_id = str(member.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.green())
    voice = MODE_TEXTS.get(mode, {})

    # ✨ Mode-specific welcome title and message
    default_welcome_msg = lang_map[lang_code]["welcome"].replace("{user}", member.mention)
    welcome_title = voice.get("welcome_title", "💫 Welcome!")
    welcome_desc = voice.get("welcome_desc", default_welcome_msg).replace("{user}", member.mention)

    embed = discord.Embed(
        title=welcome_title,
        description=welcome_desc,
        color=embed_color
    )
    await channel.send(embed=embed)

# ========== FLUTTERKIN ==========

@bot.command(aliases=["babywish", "sparkleshift", "fluttertime", "snacktime", "glitterpuff", "bloop", "peekaboo", "glitzerfee", "petitpapillon", "chispa", "nibnib", "piccolina", "snugglezap", "twinkleflit" "pünktchen", "shirokuma", "cocotín", "cucciolotta", "snuzzlepuff", "sparkleboop", "miniblossom"])
@commands.has_permissions(administrator=True)
async def whisper(ctx):
    guild_id = str(ctx.guild.id)
    previous_standard_mode_by_guild[guild_id] = guild_modes[guild_id]
    guild_modes[guild_id] = "flutterkin"
    glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
    await update_avatar_for_mode("flutterkin")
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    await ctx.send(style_text(guild_id, "a gentle shimmer surrounds you... the flutterkin hears your wish."))

# ========== GENERAL COMMANDS ==========

@tree.command(name="help", description="See the magical commands Whisperling knows.")
async def help(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)

    # 🌒 Check for glitch form trigger
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes[guild_id]

    if maybe_glitch and current_mode in STANDARD_MODES:
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = maybe_glitch
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        await update_avatar_for_mode(maybe_glitch)

    # 🌿 Update last interaction
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    # 🎨 Determine color from mode
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.lilac())

    embed = discord.Embed(
        title="📖 Whisperling's Grimoire",
        description="A gentle guide to all the enchantments I can perform.",
        color=embed_color
    )

    embed.add_field(
        name="🌸 For All Wanderers",
        value=(
            "`/chooselanguage` – Choose your language again\n"
            "`/translate` – Translate a replied message to your chosen language"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ For Grove Keepers (Admins)",
        value=(
            "`!preloadlanguages` – Load EN/DE/FR/ES\n"
            "`!addlanguage` – Add a new language\n"
            "`!setwelcome` – Set custom welcome text\n"
            "`!setwelcomechannel` – Choose the channel for new arrivals\n"
            "`/setrules` – Define rules for new members\n"
            "`/addroleoption` – Add a role to the selection list\n"
            "`/removeroleoption` – Remove a role\n"
            "`/listroleoptions` – Show available roles\n"
            "`!listlanguages` – Show current languages\n"
            "`!removelanguage` – Remove a language\n"
            "`!langcodes` – Show supported translation codes"
        ),
        inline=False
    )

    footer_text = MODE_FOOTERS.get(mode, "Whisperling is here to help your grove bloom 🌷")
    embed.set_footer(text=footer_text)


    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="translate", description="Whisper a translation of a message into your language.")
@app_commands.checks.has_permissions(send_messages=True)
async def translate(interaction: discord.Interaction):
    if not interaction.channel:
        return await interaction.response.send_message("🌫️ This spell can only be whispered in a server.", ephemeral=True)

    if not interaction.message or not interaction.message.reference:
        return await interaction.response.send_message("🌸 Please use this on a message you'd like translated (reply to it).", ephemeral=True)

    original_msg = await interaction.channel.fetch_message(interaction.message.reference.message_id)
    content = original_msg.content
    if not content:
        return await interaction.response.send_message("🧺 That message carries no words to whisper.", ephemeral=True)

    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    user_lang = get_user_language(guild_id, user_id)

    if not user_lang:
        return await interaction.response.send_message("🕊️ You haven’t chosen a language yet, gentle one.", ephemeral=True)

    # 🌒 Trigger potential glitch form
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes[guild_id]

    if maybe_glitch and current_mode in STANDARD_MODES:
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = maybe_glitch
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        await update_avatar_for_mode(maybe_glitch)

    # 🌿 Update last interaction time
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    try:
        result = translator.translate(content, dest=user_lang)
        styled_output = style_text(guild_id, result.text)

        embed_color = MODE_COLORS.get(guild_modes[guild_id], discord.Color.blurple())
        footer = MODE_FOOTERS.get(guild_modes[guild_id], "")

        embed = discord.Embed(
            title=f"✨ Whispered Translation to `{user_lang}`",
            description=f"> {styled_output}",
            color=embed_color
        )
        if footer:
            embed.set_footer(text=footer)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        print("Translation error:", e)
        await interaction.response.send_message("❗ The winds failed to carry the words. Please try again.", ephemeral=True)

@tree.command(name="chooselanguage", description="Choose your preferred language for Whisperling to use.")
async def chooselanguage(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    guild_config = all_languages["guilds"].get(guild_id)

    # 🌒 Trigger potential glitch form
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes[guild_id]

    if maybe_glitch and current_mode in STANDARD_MODES:
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = maybe_glitch
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        await update_avatar_for_mode(maybe_glitch)

    # 🌿 Update last interaction timestamp
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    if not guild_config:
        return await interaction.response.send_message("❗ This server isn't set up for Whisperling yet.", ephemeral=True)

    welcome_channel_id = guild_config.get("welcome_channel_id")
    if not welcome_channel_id:
        return await interaction.response.send_message("❗ No welcome channel has been set for this server.", ephemeral=True)

    if interaction.channel.id != welcome_channel_id:
        return await interaction.response.send_message(
            f"🌸 Please use this command in the <#{welcome_channel_id}> channel where fairy winds can guide it.",
            ephemeral=True
        )

    lang_map = guild_config.get("languages", {})
    if not lang_map:
        return await interaction.response.send_message("❗ No languages are configured yet.", ephemeral=True)

    class LanguageView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for code, data in lang_map.items():
                self.add_item(Button(label=data['name'], emoji=data['emoji'], custom_id=code))

            # 🌸 Add a Cancel button
            self.add_item(Button(label="❌ Cancel", style=discord.ButtonStyle.danger, custom_id="cancel"))

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                await message.edit(content="⏳ Time ran out for language selection.", embed=None, view=None)
            except:
                pass

        async def on_error(self, interaction: discord.Interaction, error: Exception, item):
            print(f"❗ Whisperling button error: {error}")

    async def button_callback(inter: discord.Interaction):
        selected_code = inter.data['custom_id']
        if selected_code == "cancel":
            await inter.response.edit_message(content="❌ Cancelled.", embed=None, view=None)
            return

        if "users" not in guild_config:
            guild_config["users"] = {}

        guild_config["users"][user_id] = selected_code
        save_languages()
        lang_name = lang_map[selected_code]["name"]
        await inter.response.edit_message(
            content=f"✨ Your whisper has been tuned to **{lang_name}**.", embed=None, view=None
        )

    view = LanguageView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = button_callback

    mode = guild_modes.get(guild_id, "dayform")
    voice = MODE_TEXTS.get(mode, {})
    embed_color = MODE_COLORS.get(mode, discord.Color.purple())

    embed = discord.Embed(
        title=voice.get("language_intro_title", "🧚 Choose Your Whispering Tongue"),
        description=voice.get("language_intro_desc", "").replace("{user}", interaction.user.mention),
        color=embed_color
)


    message = await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✨ Please choose your language above.", ephemeral=True)

@bot.command(aliases=["sprachenkürzel", "codeslangues", "codigosidioma"])
async def langcodes(ctx):
    guild_id = str(ctx.guild.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.blurple())
    voice = MODE_TEXTS.get(mode, {})
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
        description="Use these with `/translate` or `!translate` to whisper across tongues:",
        color=embed_color
    )

    for code, name in codes.items():
        embed.add_field(name=f"`{code}`", value=name, inline=True)

    embed.set_footer(text=footer)
    await ctx.send(embed=embed)

bot.run(TOKEN)
