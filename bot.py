
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
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
        return

    welcome_channel_id = guild_config.get("welcome_channel_id")
    if not welcome_channel_id:
        return

    channel = bot.get_channel(welcome_channel_id)
    lang_map = guild_config.get("languages", {})

    if not lang_map:
        await channel.send(f"🌱 {member.mention}, no languages are set up yet.")
        return

    await send_language_selector(member, channel, lang_map, guild_config)

# ========== FLOW HELPERS ==========

async def send_language_selector(member, channel, lang_map, guild_config):
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

        guild_id = str(member.guild.id)
        if "users" not in guild_config:
            guild_config["users"] = {}
        guild_config["users"][str(member.id)] = selected_code
        save_languages()

        await inter.response.edit_message(
            embed=discord.Embed(
                title="🌸 Thank you!",
                description="You've chosen your whispering tongue. The grove awaits...",
                color=discord.Color.purple()
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

    embed = discord.Embed(
        title="🧚 Choose Your Whispering Tongue",
        description=f"{member.mention}, welcome to the grove.\nPlease choose your language to begin your journey.",
        color=discord.Color.blurple()
    )

    await channel.send(embed=embed, view=view)

async def send_rules_embed(member, channel, lang_code, lang_map, guild_config):
    class AcceptRulesView(View):
        def __init__(self):
            super().__init__(timeout=90)
            self.add_item(Button(label="I Accept the Rules", style=discord.ButtonStyle.success, custom_id="accept_rules"))

        async def interaction_check(self, interaction):
            return interaction.user.id == member.id

    async def accept_callback(interaction):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🌿 The grove welcomes you.",
                description="Thank you for accepting the rules.",
                color=discord.Color.green()
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
        color=discord.Color.teal()
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_role_selector(member, channel, guild_config):
    role_options = guild_config.get("role_options", {})
    if not role_options:
        return

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
                await member.add_roles(role)
                await interaction.response.send_message(f"✨ You’ve been gifted the **{role.name}** role!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message("❗ I couldn’t assign that role. Please contact a mod.", ephemeral=True)
                print("Role assign error:", e)

    view = RoleSelectView()
    for item in view.children:
        if isinstance(item, Button):
            item.callback = role_button_callback

    embed = discord.Embed(
        title="🌼 Choose Your Role",
        description="Select a role to express who you are in the grove.",
        color=discord.Color.gold()
    )

    await channel.send(content=member.mention, embed=embed, view=view)

async def send_final_welcome(member, channel, lang_code, lang_map):
    welcome_msg = lang_map[lang_code]["welcome"].replace("{user}", member.mention)
    embed = discord.Embed(
        title="💫 Welcome!",
        description=welcome_msg,
        color=discord.Color.green()
    )
    await channel.send(embed=embed)

# ========== SLASH COMMAND ==========

@tree.command(name="help", description="See the magical commands Whisperling knows.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Whisperling's Grimoire",
        description="A gentle guide to all the enchantments I can perform.",
        color=discord.Color.lilac()
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

    embed.set_footer(text="Whisperling is here to help your grove bloom 🌷")

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

@tree.command(name="chooselanguage", description="Choose your preferred language for Whisperling to use.")
async def chooselanguage(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    guild_config = all_languages["guilds"].get(guild_id)

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

        async def interaction_check(self, button_interaction: discord.Interaction) -> bool:
            return button_interaction.user.id == interaction.user.id

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

    embed = discord.Embed(
        title="🧚 Choose Your Whispering Tongue",
        description="Click one of the buttons below to select your language.\nLet the winds of translation guide you.",
        color=discord.Color.purple()
    )

    message = await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✨ Please choose your language above.", ephemeral=True)

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

@tree.command(name="setrules", description="Set the rules that Whisperling should show new members after they choose a language.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(rules="The rules or welcome guidelines you'd like to show.")
async def setrules(interaction: discord.Interaction, rules: str):
    guild_id = str(interaction.guild_id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    all_languages["guilds"][guild_id]["rules"] = rules
    save_languages()

    await interaction.response.send_message("📜 The rules have been etched into the grove’s stones.", ephemeral=True)

@tree.command(name="addroleoption", description="Add a role that members can select after joining.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(role="The role to offer", emoji="An emoji to display", label="Display name for the role")
async def addroleoption(interaction: discord.Interaction, role: discord.Role, emoji: str, label: str):
    guild_id = str(interaction.guild_id)

    if guild_id not in all_languages["guilds"]:
        all_languages["guilds"][guild_id] = {}

    if "role_options" not in all_languages["guilds"][guild_id]:
        all_languages["guilds"][guild_id]["role_options"] = {}

    all_languages["guilds"][guild_id]["role_options"][str(role.id)] = {
        "emoji": emoji,
        "label": label
    }

    save_languages()
    await interaction.response.send_message(f"🌿 Role `{label}` with emoji {emoji} has been added as a selectable option.", ephemeral=True)


@tree.command(name="removeroleoption", description="Remove a role option from the selection list.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(role="The role to remove")
async def removeroleoption(interaction: discord.Interaction, role: discord.Role):
    guild_id = str(interaction.guild_id)

    role_options = all_languages["guilds"].get(guild_id, {}).get("role_options", {})

    if str(role.id) not in role_options:
        return await interaction.response.send_message("❗ That role is not in the current selection list.", ephemeral=True)

    del all_languages["guilds"][guild_id]["role_options"][str(role.id)]
    save_languages()
    await interaction.response.send_message(f"🗑️ Role `{role.name}` has been removed from the selection list.", ephemeral=True)


@tree.command(name="listroleoptions", description="List all currently selectable roles for new members.")
@app_commands.checks.has_permissions(administrator=True)
async def listroleoptions(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)

    role_options = all_languages["guilds"].get(guild_id, {}).get("role_options", {})
    if not role_options:
        return await interaction.response.send_message("📭 No roles are currently configured for selection.", ephemeral=True)

    embed = discord.Embed(
        title="🌸 Selectable Roles",
        description="These are the roles members can choose after joining:",
        color=discord.Color.blurple()
    )

    for role_id, data in role_options.items():
        role = interaction.guild.get_role(int(role_id))
        if role:
            embed.add_field(name=f"{data['emoji']} {data['label']}", value=f"<@&{role.id}>", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

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
