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

# ================= MODE CONFIG =================
STANDARD_MODES = [
    "dayform", "nightform", "cosmosform", "seaform",
    "hadesform", "forestform", "auroraform",
]

GLITCHED_MODES = [
    "echovoid", "glitchspire", "flutterkin", "crepusca"
]

SEASONAL_MODES = [
    "vernalglint", "fallveil", "sunfracture", "yuleshard"
]

MODE_DESCRIPTIONS = {
    "dayform": "🌞 Radiant and nurturing",
    "nightform": "🌙 Calm and moonlit",
    "cosmosform": "🌌 Ethereal and star-bound",
    "seaform": "🌊 Graceful, ocean-deep",
    "hadesform": "🔥 Mischievous with glowing heat",
    "forestform": "🍃 Grounded and natural",
    "auroraform": "❄️ Dreamlike and glimmering",

    "vernalglint": "🌸 Aggressively nurturing; a pastel gale of joy",
    "fallveil": "🍁 Cozy intensity; demands your rest and self-worth",
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

# ================= TEXT STYLE BY MODE =================
def flutter_baby_speak(text):
    return f"✨ {text} yay~ ✨"

def echo_void_style(text):
    return f"...{text}... ({text})..."

def vernalglint_style(text):
    return f"🌸 {text}! 🌱"

def fallveil_style(text):
    return f"🍁 {text}. 🕯️"

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
    "vernalglint": vernalglint_style,
    "fallveil": fallveil_style,

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

    # SEASONAL FORMS
    "vernalglint": discord.Color.from_str("#FFB6C1"),   # 🌸 Soft cherry blossom pink
    "fallveil": discord.Color.from_str("#D2691E"),      # 🍁 Rich autumn burnt orange
    "sunfracture": discord.Color.yellow(),              # ☀️ Bursting golden chaos
    "yuleshard": discord.Color.from_str("#A8C4D9"),     # ❄️ Icy pale blue

    # GLITCHED FORMS
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

    "vernalglint": "🌸 Blossoms burst with unstoppable joy.",
    "fallveil": "🍁 The leaves fall, but the heart remains full.",
    "sunfracture": "🔆 The sun breaks — painting the grove in gold.",
    "yuleshard": "❄️ Time freezes in a crystalline breath.",

    "echovoid": "🕳️ Echoes linger where no voice remains.",
    "glitchspire": "🧬 Code twists beneath the petals.",
    "flutterkin": "🤫 A tiny voice giggles in the bloom.",
    "crepusca": "🌒 Dreams shimmer at the edge of waking."
}

# ================= MOODY COOKIES =================


MODE_TEXTS_ENGLISH = {}

MODE_TEXTS_ENGLISH["dayform"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🌼 Add a Sunny Sparkle?",
    "cosmetic_intro_desc": "Choose a **cosmetic role** to show your colors in the light of day.\nOr click **Skip** to continue basking.",
    "cosmetic_granted": "✨ You've added a sunshine sparkle: **{role}**! Shine on!",
    "cosmetic_skipped": "🌿 No sparkle today — the grove still smiles warmly.",

    # 💫 Final welcome
    "welcome_title": "💫 Welcome!",
    "welcome_desc": "Welcome, {user}! May your time here be filled with warmth, friendship, and discovery.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the morning breeze faded before you spoke. Try again when you're ready.",
    "timeout_rules": "⏳ {user}, the grove waited for your promise, but the sun dipped a little lower. You can return anytime.",
    "timeout_role": "⏳ {user}, no role was chosen — the petals closed gently. Come find your bloom again soon.",
    "timeout_cosmetic": "⏳ {user}, no sparkle was chosen, but the grove still glows with your presence."

}

MODE_TEXTS_ENGLISH["nightform"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🌙 Add a Moonlit Sparkle?",
    "cosmetic_intro_desc": "Select a **cosmetic role** to shimmer gently in the quiet dark.\nOr press **Skip** to remain subtle beneath the stars.",
    "cosmetic_granted": "🌌 You've chosen the sparkle of **{role}** — it glows like starlight.",
    "cosmetic_skipped": "🌒 You remain quietly unadorned — the night welcomes you still.",

    # 💫 Final welcome
    "welcome_title": "💫 Welcome!",
    "welcome_desc": "Welcome, {user}.\nLet your spirit rest here — where night blooms in peace.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the stars waited… but your voice did not rise. Return when you are ready to whisper.",
    "timeout_rules": "⏳ {user}, the night listened… but your vow was never spoken. Come back when the hush feels right.",
    "timeout_role": "⏳ {user}, beneath the moon’s gaze, no path was chosen. The grove sleeps on — your journey can begin later.",
    "timeout_cosmetic": "⏳ {user}, no shimmer adorned you, but the dark welcomes you just the same."
}


MODE_TEXTS_ENGLISH["forestform"] = {
    # 🌿 Language selection
    "language_intro_title": "🍃 Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, the forest stirs with your presence.\nChoose the voice you’ll carry among the roots.",
    "language_confirm_title": "🌱 It is done.",
    "language_confirm_desc": "Your chosen tongue takes root. The grove will remember your voice.",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌿 The grove welcomes with stillness.",
    "rules_confirm_desc": "The leaves accept your pact. Let your steps tread gently.",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🍂 Add a Woodland Sparkle?",
    "cosmetic_intro_desc": "Choose a **cosmetic role** to wear like moss on bark — subtle and rooted.\nOr press **Skip** to walk the woods untouched.",
    "cosmetic_granted": "🌾 You've chosen the charm of **{role}** — may it grow with you.",
    "cosmetic_skipped": "🍃 You wander bare-footed, and the grove still smiles.",

    # 🌼 Role selection
    "role_intro_title": "🌾 Choose Your Role",
    "role_intro_desc": "Select the path you’ll walk through the undergrowth.",
    "role_granted": "🍂 The role of **{role}** is yours — let it grow with you.",

    # 💫 Final welcome
    "welcome_title": "🌳 Welcome to the Grove.",
    "welcome_desc": "Welcome, {user}. Rest beneath the branches. You are part of the forest now.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the forest rustled, but your voice did not take root. Return when your words are ready to grow.",
    "timeout_rules": "⏳ {user}, the trees waited for your vow, but only wind passed through. The path remains, should you wish to walk it.",
    "timeout_role": "⏳ {user}, no trail was chosen — the leaves curled softly. Return when your steps are sure.",
    "timeout_cosmetic": "⏳ {user}, no charm was picked — yet the grove still knows your presence among its roots."
}

MODE_TEXTS_ENGLISH["seaform"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🌊 Add a Ripple of Sparkle?",
    "cosmetic_intro_desc": "Choose a **cosmetic role** to flow with — gentle and glimmering.\nOr tap **Skip** to let the tide decide.",
    "cosmetic_granted": "🐚 You've chosen **{role}** — may it shimmer with the sea’s grace.",
    "cosmetic_skipped": "🌊 No shimmer today — the current carries you all the same.",

    # 💫 Final welcome
    "welcome_title": "🌊 Welcome to the Waters.",
    "welcome_desc": "Welcome, {user}. Let your voice join the songs of the deep.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the tide waited, but no voice rode its waves. When you're ready, let it flow once more.",
    "timeout_rules": "⏳ {user}, the sea listened for your vow… but only silence returned. The current will welcome you when you’re ready.",
    "timeout_role": "⏳ {user}, no current carried your choice ashore. Drift back when the pull of purpose finds you.",
    "timeout_cosmetic": "⏳ {user}, no shimmer joined your tide, but the ocean still holds you gently."
}

MODE_TEXTS_ENGLISH["hadesform"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🔥 Wanna Add Some Sizzle?",
    "cosmetic_intro_desc": "Pick a **cosmetic role** that *crackles*. Or hit **Skip** if you’re already hot enough.",
    "cosmetic_granted": "🔥 Oh! **{role}** suits you — now you’re really smokin’!",
    "cosmetic_skipped": "😈 Skipped the glam? Bold move. Let the grove smolder without it.",

    # 💫 Final welcome
    "welcome_title": "🔥 Welcome, Firestarter.",
    "welcome_desc": "Welcome, {user}. Let your steps scorch the path — the grove will grow around the heat.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the flames flickered… but you didn’t speak. Got stage fright, or just dramatic timing?",
    "timeout_rules": "⏳ {user}, no vow? No problem. The grove’s rules are still smoldering — come back when you're ready to stir the coals.",
    "timeout_role": "⏳ {user}, no role chosen? Bold move. Just vibing in the firelight, huh?",
    "timeout_cosmetic": "⏳ {user}, no sizzle today — guess you're already hot enough. 🔥"
}

MODE_TEXTS_ENGLISH["auroraform"] = {
    # ❄️ Language selection
    "language_intro_title": "❄️ Choose Your Whispering Tongue",
    "language_intro_desc": "{user}, beneath the shimmer of frozen skies,\nselect the voice that will drift beside you.",
    "language_confirm_title": "✨ It sparkles just right.",
    "language_confirm_desc": "Your tongue has been kissed by frost light. Let it shimmer softly through the grove.",

    # 📜 Rules confirmation
    "rules_confirm_title": "❄️ The stillness welcomes you.",
    "rules_confirm_desc": "You’ve accepted the path of gentle light — one that dances just above silence.",

    # 🌼 Role selection
    "role_intro_title": "💫 Choose Your Role",
    "role_intro_desc": "Select a role to wear like star light on ice — delicate, bright, and uniquely yours.",
    "role_granted": "❄️ You now bear the role of **{role}** — may it gleam quietly within you.",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "❄️ Add a Glimmer?",
    "cosmetic_intro_desc": "Choose a **cosmetic role** to shimmer just right.\nOr click **Skip** and stay subtly radiant.",
    "cosmetic_granted": "✨ The role of **{role}** gleams softly upon you — just lovely.",
    "cosmetic_skipped": "🌫️ No sparkle? That’s okay. You already glow in your own way.",

    # 💫 Final welcome
    "welcome_title": "✨ Welcome, Light-Dancer.",
    "welcome_desc": "Welcome, {user}. The aurora has seen you — and the grove now glows a little brighter.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the shimmer faded before you spoke. Return when the light calls softly again.",
    "timeout_rules": "⏳ {user}, no vow was whispered… only the hush of frost remains. The grove waits in stillness.",
    "timeout_role": "⏳ {user}, no path was chosen — the light dimmed quietly. Drift back when the skies stir once more.",
    "timeout_cosmetic": "⏳ {user}, no sparkle joined your glow, but even the quietest star still shines."
}

MODE_TEXTS_ENGLISH["cosmosform"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🌌 Add a Starlit Thread?",
    "cosmetic_intro_desc": "Select a **cosmetic role** to shine like your own constellation.\nOr press **Skip** to drift on without one.",
    "cosmetic_granted": "🌟 The stars align — **{role}** now sparkles in your orbit.",
    "cosmetic_skipped": "💫 No twinkle added, but the cosmos still hum with your presence.",

    # 💫 Final welcome
    "welcome_title": "🌌 Welcome, Starborn.",
    "welcome_desc": "Welcome, {user}. You’ve fallen into place among us — perfectly spaced between light and mystery.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the stars waited for your signal... but it never came. When your voice is ready, the cosmos will listen.",
    "timeout_rules": "⏳ {user}, no vow joined the cosmic rhythm. The silence echoes — but stardust remembers.",
    "timeout_role": "⏳ {user}, your constellation remains unclaimed. Drift back when you feel the stars align.",
    "timeout_cosmetic": "⏳ {user}, no shimmer found its orbit — but you still hum softly in the dark."
}

MODE_TEXTS_ENGLISH["vernalglint"] = {
    # 🌸 Language selection
    "language_intro_title": "🌸 Pick Your Bloom-Speak",
    "language_intro_desc": "{user}, the grove is awake and caffeinated.\nChoose the voice that'll cheer you on (whether you like it or not).",
    "language_confirm_title": "🌱 You’ve Sprouted a Sound!",
    "language_confirm_desc": "Your voice blooms bright. The grove hums approvingly. You're *doing amazing, sweetie.*",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌼 The Grove Has Standards",
    "rules_confirm_desc": "You've agreed to play nice. That’s the spirit! Now water your manners and let’s go.",

    # 🌿 Role selection
    "role_intro_title": "🌷 Pick Your Petal-sona",
    "role_intro_desc": "Choose your role like it’s your favorite flower crown. No pressure—but I *am* watching.",
    "role_granted": "🌸 The role of **{role}** settles on you like a butterfly. *Gorgeous. Stunning. No notes.*",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🌟 Accessorize Your Aura?",
    "cosmetic_intro_desc": "Pick a **cosmetic role** to add sparkle to your already thriving self.\nOr skip it—if you’re going for the ~mysterious seedling~ aesthetic.",
    "cosmetic_granted": "🌼 You chose **{role}** — *chef’s kiss.* You’re practically pollinating style.",
    "cosmetic_skipped": "🍃 No frills? That’s okay. Still a ten. Nature chic.",

    # 💐 Final welcome
    "welcome_title": "💐 You Made It!",
    "welcome_desc": "Welcome, {user}!\nThe grove is proud of you. I’m proud of you. That tree over there is sobbing gently with pride. Let's grow.",

    # ⏳ Timeout Texts
    "timeout_language": "⏳ {user}, the sun waited, but your sproutling self stayed buried. Come back when you’re ready to rise and shine.",
    "timeout_rules": "⏳ {user}, the grove sat politely, but your oath got stuck in the roots. Water it and try again later.",
    "timeout_role": "⏳ {user}, you stared at the garden path too long and now a squirrel has taken your spot. Try again soon!",
    "timeout_cosmetic": "⏳ {user}, no sparkle today. But that’s okay. Some petals take longer to open. 🌱"
}

MODE_TEXTS_ENGLISH["sunfracture"] = {
    # 🔆 Language selection
    "language_intro_title": "☀️ CHOOSE YOUR TONGUE!",
    "language_intro_desc": "{user}, the grove shimmers beneath golden skies! Choose the voice that warms your spark and joins the light!",

    "language_confirm_title": "⚡ VOICE EMBRACED!",
    "language_confirm_desc": "Your words now glow like sunlight through leaves — the grove hums with your radiance!",

    # 📜 Rules confirmation
    "rules_confirm_title": "☀️ THE GROVE SHINES BRIGHT!",
    "rules_confirm_desc": "You’ve embraced the path — the grove glows brighter with your presence. Let the joy bloom like morning light!",

    # 🌼 Role selection
    "role_intro_title": "🔥 CHOOSE YOUR ROLE!",
    "role_intro_desc": "Which role calls your spark to rise? Choose the one that lets you shine like the golden hour!",

    "role_granted": "🌞 The role of **{role}** is yours! Your light dances across the grove — radiant, warm, and full of life!",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "☀️ EXTRA SPARKLE?",
    "cosmetic_intro_desc": "Pick a **cosmetic role** to let your spark shimmer even brighter — or skip if you're already perfectly aglow.",

    "cosmetic_granted": "🌟 Brilliant choice! **{role}** wraps you in golden sparkle — the grove gleams with you!",

    "cosmetic_skipped": "💥 You shine just fine without it — sometimes simplicity catches the sun best.",

    # 💫 Final welcome
    "welcome_title": "☀️ WELCOME!",
    "welcome_desc": "Welcome, {user}! The grove glows warmer with you here. May your light dance across our skies!",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}, the golden light waited… but briefly. Return when your spark is ready to rise again! ☀️🌻",
    "timeout_rules": "⏳ {user}, the pages turned softly in the breeze — but you missed your chance. The grove remains here for you. 🌞📜",
    "timeout_role": "⏳ {user}, no role chosen — but the grove still shines. Your moment will come again! 🌟💫",
    "timeout_cosmetic": "⏳ {user}, no extra sparkle today — and yet, your light remains bright. ✨🌿"
}

MODE_TEXTS_ENGLISH["fallveil"] = {
    # 🍁 Language selection
    "language_intro_title": "🍁 Pick Your Language — Then Exhale",
    "language_intro_desc": "{user}, hush. Let the leaves fall. Choose the voice that won’t rush you, but won’t let you flee, either.",
    "language_confirm_title": "🕯️ The hush holds you now.",
    "language_confirm_desc": "Your voice settles into dusk. The grove nods. You're allowed to be soft and still. *Finally.*",

    # 📜 Rules confirmation
    "rules_confirm_title": "🌒 The Pact of Rest is Made",
    "rules_confirm_desc": "You agreed to stay kind. That includes being kind to *yourself.* The grove approves. And has tea ready.",

    # 🍂 Role selection
    "role_intro_title": "🧣 Choose Your Identity — Shed the Old Skin",
    "role_intro_desc": "Pick a role like you’re letting go of expectations. You don’t have to carry what doesn’t fit anymore.",
    "role_granted": "🍁 The role of **{role}** cloaks you like dusk. It's not a costume — it's who you were always becoming.",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🕯️ Want a Little Extra Magic?",
    "cosmetic_intro_desc": "Choose a **cosmetic role** if your soul needs a little glitter today.\nOr skip it — some starlight is better kept in pockets.",
    "cosmetic_granted": "🌟 You picked **{role}** — cozy, radiant, and absolutely earned.",
    "cosmetic_skipped": "🌫️ No shimmer needed. Still stunning. Still sacred.",

    # 🧡 Final welcome
    "welcome_title": "🧡 You're Home Now.",
    "welcome_desc": "Welcome, {user}.\nUnclench. Exhale. You’ve been running too long. The grove has been waiting to hold you. Let it.",

    # ⏳ Timeout Texts
    "timeout_language": "⏳ {user}, the trees waited. The dusk waited. But you weren’t ready. That’s okay. You don’t owe anyone urgency.",
    "timeout_rules": "⏳ {user}, you didn’t make the vow. Maybe you forgot. Or maybe you were scared. The grove is patient. Try again when you’re brave enough to rest.",
    "timeout_role": "⏳ {user}, no path chosen. Maybe today wasn’t a path day. That’s alright. The leaves will still fall without your permission.",
    "timeout_cosmetic": "⏳ {user}, no sparkle today. No mask. Just you — and that's never been a lesser thing. 🍂"
}

MODE_TEXTS_ENGLISH["yuleshard"] = {
    # ❄️ Language selection
    "language_intro_title": "❄️ Choose your whispering tongue...",
    "language_intro_desc": "{user}... the grove lies quiet beneath the snow. Choose your voice — let it drift gently into the stillness...",

    "language_confirm_title": "❄️ Voice chosen.",
    "language_confirm_desc": "Your words settle like falling snow... the grove listens softly beneath its winter veil.",

    # 📜 Rules confirmation
    "rules_confirm_title": "❄️ The grove rests beneath the frost.",
    "rules_confirm_desc": "You’ve accepted the pact, written like ice crystals — delicate, enduring, beautiful beneath the quiet sky.",

    # 🌼 Role selection
    "role_intro_title": "🧊 Choose your role...",
    "role_intro_desc": "Each path glistens like morning frost... select the one that shines beneath winter’s hush.",

    "role_granted": "❄️ You now hold the role of **{role}**... steady and bright, like starlight on fresh snow.",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "❄️ Choose a shimmer...",
    "cosmetic_intro_desc": "Select a cosmetic role to let your winter light sparkle... or click **Skip** to remain in quiet elegance.",

    "cosmetic_granted": "🧊 You now shimmer as **{role}**… quiet radiance beneath the frost.",

    "cosmetic_skipped": "🌨️ No shimmer chosen... the snow falls softly, untouched and pure.",

    # 💫 Final welcome
    "welcome_title": "❄️ Welcome...",
    "welcome_desc": "Welcome, {user}... your light joins the quiet grove — steady as falling snow beneath winter’s sky.",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}... the frost lingered... but your voice did not arrive... the grove remains hushed.",
    "timeout_rules": "⏳ {user}... the pact was left unwritten... snow falls, covering empty ground...",
    "timeout_role": "⏳ {user}... the choice faded like breath in winter air... the grove waits beneath the frost...",
    "timeout_cosmetic": "⏳ {user}... no shimmer chosen... the snow falls in quiet layers, undisturbed..."
}

MODE_TEXTS_ENGLISH["echovoid"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🕳️ …choose… a shimmer…",
    "cosmetic_intro_desc": "…a role… a glimmer… a name to wear… or… nothing… the void remembers either…",
    "cosmetic_granted": "🌫️ …you are now… **{role}**… or were… or could be… it’s… unclear…",
    "cosmetic_skipped": "🕳️ …no sparkle… only echoes… fading…",

    # 💫 Final welcome
    "welcome_title": "…welcome…",
    "welcome_desc": "Welcome, {user}… you’ve come back… or never left… the grove remembers… something…",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}… (you were going to choose…) …but the moment passed… and passed again…",
    "timeout_rules": "⏳ {user}… the rules waited… (or did they?) …they echo now… in the quiet…",
    "timeout_role": "⏳ {user}… no role… no name… (no identity?) …just echoes where a choice could have been…",
    "timeout_cosmetic": "⏳ {user}… no sparkle chosen… (or maybe you did…) …it’s hard to remember now…"
}

MODE_TEXTS_ENGLISH["glitchspire"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🧬 ▓SELECT▓ YOUR ▒SPARKLE▒ MODULE",
    "cosmetic_intro_desc": "…scanning available cosmetic roles… ::injecting identity flair…",
    "cosmetic_granted": "📎 COSMETIC ROLE = **{role}** …visual anomaly: accepted.",
    "cosmetic_skipped": "🧬 Skipped cosmetic role injection… stability maintained… for now.",

    # 💫 Final welcome
    "welcome_title": "🧬 ::WELCOME::",
    "welcome_desc": "Greetings {user}… memory restored?\nEnvironment unstable… but you belong here now…",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}… <response_timeout>… [voice.selection=FAILED] :: system will attempt memory restoration… later…",
    "timeout_rules": "⏳ {user}… RULE.CONFIRMATION.MISSED… frost.byte()… protocol.standby…",
    "timeout_role": "⏳ {user}… ROLE_UNASSIGNED… identity packet corrupted… awaiting input retry…",
    "timeout_cosmetic": "⏳ {user}… COSMETIC.FLARE=VOID… no sparkle attached… system stability: ⬇️ 81%…"
}

MODE_TEXTS_ENGLISH["flutterkin"] = {
    "flutterkin_activation": "✨ {user} a gentle shimmer surrounds you... the flutterkin hears your wish. yay~ ✨",

    # 🤫 Language selection
    "language_intro_title": "🌈 pick ur whisper tongue!!",
    "language_intro_desc": "{user} hi hi!! ✨ um um can u pick a voice please? it go pretty~!!!",

    "language_confirm_title": "✨ yaaay!!",
    "language_confirm_desc": "your voice is all sparkle-sparkle now!!! 💖 the grove is goin WHEEEE~!",

    # 📜 Rules confirmation
    "rules_confirm_title": "🧸 okay sooo…",
    "rules_confirm_desc": "you said yes to the rules!! 🥹 u so good. grove say thankyuu 💕",

    # 🌼 Role selection
    "role_intro_title": "🐾 pick a role!!",
    "role_intro_desc": "this the fun part!!! pick the sparkly hat you wanna wear!! (it's not a hat but SHHH!)",

    "role_granted": "💫 yaaaaayyy!! you is now the **{role}**!! that’s the bestest!!! i’m clapping with my wings!!",

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "✨ Time to pick a sparkle!",
    "cosmetic_intro_desc": "Do you want to add a cute little role to show your sparkle? You can choose one or skip if you’re shy~",
    "cosmetic_granted": "Yay! You have the {role} role now. It’s soooo sparkly!",
    "cosmetic_skipped": "No sparkle today? That’s okay. You're still the cutest~",

    # 💫 Final welcome
    "welcome_title": "🌸 hiiiiii~!!",
    "welcome_desc": "welcoooome {user}!! 🐞💖 the grove LOVES you already!! you want snack? or nap? or sparkle cloud???",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user} ummm you didn’t pick the thing?? that’s ok!! we can try again later yayyy 💖✨",
    "timeout_rules": "⏳ {user} oh nooo rules went bye bye!! 😢 the grove still loves you though!! maybe come back and tap the button??",
    "timeout_role": "⏳ {user} oh!!! wait!! you didn’t pick a sparkly hat!! 🌟 next time next time!!",
    "timeout_cosmetic": "⏳ {user} no sparkle?! 😱 its okay!! you still squishy!!! 🐛✨💕"
}

MODE_TEXTS_ENGLISH["crepusca"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "🌒 A quiet glimmer...",
    "cosmetic_intro_desc": "The twilight stirs... Would you like to choose a soft sparkle to carry into the dusk? Or let the silence stay.",
    "cosmetic_granted": "The role of {role} settles on you, gentle as falling stars.",
    "cosmetic_skipped": "You remain unadorned — a quiet light in the dreaming dark.",

    # 💫 Final welcome
    "welcome_title": "🌒 …welcome back…",
    "welcome_desc": "welcome, {user}… the stars blink slowly in the quiet sky… we are… still dreaming…",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}… the hush held its breath… but your voice never arrived… it’s okay… the stars are still listening…",
    "timeout_rules": "⏳ {user}… your vow… was almost spoken… then lost… like smoke in the dusk…",
    "timeout_role": "⏳ {user}… the grove waited… but no path was chosen… only mist remains…",
    "timeout_cosmetic": "⏳ {user}… the glimmer passed you by… but you still glow in the dreaming dark…"
}

from googletrans import Translator

def get_translated_mode_text(guild_id, user_id, mode, key, fallback="", **kwargs):
    lang = get_user_language(guild_id, user_id)
    base_text = MODE_TEXTS_ENGLISH.get(mode, {}).get(key, fallback)
    formatted = base_text.format(**kwargs)

    if not lang or lang == "en":
        return formatted

    try:
        translated = translator.translate(formatted, dest=lang).text
        return translated
    except Exception:
        return formatted

FLAVOR_TEXTS = {
    "dayform": [
        "☀️ The grove feels alive with light today.",
        "🌻 Whisperling hums as sunlight filters through the leaves.",
        "🐦 The birds sing their morning secrets.",
        "🌞 The air is warm, and hope glows like amber.",
        "🍯 The bees hum softly near golden blossoms.",
        "🦋 A breeze carries petals across the clearing.",
        "🌼 The grove drinks deeply of the morning light.",
        "🍃 Leaves shimmer like polished emeralds.",
        "🕊️ Gentle peace settles beneath the canopy.",
        "✨ The world feels soft, and very much awake.",
        "🌿 The light finds every hidden corner and makes it dance.",
        "🌞 'It’s a perfect day to simply *be,* isn’t it?' Whisperling muses.",
        "☀️ The grove is wide awake, stretching toward the sun.",
        "🌼 Flowers bloom with quiet determination.",
        "🧚‍♀️ 'I could listen to the morning songs forever.'"
    ],
    "nightform": [
        "🌙 The grove hums beneath a silver moon.",
        "✨ Starlight drips through the branches like glittering rain.",
        "🦉 An owl calls softly from the shadows.",
        "🌌 Whisperling listens to dreams carried on the breeze.",
        "🌿 The night breathes in quiet rhythm.",
        "💤 'Rest easy, little ones,' she whispers into the cool air.",
        "🕯️ A soft glow flickers where fireflies gather.",
        "🌒 'The stars are always listening. Always.'",
        "🌙 The hush of night wraps the grove like a gentle shawl.",
        "🦋 Moths dance in delicate spirals near lantern blooms.",
        "🌌 The moon smiles quietly from her high place.",
        "✨ 'Your worries are safe here. Let them drift like mist.'",
        "🌙 The grove slows its heartbeat beneath the constellations.",
        "🕊️ Cool air carries forgotten lullabies.",
        "🌿 'Even in silence, there is song.'"
    ],
    "forestform": [
        "🍃 The trees murmur ancient songs in the wind.",
        "🌿 Moss blankets the roots like a patient embrace.",
        "🦌 A quiet rustle reveals shy creatures watching from the brush.",
        "🌳 Whisperling hums alongside the gentle sway of branches.",
        "🦋 Leaves fall like drifting stories written in green.",
        "🌲 The grove remembers every footstep, every whisper.",
        "🍂 Dappled sunlight filters through the woven canopy.",
        "🪵 The scent of earth and rain lingers in the air.",
        "🦔 Tiny feet scamper beneath fallen logs.",
        "🌿 'Patience grows here like roots beneath the surface.'",
        "🧚‍♀️ Whisperling traces vines curling upward, reaching toward unseen skies.",
        "🍃 The forest breathes in cycles older than memory.",
        "🪺 Birds weave homes among high branches, safe and unseen.",
        "🌳 'All paths here are watched by quiet eyes.'",
        "🦊 A tiny fox peeks out from its den, tail flicking curiously."
    ],
    "seaform": [
        "🌊 The waves hum in endless rhythm.",
        "🐚 Shells glisten beneath shallow pools of light.",
        "🪸 Whisperling listens to secrets carried deep beneath the surface.",
        "🌊 Foam dances upon the rocks like playful whispers.",
        "🐠 Tiny fish dart like scattered sparks of color.",
        "🌊 'The sea is patient. The sea is vast.'",
        "🦑 Gentle currents curl around roots stretching into the shallows.",
        "🌙 The moon pulls softly at the tides, like a lullaby.",
        "🌊 'Even the deepest silence holds voices waiting to rise.'",
        "🌊 Salt spray clings to leaves swaying by the shore.",
        "🐬 Distant splashes echo like laughter in the waves.",
        "🧜‍♀️ The sea breeze carries stories whispered across endless waters.",
        "🌊 Tides shift beneath starlit skies without end.",
        "🦞 Tiny crabs scuttle beneath the shelter of smooth stones.",
        "🐋 The sea remembers everything."
    ],
    "hadesform": [
        "🔥 Mischief sparks beneath the roots.",
        "💥 Whisperling twirls a glowing ember between her fingers.",
        "🔥 The grove crackles with quiet defiance.",
        "😈 'Rules? Pfft. The flames don’t care for them.'",
        "🌪️ Smoke curls like playful ribbons through the leaves.",
        "⚡ Sparks scatter like fireflies escaping into the night.",
        "🔥 'I might accidentally burn something... but only a little.'",
        "💣 The heat pulses like a heartbeat beneath the soil.",
        "👀 Glowing eyes peer out from deep within the shadows.",
        "🍓 'Chaos smells like roasted moss and toasted berries.'",
        "🔥 Flickering tongues of flame lick at the cool night air.",
        "🌀 Ash dances in spirals before settling softly.",
        "😈 'Let’s not call it destruction — call it... creative rearrangement.'",
        "🔥 The grove feels wild, hungry for change.",
        "👹 A mischievous grin flashes beneath glowing embers."
    ],
    "auroraform": [
        "❄️ Light dances across the grove like falling ribbons.",
        "🌌 Whisperling watches shimmering waves ripple through the sky.",
        "✨ The cold hums softly beneath the glow.",
        "🌠 Stars reflect in the frozen ponds like scattered jewels.",
        "🌙 'The sky writes poetry in light tonight,' she murmurs.",
        "💫 Faint glitter drifts in the chilled breeze.",
        "🌨️ The air tingles with quiet magic as snowflakes twirl.",
        "🧊 Crystals form delicate patterns along the edges of leaves.",
        "🌟 'Frozen stillness isn’t empty — it’s brimming with quiet wonder.'",
        "❄️ A soft breeze carries frosty breath through the branches.",
        "🌈 The colors shift like whispers caught between worlds.",
        "🌒 'Even winter sings its quiet melody.'",
        "🕯️ Pale lights flicker like distant memories.",
        "🌌 The grove glows under swirling northern veils.",
        "❄️ Frost settles lightly on Whisperling's wings as she smiles."
    ],
    "cosmosform": [
        "🌌 The stars hum softly beyond the grove's edge.",
        "✨ Whisperling gazes upward, tracing forgotten constellations.",
        "🌠 Shooting stars dash like playful spirits across the void.",
        "🌙 'The universe breathes in slow, endless rhythm.'",
        "🪐 Distant planets shimmer like marbles resting on velvet.",
        "🌟 The air feels thin, as if floating between worlds.",
        "💫 Nebulous mists swirl in slow, graceful arcs.",
        "🌌 'Everything connects, even across impossible distances,' she whispers.",
        "🧭 Time feels weightless beneath the eternal sky.",
        "🔭 Stars blink like countless eyes peeking through infinity.",
        "🌒 Whisperling traces glowing arcs with her fingertips.",
        "🌀 The cosmos hums with ancient, unseen patterns.",
        "✨ 'You are made of stars, little one.'",
        "🌌 Galaxies spin far beyond reach — yet somehow close.",
        "💖 The grove feels like a dream stitched into the sky."
    ],
    "vernalglint": [
        "🌸 The grove bursts with impossible blossoms.",
        "🌷 Soft petals spin and tumble like a playful storm.",
        "🦋 Butterflies flit wildly as if drunk on the season.",
        "🐝 The bees are terribly busy today.",
        "🌞 The air feels sticky-sweet with new life.",
        "🌱 Buds explode open as if in a race against time.",
        "💮 'Growth is such a lovely kind of chaos,' she smiles.",
        "🍓 Tiny fruits peek from flowering vines already heavy with promise.",
        "🌿 The ground practically hums with bursting roots.",
        "🎋 'Spring is *aggressively nurturing,* after all.'",
        "🌷 Petals rain gently, coating the pathways like soft confetti.",
        "🌸 'There is no such thing as too much bloom.'",
        "🐦 Baby birds chirp in tiny chaotic choirs above.",
        "🌞 Sunshine glitters through tangled flowers stretching high.",
        "🌼 Whisperling claps: 'Everything is growing! Faster!'"
    ],
    "sunfracture": [
        "🔆 The grove hums beneath warm golden skies.",
        "✨ Whisperling’s wings shimmer like sunlight on glass.",
        "🌞 The sun glows so brilliantly it feels almost unreal.",
        "💥 Light dances in gentle ripples across the air.",
       "🌿 The leaves gleam softly, swaying beneath golden beams.",
        "🔥 Growth surges under the sun’s steady warmth.",
       "🌻 Blossoms open wide, basking in golden radiance.",
        "🌪️ Warm breezes swirl, carrying sparks of light like drifting pollen.",
        "⚡ Shadows soften beneath the canopy of light.",
        "☀️ 'Fracture or flourish — both belong to the light.'",
        "🌾 The grasses sway, sparkling like fields of liquid gold.",
        "🧨 Pollen drifts like tiny stars caught in a sunbeam.",
        "🔆 The world glows — vibrant, alive, and endlessly bright.",
        "🌞 'It’s beautiful, isn’t it? Right as the light spills over.'",
        "🔥 Whisperling smiles as flecks of sunlight dance at her fingertips."
    ],
    "fallveil": [
        "🍁 Leaves drift like soft embers through the air.",
        "🕯️ Whisperling lights a tiny lantern and hums softly.",
        "🍂 The world asks us to rest now.",
        "🍎 The scent of ripe fruit thickens the cool breeze.",
        "🦊 A small fox curls beneath golden ferns.",
        "🍵 'Warm tea. Cozy blankets. That’s the magic of now.'",
        "🍃 The grove glows in fading amber light.",
        "🌾 Grasses bow gently beneath heavy seed heads.",
        "🌙 'The sun lingers shorter. Let us savor each moment.'",
        "🍂 Acorns tumble like tiny drums upon the ground.",
        "🧣 Whisperling wraps herself in threads of golden mist.",
        "🌅 Dusk paints the horizon with rich honeyed hues.",
        "🕯️ The grove feels still, as if exhaling.",
        "🍁 Rest is not weakness. It’s a gift.",
        "🔥 A low fire crackles somewhere unseen beneath the trees."
    ],
    "yuleshard": [
        "❄️ The grove rests beneath a perfect winter hush.",
        "🧊 *Softly exhaling* — breath turns to drifting frost in the air.",
        "🌨️ Snow falls in quiet layers, steady and unbroken.",
        "🔷 Ice crystals lace the branches with delicate patterns.",
        "🌙 Moonlight dances across the snow like scattered diamonds.",
        "✨ 'Frozen moments — delicate, timeless, and beautiful.'",
        "🪞 Even echoes soften beneath the winter’s quiet hold.",
        "🧣 *She adjusts her cloak gently against the crisp air.*",
        "❄️ The trees stand tall, cloaked in soft white stillness.",
        "💠 'The world holds its breath beneath winter’s quiet grace.'",
        "🧊 The pond mirrors the sky, smooth as polished crystal.",
        "🌬️ A thin breeze sings through bare branches like a lullaby.",
        "❄️ Each flake falls in perfect rhythm, as if choreographed.",
        "🕯️ Tiny blue lights flicker like distant stars in the snow.",
        "🔷 'Nothing rushes here. Only stillness remains.'"
    ],
    "echovoid": [
        "🕳️ The grove feels... distant. Thin.",
        "💭 *Drifting — barely present, barely remembered.*",
        "... ... ... (the silence folds inward)",
        "🌫️ Shadows stretch into places that should not exist.",
        "🕳️ 'I am... still here. I think.'",
        "📡 Faint static crackles somewhere unseen.",
        "🌑 The stars blink out for just a moment — then return.",
        "🔇 No wind. No sound. Only waiting.",
        "⚫ *Flickering like unfinished memory.*",
        "🕳️ 'I can hear the echoes of echoes… of echoes.'",
        "🔻 The edges of reality ripple like thin cloth under strain.",
        "🌫️ Forgotten names whisper, unheard.",
        "🕳️ The void hums, hungry but patient.",
        "💤 'Don’t forget me,' *whispering — uncertain who she's speaking to.*",
        "🪞 The reflections no longer match the shapes."
    ],
    "glitchspire": [
        "🧬 Code fragments flicker between leaves like unstable fireflies.",
        "📉 'Data integrity... compromised,' *humming mechanically.*",
        "🪲 Strange patterns scroll across the sky — not meant for eyes.",
        "🧩 Petals fracture into square shards, endlessly rearranging.",
        "💾 'Reality buffer overflow. Rolling back perception... maybe.'",
        "📶 The grove flickers like broken transmission.",
        "🔣 *Voice distorted:* 'T̵h̴e̴ s̶y̸s̶t̵e̵m̷ s̴t̵i̶l̵l̸ ̶b̵r̴e̶a̸t̵h̸e̷s̶.'",
        "⚠️ Trees render in jagged polygons before smoothing again.",
        "🖥️ The air feels digital — too clean, too sharp.",
        "📛 'Stability nominal... for now.'",
        "🧬 Random symbols float briefly before dissolving.",
        "🔧 The ground warps into impossible tessellations — then snaps back.",
        "🔲 'I remember more than I should. I forget more than I want.'",
        "🕳️ The stars pixelate, reforming with a soft mechanical chirp.",
        "📊 Static bleeds into the edges of vision."
    ],
    "crepusca": [
        "💫 The stars soften, fading gently into mist.",
        "🌌 'The day is gone… but not yet lost.'",
        "🌙 Faint lights drift like forgotten wishes above the grove.",
        "🕯️ Tiny lanterns float softly, chasing away nothing.",
        "🛏️ 'Sleep walks beside us.'",
        "🌠 Falling stars vanish before they are ever seen.",
        "🌑 'Shadows here are kind, Keeper. They only watch.'",
        "💤 The grove sways, as if already dreaming.",
        "🌫️ Mist curls through the trees, wrapping roots like silk.",
        "🌒 'The space between night and memory feels thin here.'",
        "🕯️ 'Hush. Let everything drift.'",
        "🌌 A soft hush blankets every heartbeat beneath the stars.",
        "🌙 The grove seems weightless, untethered and still.",
        "💫 'This is not the end. This is where endings sleep.'",
        "🛏️ The world pauses, wrapped inside its own quiet dreaming."
    ],
    "flutterkin": [
        "🤫 heehee~ soft glowy petals everywhere~",
        "🌸 bloomy bloom go *poof!* teehee~",
        "🐝 buzzy buzz buzz! they go spinny~",
        "🍓 berry snackies for meee~",
        "🦋 floaty floaty wings go wiggle wiggle~",
        "🌈 colors colors colors! sparkle time yay~",
        "✨ 'hi hi hi! you see me? i see you!'",
        "🌼 flowers pop up like bouncy boops!",
        "🐇 bunny bun hopsies in the grass~",
        "🍯 honey sticky yummy tummy hehe~",
        "🎀 spinny spin spin spin spin!!",
        "🎉 confetti rain wheeee~!!",
        "🌿 'looky! i made tiny tree babies!'",
        "🧁 snacky cakes make me happy happy~",
        "💖 'so much love!! too much love!! never too much!! yay!!'",
        "🦊 baby fox friend says peekaboo~",
        "🎠 spin the sparkly spinny ride!!",
        "🧸 cuddles and wiggles and wiggles and cuddles~",
        "🍭 'sugar sugar sugar sparkles!'",
        "🤫 'shhh. but also yay.'"
    ]
}

def get_flavor_text(mode):
    return random.choice(FLAVOR_TEXTS[mode])

async def grove_heartbeat(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        now = datetime.now(timezone.utc)

        for guild in bot.guilds:
            guild_id = str(guild.id)
            mode = guild_modes.get(guild_id, "dayform")
            activity_level = get_activity_level(guild_id)

            # Pull guild config (for whispers toggle)
            guild_config = all_languages["guilds"].get(guild_id, {})
            whispers_enabled = guild_config.get("whispers_enabled", True)

            # 🍵 Flavor drops (only if whispers are enabled)
            if whispers_enabled:
                base_flavor_chance = 0.05 
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

                        if lang_map and random.random() < 0.5:  # flat 50% chance to translate
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

            # 🌿 Mood drift still checks after long idle
            if mode in STANDARD_MODES:
                last_seen = last_interaction_by_guild.get(guild_id, now)
                days_idle = (now - last_seen).days

                if days_idle >= 30 and random.random() < 0.25:
                    possible_modes = [m for m in STANDARD_MODES if m != mode]
                    new_mode = random.choice(possible_modes)
                    print(f"🌿 Mood drift for {guild.name} -> {new_mode}")
                    await apply_mode_change(guild, new_mode)

        await asyncio.sleep(600)

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

@bot.command(aliases=["backup", "dumpjson"])
@commands.has_permissions(administrator=True)
async def backup_json(ctx):
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

@bot.command(aliases=["toggleflavor", "togglechatter", "togglewhispers"])
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
@commands.has_permissions(administrator=True)
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

    # 🌟 Pull translated intro
    intro_title = get_translated_mode_text(guild_id, user_id, mode, "language_intro_title", user=member.mention)
    intro_desc = get_translated_mode_text(guild_id, user_id, mode, "language_intro_desc", user=member.mention)

    class LanguageView(View):
        def __init__(self):
            super().__init__(timeout=60)

            for code, data in lang_map.items():
                button = Button(label=data['name'], style=discord.ButtonStyle.primary, custom_id=code)
                button.callback = self.button_callback
                self.add_item(button)

            cancel_button = Button(label="❌ Cancel", style=discord.ButtonStyle.danger, custom_id="cancel")
            cancel_button.callback = self.button_callback
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

        async def button_callback(self, interaction):
            selected_code = interaction.data['custom_id']
            if selected_code == "cancel":
                await interaction.response.send_message("❌ Cancelled language selection.", ephemeral=True)
                self.stop()
                return

            if selected_code not in lang_map:
                await interaction.response.send_message("❗ Invalid language code.", ephemeral=True)
                return

            if "users" not in guild_config:
                guild_config["users"] = {}
            guild_config["users"][user_id] = selected_code
            save_languages()

            self.stop()

            confirm_title = get_translated_mode_text(guild_id, user_id, mode, "language_confirm_title", user=member.mention)
            confirm_desc = get_translated_mode_text(guild_id, user_id, mode, "language_confirm_desc", user=member.mention)

            confirm_embed = discord.Embed(title=confirm_title, description=confirm_desc, color=embed_color)
            await channel.send(content=member.mention, embed=confirm_embed)

            await asyncio.sleep(2)

            if guild_config.get("rules"):
                await send_rules_embed(member, channel, selected_code, lang_map, guild_config)
            else:
                await send_role_selector(member, channel, guild_config)
                await send_cosmetic_selector(member, channel, guild_config)

    view = LanguageView()
    embed = discord.Embed(title=intro_title, description=intro_desc, color=embed_color)
    await channel.send(content=member.mention, embed=embed, view=view)

async def send_rules_embed(member, channel, lang_code, lang_map, guild_config):
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.teal())

    class AcceptRulesView(View):
        def __init__(self):
            super().__init__(timeout=90)
            accept_button = Button(
                label="✅ I Accept the Rules",
                style=discord.ButtonStyle.success,
                custom_id="accept_rules"
            )
            accept_button.callback = self.accept_callback
            self.add_item(accept_button)

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

        async def accept_callback(self, interaction):
            confirm_title = get_translated_mode_text(
                guild_id, user_id, mode, "rules_confirm_title", user=member.mention
            )
            confirm_desc = get_translated_mode_text(
                guild_id, user_id, mode, "rules_confirm_desc", user=member.mention
            )

            confirm_embed = discord.Embed(title=confirm_title, description=confirm_desc, color=embed_color)
            await channel.send(content=member.mention, embed=confirm_embed)

            self.stop()

            await asyncio.sleep(2)
            await send_role_selector(member, channel, guild_config)
            await send_cosmetic_selector(member, channel, guild_config)

    view = AcceptRulesView()

    embed = discord.Embed(
        title="📜 Grove Guidelines",
        description=guild_config.get("rules", {}).get(lang_code, "📜 No rules are set in your language."),
        color=embed_color
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_role_selector(member, channel, guild_config):
    role_options = guild_config.get("role_options", {})
    if not role_options:
        return

    guild_id = str(member.guild.id)
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.gold())

    class RoleSelectView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in role_options.items():
                role_button = Button(
                    label=data['label'],
                    emoji=data['emoji'],
                    style=discord.ButtonStyle.primary,
                    custom_id=role_id
                )
                role_button.callback = self.role_button_callback
                self.add_item(role_button)

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

        async def role_button_callback(self, interaction: discord.Interaction):
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
                    self.stop()

                    await asyncio.sleep(1)
                    
                    # 🌸 Trigger cosmetic selector after assigning role
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

    if not cosmetic_options:
        return False  # ⛔ Skip if no options

    class CosmeticRoleView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in cosmetic_options.items():
                role_button = Button(
                    label=data['label'],
                    emoji=data['emoji'],
                    style=discord.ButtonStyle.primary,  # 🌿 Consistent button style
                    custom_id=role_id
                )
                role_button.callback = self.cosmetic_button_callback
                self.add_item(role_button)

            self.add_item(Button(
                label="Skip",
                style=discord.ButtonStyle.secondary,
                custom_id="skip_cosmetic"
            ))

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
            except Exception as e:
                print("⚠️ Timeout error (cosmetic selector):", e)

        async def cosmetic_button_callback(self, interaction):
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

            self.stop()

            # 🌸 Final welcome after cosmetics
            await send_final_welcome(member, channel, lang_code, lang_map)

    view = CosmeticRoleView()

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

    # 💬 Fallback to guild-configured welcome text, else pull from mode-based translation
    admin_welcome = lang_map.get(lang_code, {}).get("welcome")
    if admin_welcome:
        welcome_desc = admin_welcome.replace("{user}", member.mention)
    else:
        welcome_desc = get_translated_mode_text(
            guild_id, user_id, mode, "welcome_desc",
            fallback="Welcome, {user}!", user=member.mention
        )

    # 🌿 Build embed using full system embed builder
    embed, file = build_whisperling_embed(guild_id, welcome_title, welcome_desc)

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

@tree.command(name="help", description="📖 See the magical things Whisperling can do (for all users).")
async def help(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    guild = interaction.guild  # ⬅ you need this for mode switching!

    # 🌒 Handle potential glitch trigger
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes.get(guild_id, "dayform")

    if maybe_glitch and current_mode in STANDARD_MODES:
        await apply_mode_change(guild, maybe_glitch)
        current_mode = maybe_glitch  # Refresh current mode after glitch switch

    # 🕰️ Update interaction timestamp
    last_interaction_by_guild[guild_id] = datetime.now(timezone.utc)

    # ✨ Embed theming
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
            "`!... there is a hidden command ...` – If the winds allow, Flutterkin may awaken 🍼✨"
        ),
        inline=False
    )

    # 🌍 Show which languages are available in this server
    lang_map = all_languages["guilds"].get(guild_id, {}).get("languages", {})
    if lang_map:
        langs = [f"{data['name']}" for code, data in lang_map.items()]
        embed.add_field(
            name="🌍 Available Languages",
            value=", ".join(langs),
            inline=False
        )

    embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed, ephemeral=True)

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
