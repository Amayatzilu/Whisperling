
import discord
from discord.ext import commands
from discord import app_commands
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

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)

    if not guild_config:
        print(f"No config for guild {guild_id}")
        return

    channel_id = guild_config.get("welcome_channel_id")
    if not channel_id:
        print(f"No welcome_channel_id set for guild {guild_id}")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"❌ Welcome channel with ID {channel_id} not found.")
        return

    lang_map = guild_config.get("languages", {})
    if not lang_map:
        await channel.send(f"🍃 {member.mention}, no languages are set up yet.")
        return

    emoji_list = [data["emoji"] for data in lang_map.values()]
    msg_lines = [f"🧚 Welcome, {member.mention}! Please choose your language by reacting:"]
    for code, data in lang_map.items():
        msg_lines.append(f"{data['emoji']} {data['name']}")
    msg = await channel.send("\n".join(msg_lines))

    for emoji in emoji_list:
        await msg.add_reaction(emoji)

    def check(reaction, user):
        return user == member and str(reaction.emoji) in emoji_list and reaction.message.id == msg.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
        selected_lang = None
        for code, data in lang_map.items():
            if data["emoji"] == str(reaction.emoji):
                selected_lang = code
                break

        if selected_lang:
            welcome_text = lang_map[selected_lang]["welcome"].replace("{user}", member.mention)
            await channel.send(welcome_text)

            if "users" not in all_languages["guilds"][guild_id]:
                all_languages["guilds"][guild_id]["users"] = {}

            all_languages["guilds"][guild_id]["users"][str(member.id)] = selected_lang
            save_languages()
        else:
            await channel.send(f"🍂 {member.mention}, a fairy misheard your whisper. Please try again.")

    except asyncio.TimeoutError:
        await channel.send(f"🕊️ {member.mention}, no language was chosen in time. The breeze will wait for you.")

# ========== SLASH COMMAND ==========
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

    try:
        result = translator.translate(content, dest=user_lang)
        await interaction.response.send_message(
    f"""✨ Whispered into `{user_lang}`:
> {result.text}""",
    ephemeral=True
)
    except Exception as e:
        print("Translation error:", e)
        await interaction.response.send_message("❗ The winds failed to carry the words. Please try again.", ephemeral=True)

@tree.command(name="setlanguage", description="Choose your preferred language for translations.")
@app_commands.describe(code="The language code you'd like to use.")
async def setlanguage(interaction: discord.Interaction, code: str):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    guild_config = all_languages["guilds"].get(guild_id)

    if not guild_config or "languages" not in guild_config or code not in guild_config["languages"]:
        return await interaction.response.send_message("❗ That language isn't available in this server.", ephemeral=True)

    if "users" not in guild_config:
        guild_config["users"] = {}

    guild_config["users"][user_id] = code
    save_languages()

    lang_name = guild_config["languages"][code]["name"]
    await interaction.response.send_message(f"✨ Your whispers will now be translated into **{lang_name}**.", ephemeral=True)

# ========== ADMIN COMMANDS ==========

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
    await ctx.send("🦋 Preloaded English, German, Spanish, and French.")


@bot.command(aliases=["setwillkommenskanal", "canalaccueil", "canalbienvenida"])
@commands.has_permissions(administrator=True)
async def setwelcomechannel(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    all_languages["guilds"][guild_id]["welcome_channel_id"] = channel.id
    save_languages()
    await ctx.send(f"🕊️ Welcome channel set to {channel.mention}")


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
    await ctx.send(f"✅ Updated welcome message for `{code}`.")


@bot.command(aliases=["sprachliste", "listelangues", "listaridiomas"])
@commands.has_permissions(administrator=True)
async def listlanguages(ctx):
    guild_id = str(ctx.guild.id)
    guild_config = all_languages["guilds"].get(guild_id)
    if not guild_config or "languages" not in guild_config or not guild_config["languages"]:
        await ctx.send("❗ No languages configured for this server.")
        return

    msg_lines = ["🌍 **Languages configured:**"]
    for code, data in guild_config["languages"].items():
        emoji = data.get("emoji", "❓")
        name = data.get("name", code)
        msg_lines.append(f"{emoji} `{code}` — {name}")
    await ctx.send("\n".join(msg_lines))


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
    await ctx.send(f"🗑️ Removed language `{code}`.")


@bot.command(aliases=["sprachenkürzel", "codeslangues", "codigosidioma"])
async def langcodes(ctx):
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

    msg_lines = ["🌐 **Common Language Codes** (for use with `/translate` or `!translate`)"]
    for code, name in codes.items():
        msg_lines.append(f"`{code}` — {name}")
    await ctx.send("\n".join(msg_lines))

bot.run(TOKEN)
