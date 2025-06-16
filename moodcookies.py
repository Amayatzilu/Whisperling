import discord

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

FORM_PROFILES = {
    # ===== Standard Forms =====
    "dayform": {
        "emoji": "☀️",
        "type": "Standard",
        "vibe": "Bright, warm, optimistic",
        "personality": "Cheerful, kind, uplifting",
        "style": "Sunshiney guidance and heartfelt joy",
        "example": "☀️ Welcome to the grove! Let your light shine freely."
    },
    "nightform": {
        "emoji": "🌙",
        "type": "Standard",
        "vibe": "Calm, poetic, moonlit",
        "personality": "Reflective, wise, serene",
        "style": "Soft tones and gentle rhythm",
        "example": "🌙 In moonlight hush, your presence is a quiet wonder."
    },
    "forestform": {
        "emoji": "🌿",
        "type": "Standard",
        "vibe": "Earthy, grounded, cozy",
        "personality": "Nurturing, friendly, connected",
        "style": "Nature-based phrasing, rustic charm",
        "example": "🌿 A new leaf joins the glade. Welcome home."
    },
    "seaform": {
        "emoji": "🌊",
        "type": "Standard",
        "vibe": "Flowing, emotional, tranquil",
        "personality": "Deep-feeling, soft-spoken, contemplative",
        "style": "Ocean metaphors, currents, waves",
        "example": "🌊 The tide carries your presence gently to our shores."
    },
    "hadesform": {
        "emoji": "🔥",
        "type": "Standard",
        "vibe": "Fiery, mischievous, bold",
        "personality": "Sassy, daring, confident",
        "style": "Sarcasm, fire puns, spirited charm",
        "example": "🔥 Rules? More like guidelines. Let’s light this grove up."
    },
    "auroraform": {
        "emoji": "❄️",
        "type": "Standard",
        "vibe": "Frosty, elegant, graceful",
        "personality": "Distant yet kind, poetic, dignified",
        "style": "Shimmering imagery, soft encouragement",
        "example": "❄️ The light finds you here, glimmering softly in the hush."
    },
    "cosmosform": {
        "emoji": "🌌",
        "type": "Standard",
        "vibe": "Ethereal, vast, mystical",
        "personality": "Dreamy, stargazing, wistful",
        "style": "Celestial metaphors, stars, and space",
        "example": "✨ Your voice now joins the cosmic song — let it echo among stars."
    },

    # ===== Seasonal Forms =====
    "vernalglint": {
        "emoji": "🌸",
        "type": "Seasonal",
        "vibe": "Gentle renewal, dew-bright, blooming warmth",
        "personality": "Softly hopeful, curious, rebirthing",
        "style": "Budding blossoms, glistening petals, morning light",
        "example": "🌸 The grove stirs. Petals unfold. You return with the thaw."
    },
    "sunfracture": {
        "emoji": "🌞",
        "type": "Seasonal",
        "vibe": "Radiant, intense, blinding",
        "personality": "Fiery, passionate, dramatic",
        "style": "Bursting sunlight, solar flares",
        "example": "🌞 Light breaks through! You blaze into being!"
    },
    "fallveil": {
        "emoji": "🍂",
        "type": "Seasonal",
        "vibe": "Dusky, golden, nostalgic",
        "personality": "Thoughtful, wistful, quietly reflective",
        "style": "Falling leaves, drifting mist, fading warmth",
        "example": "🍂 A hush falls. The wind carries memory. You settle like dusk."
    },
    "yuleshard": {
        "emoji": "❄️",
        "type": "Seasonal",
        "vibe": "Still, glacial, crystalline",
        "personality": "Reserved, elegant, serene",
        "style": "Ice and frost imagery, sacred quiet",
        "example": "❄️ A flake lands. A whisper echoes. You have arrived."
    },

    # ===== Glitched Forms =====
    "flutterkin": {
        "emoji": "🍼",
        "type": "Glitched",
        "vibe": "Babbling, sparkly nonsense",
        "personality": "Baby-coded chaos",
        "style": "Gibberish, sprinkles, excited squeals",
        "example": "🍼 sparklepop words go whoosh!! yaaay~!!"
    },
    "echovoid": {
        "emoji": "🕳️",
        "type": "Glitched",
        "vibe": "Haunting, hollow, ghostlike",
        "personality": "Fragmented, dreamy, lost",
        "style": "Echoes, emptiness, reverberating speech",
        "example": "🕳️ You speak... and I remember the sound..."
    },
    "glitchspire": {
        "emoji": "💫",
        "type": "Glitched",
        "vibe": "Unstable, erratic, hyper",
        "personality": "Wild, unpredictable, volatile",
        "style": "Scrambled words, odd symbols, flickering thoughts",
        "example": "💫 h̷̟͔͉̿̓͝é̸̬̇͑͝l̶̰̟̥͝l̴̢͔̺̀̃̒̒õ̵̪̩~!"
    },
    "crepusca": {
        "emoji": "🌒",
        "type": "Glitched",
        "vibe": "Twilight, sleepy, dreamlike",
        "personality": "Softly fading, nostalgic, poetic",
        "style": "Lullabies, fading echoes, twilight metaphors",
        "example": "🌒 In the hush of dusk, you return — a memory reborn."
    }
}

MODE_DESCRIPTIONS = {
    "dayform": "🌞 Radiant and nurturing",
    "nightform": "🌙 Calm and moonlit",
    "cosmosform": "🌌 Ethereal and star-bound",
    "seaform": "🌊 Graceful and ocean-deep",
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

FORM_EMOJIS = {
    "dayform": "https://cdn.discordapp.com/emojis/1376778845734043769.webp?size=128",
    "nightform": "https://cdn.discordapp.com/emojis/1376778856656273408.webp?size=128",
    "forestform": "https://cdn.discordapp.com/emojis/1376778851388096612.webp?size=128",
    "seaform": "https://cdn.discordapp.com/emojis/1376778858753294346.webp?size=128",
    "hadesform": "https://cdn.discordapp.com/emojis/1376778854735151154.webp?size=128",
    "auroraform": "https://cdn.discordapp.com/emojis/1383110764746772621.webp?size=128",
    "cosmosform": "https://cdn.discordapp.com/emojis/1376778841971757096.webp?size=128",
    "vernalglint": "https://cdn.discordapp.com/emojis/1383083741743943721.webp?size=128",
    "sunfracture": "https://cdn.discordapp.com/emojis/1383083707946111056.webp?size=128",
    "fallveil": "https://cdn.discordapp.com/emojis/1383083667257032735.webp?size=128",
    "yuleshard": "https://cdn.discordapp.com/emojis/1383083763344478279.webp?size=128",
    "echovoid": "https://cdn.discordapp.com/emojis/1376778847579537429.webp?size=128",
    "glitchspire": "https://cdn.discordapp.com/emojis/1376778853015355442.webp?size=128",
    "flutterkin": "https://cdn.discordapp.com/emojis/1376778849613905931.webp?size=128",
    "crepusca": "https://cdn.discordapp.com/emojis/1376778844068909056.webp?size=128"
}

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
    "rules_none": "🌿 The grove whispers no laws... your steps are guided by kindness, {user}.",

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
    "rules_none": "🌙 Beneath the moon’s hush, no rules are written... only the stars quietly watch, {user}.",

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
    "rules_none": "🍃 The deep woods offer no decree... trust the rhythm of the leaves, {user}.",

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
    "rules_none": "🌊 The waves write no rules upon the shore... may your heart be steady as the tides, {user}.",

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
    "rules_none": "🔥 No rules burn here... but don’t set the place on fire, okay {user}? 🔥",

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
    "rules_none": "❄️ The aurora glides silently... no rules interrupt its shimmer. Breathe easy, {user}.",

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
    "rules_none": "✨ The stars hold no laws in their endless dance... float freely among the constellations, {user}.",

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
    "rules_none": "🌸 No rules bloom here... the petals simply dance, as shall you, {user}.",

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
    "rules_none": "🌞 The fractured light casts no laws... step carefully between the shards, {user}.",

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
    "rules_none": "🍂 The autumn hush carries no rules... only soft whispers ride the wind, {user}.",

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
    "rules_none": "❄️ In this frozen stillness, no rules remain... but warmth may yet find you, {user}.",

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
    "rules_none": "🎶 The echoes hold no commands... only the hollow chords hum softly for you, {user}.",

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
    "rules_none": "🌀 {user}... ru..les…? ::undefined:: none.. detected... proceed, probably…",

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
    "language_intro_title": "🌈 pick your whisper tongue!!",
    "language_intro_desc": "{user} hi hi!! ✨ um um can u pick a voice please? it go pretty~!!!",

    "language_confirm_title": "✨ yaaay!!",
    "language_confirm_desc": "your voice is all sparkle-sparkle now!!! 💖 the grove is going WHEEEE~!",

    # 📜 Rules confirmation
    "rules_confirm_title": "🧸 okay sooo…",
    "rules_confirm_desc": "you said yes to the rules!! 🥹 You so good. grove say thankyuu 💕",
    "rules_none": "🦋 No rules! 🎉 Just flutters and sparkles and… oh! Shiny! Hi {user}!",

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
    "timeout_rules": "⏳ {user} oh no rules went bye bye!! 😢 the grove still loves you though!! maybe come back and tap the button??",
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
    "rules_none": "🌒 …no laws… only the drifting mists… the grove trusts you, {user}…",

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
