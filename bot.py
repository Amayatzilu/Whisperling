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
            if mode == "flutterkin":
                if timestamp and (now - timestamp > timedelta(minutes=30)):
                    previous = previous_standard_mode_by_guild[guild_id]
                    print(f"🍼 Flutterkin nap time for {guild_id}. Reverting to {previous}.")
                    guild_modes[guild_id] = previous
                    glitch_timestamps_by_guild[guild_id] = None
                    await update_avatar_for_mode(previous)
            elif mode in ["echovoid", "glitchspire", "crepusca"]:
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

MODE_TEXTS_ENGLISH["sunfracture"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "☀️ EXTRA SPARKLE?! YES PLEASE!!!",
    "cosmetic_intro_desc": "Pick a **cosmetic role** to SHIMMER EVEN HARDER!!! Or hit **Skip** if you’re TOO BRIGHT ALREADY!!!",
    "cosmetic_granted": "🌟 WHOOOO!! You got **{role}** and now you’re EVEN MORE FABULOUS!!!",
    "cosmetic_skipped": "💥 Skipped it?! BOLD. Brilliant. A PURE BEAM OF CHOICE!!!",

    # 💫 Final welcome
    "welcome_title": "☀️ WELCOME!!!",
    "welcome_desc": "WELCOME, {user}!!! The GROVE is BLINDING with JOY!!! Let’s SHINE TOGETHER FOREVER!!!",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}!!! YOU TOOK TOO LONG!! THE GROVE IS STILL BRIGHT BUT LIKE!! HURRY NEXT TIME!! 💛💥🌻",
    "timeout_rules": "⏳ {user}, rules were GLOWING, pages were TURNING… but you MISSED THEM!! No worries!! COME BACK SOON OKAY?! 🌞🔥📜",
    "timeout_role": "⏳ {user}!!! NO ROLE?! NO GLOW-UP?? 😱😱 okay okay breathe... YOU CAN STILL SHINE LATER!!! 🌟💫",
    "timeout_cosmetic": "⏳ {user}!!! YOU DIDN’T SPARKLE!!! but like... YOU’RE STILL FABULOUS!!! 😘✨✨✨"
}

MODE_TEXTS_ENGLISH["yuleshard"] = {
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

    # ✨ Cosmetic Role Selection
    "cosmetic_intro_title": "❄️ choose... a shimmer…",
    "cosmetic_intro_desc": "select... a cosmetic role... to reflect your frozen light...\nor... click **Skip**... if the cold is enough...",
    "cosmetic_granted": "🧊 you now glimmer as **{role}**… brittle... beautiful… unforgettable…",
    "cosmetic_skipped": "🌨️ the frost deepens... no shimmer chosen... only silence remains…",

    # 💫 Final welcome
    "welcome_title": "❄️ Welcome...",
    "welcome_desc": "Welcome, {user}... the grove... remembers your warmth... as the ice takes hold...",

    # ⏳ Timeout Text
    "timeout_language": "⏳ {user}... the cold waited... your voice never arrived... it’s... so quiet now...",
    "timeout_rules": "⏳ {user}... the pact was never spoken... the ice holds... nothing...",
    "timeout_role": "⏳ {user}... your choice... froze before it formed... the grove forgets the shape of it...",
    "timeout_cosmetic": "⏳ {user}... no shimmer... only frost settling deeper... and deeper..."
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

async def update_avatar_for_mode(mode: str):
    avatar_paths = {
        "dayform": "avatars/dayform.png",
        "nightform": "avatars/nightform.png",
        "forestform": "avatars/forestform.png",
        "seaform": "avatars/seaform.png",
        "hadesform": "avatars/hadesform.png",
        "auroraform": "avatars/auroraform.png",
        "cosmosform": "avatars/cosmosform.png",

        "sunfracture": "avatars/sunfracture.png",
        "yuleshard": "avatars/yuleshard.png",
        "echovoid": "avatars/echovoid.png",
        "glitchspire": "avatars/glitchspire.png",
        "flutterkin": "avatars/flutterkin.png",
        "crepusca": "avatars/crepusca.png",
    }

    path = avatar_paths.get(mode)
    if path and os.path.exists(path):
        with open(path, 'rb') as f:
            try:
                await bot.user.edit(avatar=f.read())
                print(f"✨ Avatar updated for mode: {mode}")
            except discord.HTTPException as e:
                print(f"❗ Failed to update avatar: {e}")
    else:
        print(f"⚠️ No avatar found for mode: {mode}")

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
            "_Example:_ `!addlanguage it 🇮🇹 Italiano`"
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
        name="4️⃣ Server Rules",
        value="`!setrules <text>` – Shown after language is chosen.",
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

@bot.command(aliases=["Kosmetikhinzufügen", "ajouterrolecosmetique", "agregarrolcosmetico"])
@commands.has_permissions(administrator=True)
async def addcosmetic(ctx, role: discord.Role, emoji: str, *, label: str):
    guild_id = str(ctx.guild.id)
    config = all_languages["guilds"].setdefault(guild_id, {})
    config.setdefault("cosmetic_role_options", {})[str(role.id)] = {
        "emoji": emoji,
        "label": label
    }
    save_languages()
    await ctx.send(f"✨ Added cosmetic role `{label}` with emoji {emoji}.")

@bot.command(aliases=["Kosmetikentfernen", "supprimerrolecosmetique", "eliminarrolcosmetico"])
@commands.has_permissions(administrator=True)
async def removecosmetic(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    cosmetic_roles = all_languages["guilds"].get(guild_id, {}).get("cosmetic_role_options", {})

    if str(role.id) not in cosmetic_roles:
        await ctx.send("❗ That cosmetic role is not currently configured.")
        return

    del all_languages["guilds"][guild_id]["cosmetic_role_options"][str(role.id)]
    save_languages()
    await ctx.send(f"🗑️ Removed cosmetic role `{role.name}`.")

@bot.command(aliases=["Kosmetikliste", "listerolescosmetiques", "listarrolescosmeticos"])
@commands.has_permissions(administrator=True)
async def listcosmetics(ctx):
    guild_id = str(ctx.guild.id)
    cosmetic_roles = all_languages["guilds"].get(guild_id, {}).get("cosmetic_role_options", {})

    if not cosmetic_roles:
        await ctx.send("📭 No cosmetic roles are currently configured.")
        return

    embed = discord.Embed(
        title="✨ Cosmetic Roles",
        description="These roles add flair without affecting permissions:",
        color=discord.Color.purple()
    )

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
                self.add_item(Button(label=data['name'], emoji=data['emoji'], custom_id=code))
            self.add_item(Button(label="❌ Cancel", style=discord.ButtonStyle.danger, custom_id="cancel"))

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
            except:
                pass

    async def button_callback(inter):
        selected_code = inter.data['custom_id']
        if selected_code == "cancel":
            await inter.response.send_message("❌ Cancelled language selection.", ephemeral=True)
            return

        if selected_code not in lang_map:
            return

        if "users" not in guild_config:
            guild_config["users"] = {}

        guild_config["users"][user_id] = selected_code
        save_languages()

        view.stop()

        # 🌸 Pull confirmation
        confirm_title = get_translated_mode_text(guild_id, user_id, mode, "language_confirm_title", user=member.mention)
        confirm_desc = get_translated_mode_text(guild_id, user_id, mode, "language_confirm_desc", user=member.mention)

        confirm_embed = discord.Embed(title=confirm_title, description=confirm_desc, color=embed_color)
        await channel.send(content=member.mention, embed=confirm_embed)

        await asyncio.sleep(2)

        # 🌿 Continue journey
        if guild_config.get("rules"):
            await send_rules_embed(member, channel, selected_code, lang_map, guild_config)
        else:
            await send_role_selector(member, channel, guild_config)
            await send_cosmetic_selector(member, channel, guild_config)

    # 🔘 Assign callbacks to each button
    view = LanguageView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = button_callback

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
            self.add_item(Button(label="✅ I Accept the Rules", style=discord.ButtonStyle.success, custom_id="accept_rules"))

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
            except:
                pass

    async def accept_callback(interaction):
        confirm_title = get_translated_mode_text(guild_id, user_id, mode, "rules_confirm_title", user=member.mention)
        confirm_desc = get_translated_mode_text(guild_id, user_id, mode, "rules_confirm_desc", user=member.mention)

        confirm_embed = discord.Embed(title=confirm_title, description=confirm_desc, color=embed_color)
        await channel.send(content=member.mention, embed=confirm_embed)

        view.stop()  # ✅ Stop the timeout here on successful press

        await asyncio.sleep(2)
        await send_role_selector(member, channel, guild_config)
        await send_cosmetic_selector(member, channel, guild_config)

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
    user_id = str(member.id)
    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.gold())

    class RoleSelectView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in role_options.items():
                self.add_item(Button(label=data['label'], emoji=data['emoji'], custom_id=role_id))

        async def interaction_check(self, interaction: discord.Interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                timeout_msg = get_translated_mode_text(
                    guild_id,
                    user_id,
                    mode,
                    "timeout_role",
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
                    guild_id,
                    user_id,
                    mode,
                    "role_granted",
                    role=role.name,
                    user=member.mention
                )
                await interaction.response.send_message(role_msg, ephemeral=True)
                view.stop()  # ✅ Stop timeout on successful button click

                # 🌸 Continue to cosmetic selector
                cosmetic_shown = await send_cosmetic_selector(member, channel, guild_config)
                if not cosmetic_shown:
                    lang_code = all_languages["guilds"][guild_id]["users"].get(user_id, "en")
                    lang_map = all_languages["guilds"][guild_id]["languages"]
                    await send_final_welcome(member, channel, lang_code, lang_map)

            except Exception as e:
                print("⚠️ Role assign error:", e)
                await interaction.response.send_message("❗ I couldn’t assign that role. Please contact a mod.", ephemeral=True)

    # 💠 Assign button callbacks
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

    if not cosmetic_options:
        return False  # ⛔ Skip if no options

    class CosmeticRoleView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for role_id, data in cosmetic_options.items():
                self.add_item(Button(label=data['label'], emoji=data['emoji'], custom_id=role_id))
            self.add_item(Button(label="Skip", style=discord.ButtonStyle.secondary, custom_id="skip_cosmetic"))

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
            except:
                pass

    async def button_callback(interaction):
        selected = interaction.data["custom_id"]

        if selected == "skip_cosmetic":
            skip_msg = get_translated_mode_text(guild_id, user_id, mode, "cosmetic_skipped", user=member.mention)
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
                    print("Cosmetic role error:", e)

        # ✅ Stop the view so the timeout doesn't fire
        view.stop()

        # 🎉 Final welcome
        await send_final_welcome(member, channel, lang_code, lang_map)

    view = CosmeticRoleView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = button_callback

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
    embed_color = MODE_COLORS.get(mode, discord.Color.green())

    # ✨ Get translated mode-specific title
    welcome_title = get_translated_mode_text(guild_id, user_id, mode, "welcome_title")

    # 💬 Fallback to guild-configured welcome if mode text missing
    admin_welcome = lang_map.get(lang_code, {}).get("welcome")
    if admin_welcome:
        welcome_desc = admin_welcome.replace("{user}", member.mention)
    else:
        # 🧚 Fallback to translated mode-specific welcome
        raw_welcome_desc = get_translated_mode_text(
            guild_id, user_id, mode, "welcome_desc", fallback="Welcome, {user}!", user=member.mention
        )
        welcome_desc = raw_welcome_desc

    embed = discord.Embed(
        title=welcome_title,
        description=welcome_desc,
        color=embed_color
    )
    await channel.send(embed=embed)

# ========== FLUTTERKIN ==========

flutterkin_last_triggered = {}  # guild_id -> datetime

@bot.command(aliases=["babywish", "sparkleshift", "fluttertime", "snacktime", "glitterpuff", "bloop", "peekaboo", "glitzerfee", "petitpapillon", "chispa", "nibnib", "piccolina", "snugglezap", "twinkleflit" "pünktchen", "shirokuma", "cocotín", "cucciolotta", "snuzzlepuff", "sparkleboop", "miniblossom"])
async def whisper(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    now = datetime.now(timezone.utc)
    current_mode = guild_modes.get(guild_id, "dayform")

    # ⏳ 30-minute cooldown check
    last_used = flutterkin_last_triggered.get(guild_id)
    if last_used and (now - last_used).total_seconds() < 1800:
        minutes = int(30 - (now - last_used).total_seconds() // 60)
        await ctx.send(f"🕰️ Flutterkin is resting... please wait {minutes} more minutes!")
        return

    # 🦋 Activate Flutterkin only if not already in it
    if current_mode != "flutterkin":
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = "flutterkin"
        glitch_timestamps_by_guild[guild_id] = now
        await update_avatar_for_mode("flutterkin")

    # Update cooldown tracking and activity time
    flutterkin_last_triggered[guild_id] = now
    last_interaction_by_guild[guild_id] = now

    # 🍼 Intro message (translated and styled)
    intro = get_translated_mode_text(guild_id, user_id, "flutterkin", "language_confirm_desc", user=ctx.author.mention)
    await ctx.send(style_text(guild_id, intro))

    # 🗨️ Optional: Translate replied message
    if ctx.message.reference:
        try:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            content = replied_msg.content
            if not content:
                return await ctx.send("🧺 that message has no words to sparkle~ ✨")

            user_lang = get_user_language(guild_id, user_id)
            if not user_lang:
                return await ctx.send("🤔 you don’t got a chosen tongue yet!! go pick one!! 🐞")

            translated = translator.translate(content, dest=user_lang).text
            styled_translated = style_text(guild_id, translated)

            await ctx.send(f"💫 translated!! look!!:\n> {styled_translated}")

        except Exception as e:
            print("whisper translate error:", e)
            await ctx.send("😥 uh oh... i tried and it broke. no sparkle... try again?")

# ========== GENERAL COMMANDS ==========

@tree.command(name="help", description="📖 See the magical things Whisperling can do (for all users).")
async def help(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)

    # 🌒 Handle potential glitch trigger
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes.get(guild_id, "dayform")

    if maybe_glitch and current_mode in STANDARD_MODES:
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = maybe_glitch
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        await update_avatar_for_mode(maybe_glitch)
        current_mode = maybe_glitch

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
            "`!translate` – Translate a replied message into your chosen language\n"
            "`!chooselanguage` – Pick or change your preferred language\n"
            "`!... there is a hidden command ...` – If the winds allow, Flutterkin may awaken 🍼✨"
        ),
        inline=False
    )

    embed.set_footer(text=footer)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(aliases=["whispertranslate", "übersetzen", "traduire", "traducir"])
async def translate(ctx):
    # Check for replied message
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

    # 🌒 Trigger potential glitch form
    maybe_glitch = maybe_trigger_glitch(guild_id)
    current_mode = guild_modes[guild_id]

    if maybe_glitch and current_mode in STANDARD_MODES:
        previous_standard_mode_by_guild[guild_id] = current_mode
        guild_modes[guild_id] = maybe_glitch
        glitch_timestamps_by_guild[guild_id] = datetime.now(timezone.utc)
        await update_avatar_for_mode(maybe_glitch)

    # Update last interaction
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

        await ctx.send(embed=embed)

    except Exception as e:
        print("Translation error:", e)
        await ctx.send("❗ The winds failed to carry the words. Please try again.", delete_after=10)

@bot.command(aliases=["wählesprache", "choisirlalangue", "eligelenguaje"])
async def chooselanguage(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    member = ctx.author
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

    mode = guild_modes.get(guild_id, "dayform")
    embed_color = MODE_COLORS.get(mode, discord.Color.purple())
    voice = MODE_TEXTS_ENGLISH.get(mode, {})

    embed = discord.Embed(
        title=voice.get("language_intro_title", "🧚 Choose Your Whispering Tongue"),
        description=voice.get("language_intro_desc", "").replace("{user}", member.mention),
        color=embed_color
    )

    class LanguageView(View):
        def __init__(self):
            super().__init__(timeout=60)
            for code, data in lang_map.items():
                self.add_item(Button(label=data['name'], emoji=data['emoji'], custom_id=code))
            self.add_item(Button(label="❌ Cancel", style=discord.ButtonStyle.danger, custom_id="cancel"))

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

        async def on_timeout(self):
            try:
                await message.edit(content="⏳ Time ran out for language selection.", embed=None, view=None)
            except:
                pass

    async def button_callback(inter):
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

    message = await ctx.send(embed=embed, view=view)

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
