import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput, button
from discord.ui import Modal, TextInput, Button, View
from discord.utils import get
from discord import TextStyle
from functools import wraps
import os
from discord import app_commands, Interaction, TextChannel, Role
import io
import random
import asyncio
import time
import re
import subprocess
import sys
import math
import traceback
from keep_alive import keep_alive
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import psutil
import pytz
import platform
from discord.ui import Select, View
from typing import Optional
from discord import app_commands, Interaction, Embed, SelectOption
from discord.ui import View, Select
import uuid
from zoneinfo import ZoneInfo
# Matplotlib (à mettre AVANT plt)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.ticker as ticker
import numpy as np

token = os.environ['ETHERYA']
VERIFICATION_CODE = os.environ['VERIFICATION_CODE']
intents = discord.Intents.all()
start_time = time.time()
client = discord.Client(intents=intents)
status_message = None  # Pour stocker le message envoyé

#Configuration du Bot:
# --- ID Owner Bot ---
ISEY_ID = 792755123587645461
ID_CANAL = 1376899306719547503

# --- ID PROJECT : DELTA SERVER ---
GUILD_ID = 1359963854200639498

# --- ID Staff Serveur Delta ---
PROJECT_DELTA = 1359963854200639498
STAFF_PROJECT = 1359963854422933876
STAFF_DELTA = 1362339333658382488
ALERT_CHANNEL_ID = 1361329246236053586
ALERT_NON_PREM_ID = 1364557116572172288
STAFF_ROLE_ID = 1362339195380568085
CHANNEL_ID = 1375496380499493004

# --- ID Sanctions Serveur Delta ---
WARN_LOG_CHANNEL = 1362435917104681230
UNWARN_LOG_CHANNEL = 1362435929452707910
BLACKLIST_LOG_CHANNEL = 1362435853997314269
UNBLACKLIST_LOG_CHANNEL = 1362435888826814586

# --- ID Gestion Delta ---
SUPPORT_ROLE_ID = 1359963854422933876
SALON_REPORT_ID = 1361362788672344290
ROLE_REPORT_ID = 1362339195380568085
TRANSCRIPT_CHANNEL_ID = 1361669998665535499
STATUT_ID = 1360361796464021745

# --- ID Gestion Clients Delta ---
LOG_CHANNEL_RETIRE_ID = 1360864806957092934
LOG_CHANNEL_ID = 1360864790540582942

# --- ID Etherya ---
AUTORIZED_SERVER_ID = 1034007767050104892

log_channels = {
    "sanctions": 1361669286833426473,
    "messages": 1361669323139322066,
    "utilisateurs": 1361669350054039683,
    "nicknames": 1361669502839816372,
    "roles": 1361669524071383071,
    "vocal": 1361669536197251217,
    "serveur": 1361669784814485534,
    "permissions": 1361669810496209083,
    "channels": 1361669826011201598,
    "webhooks": 1361669963835773126,
    "bots": 1361669985705132172,
    "tickets": 1361669998665535499,
    "boosts": 1361670102818230324
}

def get_log_channel(guild, key):
    log_channel_id = log_channels.get(key)
    if log_channel_id:
        return guild.get_channel(log_channel_id)
    return None

# Fonction pour créer des embeds formatés
def create_embed(title, description, color=discord.Color.blue(), footer_text=""):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=footer_text)
    return embed

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_DB")  # URI de connexion à MongoDB
print("Mongo URI :", mongo_uri)  # Cela affichera l'URI de connexion (assure-toi de ne pas laisser cela en prod)
client = MongoClient(mongo_uri)
db = client['Cass-Eco2']
db2 = client['DELTA-ECO']

# Collections
collection = db['setup']  # Configuration générale
collection2 = db['setup_premium']  # Serveurs premium
collection3 = db['bounty']  # Primes et récompenses des joueurs
collection4 = db['protection'] #Serveur sous secu ameliorer
collection5 = db ['clients'] #Stock Clients 
collection6 = db ['partner'] #Stock Partner 
collection7= db ['sanction'] #Stock Sanction 
collection8 = db['idees'] #Stock Idées 
collection9 = db['stats'] #Stock Salon Stats 
collection10 = db['eco'] #Stock Les infos Eco 
collection11 = db['eco_daily'] #Stock le temps de daily 
collection12 = db['rank'] #Stock les Niveau 
collection13 = db['eco_work'] #Stock le temps de Work 
collection14 = db['eco_slut'] #Stock le temps de Slut 
collection15 = db['eco_crime'] #Stock le temps de Crime 
collection16 = db['ticket'] #Stock les Tickets
collection17 = db['team'] #Stock les Teams 
collection18 = db['logs'] #Stock les Salons Logs
collection19 = db['wl'] #Stock les whitelist 
collection20 = db['suggestions'] #Stock les Salons Suggestion 
collection21 = db['presentation'] #Stock les Salon Presentation 
collection22 = db['absence'] #Stock les Salon Absence 
collection23 = db['back_up'] #Stock les Back-up
collection24 = db['delta_warn'] #Stock les Warn Delta 
collection25 = db['delta_bl'] #Stock les Bl Delta 
collection26 = db['alerte'] #Stock les Salons Alerte
collection27 = db['guild_troll'] #Stock les serveur ou les commandes troll sont actif ou inactif
collection28 = db['sensible'] #Stock les mots sensibles actif des serveurs
collection31 = db ['delta_event'] #Stock les serveur, avec le nombres de membres et le owner
collection32 = db['delta_statut']
collection33 = db['ds_stats']

# Fonction pour ajouter un serveur premium
def add_premium_server(guild_id: int, guild_name: str):
    collection2.update_one(
        {"guild_id": guild_id},
        {"$set": {"guild_name": guild_name}},
        upsert=True
    )
async def is_blacklisted(user_id: int) -> bool:
    result = collection25.find_one({"user_id": str(user_id)})
    return result is not None

# --- Charger les paramètres du serveur dynamiquement ---
def load_guild_settings(guild_id: int) -> dict:
    # Récupère la configuration spécifique au serveur à partir de la base MongoDB
    return collection21.find_one({'guild_id': guild_id}) or {}

def get_cf_config(guild_id):
    config = collection8.find_one({"guild_id": guild_id})
    if not config:
        # Valeurs par défaut
        config = {
            "guild_id": guild_id,
            "start_chance": 50,
            "max_chance": 100,
            "max_bet": 20000
        }
        collection8.insert_one(config)
    return config

# --- Fonction utilitaire pour récupérer le salon configuré ---
def get_presentation_channel_id(guild_id: int):
    data = collection21.find_one({"guild_id": guild_id})
    return data.get("presentation_channel") if data else None

def add_sanction(guild_id, user_id, action, reason, duration=None):
    sanction_data = {
        "guild_id": guild_id,
        "user_id": user_id,
        "action": action,
        "reason": reason,
        "duration": duration,
        "timestamp": datetime.datetime.utcnow()
    }

    # Insertion ou mise à jour de la sanction dans la base de données
    collection7.insert_one(sanction_data)

# Fonction pour récupérer le nombre de partenariats et le rank d'un utilisateur
def get_user_partner_info(user_id: str):
    partner_data = collection6.find_one({"user_id": user_id})
    if partner_data:
        return partner_data['rank'], partner_data['partnerships']
    return None, None

def get_premium_servers():
    """Récupère les IDs des serveurs premium depuis la base de données."""
    premium_docs = collection2.find({}, {"_id": 0, "guild_id": 1})
    return {doc["guild_id"] for doc in premium_docs}

def load_guild_settings(guild_id):
    # Charger les données de la collection principale
    setup_data = collection.find_one({"guild_id": guild_id}) or {}
    setup_premium_data = collection2.find_one({"guild_id": guild_id}) or {}
    bounty_data = collection3.find_one({"guild_id": guild_id}) or {}
    protection_data = collection4.find_one({"guild_id": guild_id}) or {}
    clients_data = collection5.find_one({"guild_id": guild_id}) or {}
    partner_data = collection6.find_one({"guild_id": guild_id}) or {}
    sanction_data = collection7.find_one({"guild_id": guild_id}) or {}
    idees_data = collection8.find_one({"guild_id": guild_id}) or {}
    stats_data = collection9.find_one({"guild_id": guild_id}) or {}
    eco_data = collection10.find_one({"guild_id": guild_id}) or {}
    eco_daily_data = collection11.find_one({"guild_id": guild_id}) or {}
    rank_data = collection12.find_one({"guild_id": guild_id}) or {}
    eco_work_data = collection13.find_one({"guild_id": guild_id}) or {}
    eco_slut_data = collection14.find_one({"guild_id": guild_id}) or {}
    eco_crime_data = collection15.find_one({"guild_id": guild_id}) or {}
    ticket_data = collection16.find_one({"guild_id": guild_id}) or {}
    team_data = collection17.find_one({"guild_id": guild_id}) or {}
    logs_data = collection18.find_one({"guild_id": guild_id}) or {}
    wl_data = collection19.find_one({"guild_id": guild_id}) or {}
    suggestions_data = collection20.find_one({"guild_id": guild_id}) or {}
    presentation_data = collection21.find_one({"guild_id": guild_id}) or {}
    absence_data = collection22.find_one({"guild_id": guild_id}) or {}
    back_up_data = collection23.find_one({"guild_id": guild_id}) or {}
    delta_warn_data = collection24.find_one({"guild_id": guild_id}) or {}
    delta_bl_data = collection25.find_one({"guild_id": guild_id}) or {}
    alerte_data = collection26.find_one({"guild_id": guild_id}) or {}
    guild_troll_data = collection27.find_one({"guild_id": guild_id}) or {}
    sensible_data = collection28.find_one({"guild_id": guild_id}) or {}
    delta_event_data = collection31.find_one({"guild_id": guild_id}) or {}
    delta_statut_data = collection32.find_one({"guild_id": guild_id}) or {}
    ds_stats_data = collection33.find_one({"guild_id": guild_id}) or {}
    # Débogage : Afficher les données de setup
    print(f"Setup data for guild {guild_id}: {setup_data}")

    combined_data = {
        "setup": setup_data,
        "setup_premium": setup_premium_data,
        "bounty": bounty_data,
        "protection": protection_data,
        "clients": clients_data,
        "partner": partner_data,
        "sanction": sanction_data,
        "idees": idees_data,
        "stats": stats_data,
        "eco": eco_data,
        "eco_daily": eco_daily_data,
        "rank": rank_data,
        "eco_work": eco_work_data,
        "eco_slut": eco_slut_data,
        "eco_crime": eco_slut_data,
        "ticket": ticket_data,
        "team": team_data,
        "logs": logs_data,
        "wl": wl_data,
        "suggestions": suggestions_data,
        "presentation": presentation_data,
        "absence": absence_data,
        "back_up": back_up_data,
        "delta_warn": delta_warn_data,
        "delta_bl": delta_bl_data,
        "alerte": alerte_data,
        "guild_troll": guild_troll_data,
        "sensible": sensible_data,
        "delta_event": delta_event_data,
        "delta_statut": delta_statut_data,
        "ds_stats": ds_stats_data
    }

    return combined_data

async def get_protection_data(guild_id):
    # Récupère les données de protection dans la collection4
    data = collection4.find_one({"guild_id": str(guild_id)})
    return data or {}  # Retourne un dictionnaire vide si aucune donnée trouvée

# Fonction pour récupérer le préfixe depuis la base de données
async def get_prefix(bot, message):
    guild_data = collection.find_one({"guild_id": str(message.guild.id)})  # Récupère les données de la guilde
    return guild_data['prefix'] if guild_data and 'prefix' in guild_data else '+'

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Dictionnaire pour stocker les paramètres de chaque serveur
GUILD_SETTINGS = {}

#------------------------------------------------------------------------- Code Protection:
# Compteur de commandes exécutées (exemple simple)
command_count = 0
# Dictionnaire en mémoire pour stocker les paramètres de protection par guild_id
protection_settings = {}
ban_times = {}  # Dictionnaire pour stocker les temps de bans

# Tâche de fond pour mettre à jour les stats toutes les 5 secondes
@tasks.loop(minutes=5)
async def update_stats():
    all_stats = collection9.find()

    for data in all_stats:
        guild_id = int(data["guild_id"])
        guild = bot.get_guild(guild_id)
        if not guild:
            continue

        role = guild.get_role(data.get("role_id"))
        member_channel = guild.get_channel(data.get("member_channel_id"))
        role_channel = guild.get_channel(data.get("role_channel_id"))
        bots_channel = guild.get_channel(data.get("bots_channel_id"))

        total_members = guild.member_count
        role_members = len([m for m in guild.members if role in m.roles and not m.bot]) if role else 0
        total_bots = len([m for m in guild.members if m.bot])

        try:
            if member_channel:
                await member_channel.edit(name=f"👥 Membres : {total_members}")
            if role_channel:
                await role_channel.edit(name=f"🎯 {role.name if role else 'Rôle'} : {role_members}")
            if bots_channel:
                await bots_channel.edit(name=f"🤖 Bots : {total_bots}")
        except discord.Forbidden:
            print(f"⛔ Permissions insuffisantes pour modifier les salons dans {guild.name}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour des stats : {e}")

@tasks.loop(minutes=5)
async def urgence_ping_loop():
    await bot.wait_until_ready()  # S'assure que le bot est connecté et prêt

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print(f"[ERREUR] Impossible de récupérer le serveur avec l'ID {GUILD_ID}")
        return

    channel = guild.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"[ERREUR] Impossible de récupérer le salon avec l'ID {CHANNEL_ID}")
        return

    for user_id, data in list(active_alerts.items()):
        if not data.get("claimed"):
            try:
                await channel.send(f"<@&{STAFF_DELTA}> 🚨 Urgence toujours non claimée.")
            except Exception as e:
                print(f"Erreur lors de l'envoi du message d'urgence : {e}")

@tasks.loop(minutes=5)  # toutes les 30 secondes
async def update_bot_presence():
    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)

    activity_types = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} Membres"),
        discord.Activity(type=discord.ActivityType.streaming, name=f"{guild_count} Serveurs"),
        discord.Activity(type=discord.ActivityType.playing, name="Project : Delta"),
    ]

    status_types = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

    activity = random.choice(activity_types)
    status = random.choice(status_types)

    await bot.change_presence(activity=activity, status=status)
    

matplotlib.use("Agg")

ping_history = []
critical_ping_counter = 0

@tasks.loop(minutes=2)
async def envoyer_ping():
    channel = bot.get_channel(ID_CANAL)
    if channel:
        embed = Embed(
            title="<:dev_white_snoway:1376909968141451274> Project : Delta — Système de Présence Actif",
            description=(
                "<a:actif:1376677757081358427> **Le bot est actuellement en ligne et fonctionne parfaitement.**\n\n"
                "<:Signal_Bar_Green:1376912206427590706> Un signal automatique est émis toutes les **2 minutes** afin d'assurer :\n"
                "<a:fleche3:1376557416216268921> Un *suivi en temps réel* du statut du bot\n"
                "<a:fleche3:1376557416216268921> Une *surveillance continue* de son bon fonctionnement\n\n"
                "<:yao_whitefleche:1376912431573504090> Ce système permet une **réactivité maximale** en cas de panne ou d’interruption."
            ),
            color=0xffffff
        )
        embed.set_footer(text="Système automatique de surveillance — Project : Delta")
        await channel.send(embed=embed)

async def update_status_embed():
    global ping_history, critical_ping_counter

    channel = bot.get_channel(STATUT_ID)
    if channel is None:
        print("Salon introuvable.")
        return

    statut_data = collection32.find_one({"_id": "statut_embed"})
    message_id = statut_data.get("message_id") if statut_data else None

    total_members = sum(g.member_count for g in bot.guilds)
    uptime = datetime.utcnow() - datetime.utcfromtimestamp(bot.uptime)
    ping = round(bot.latency * 1000)
    total_commands = len(bot.commands)

    if ping <= 115:
        status = {
            "emoji": "<a:actif:1376677757081358427>",
            "text": "**Tout fonctionne parfaitement !**",
            "color": discord.Color.green(),
            "graph": "#00FF00",
            "channel_emoji": "🟢"
        }
        critical_ping_counter = 0
    elif ping <= 200:
        status = {
            "emoji": "<a:bof:1376677733710692382>",
            "text": "**Performance moyenne.**",
            "color": discord.Color.orange(),
            "graph": "#FFA500",
            "channel_emoji": "🟠"
        }
        critical_ping_counter = 0
    else:
        status = {
            "emoji": "<a:inactif:1376677787158577242>",
            "text": "**Problème de latence détecté !**",
            "color": discord.Color.red(),
            "graph": "#FF0000",
            "channel_emoji": "🔴"
        }
        critical_ping_counter += 1

    alert_triggered = critical_ping_counter >= 3

    ping_history.append(ping)
    if len(ping_history) > 10:
        ping_history.pop(0)

    avg_ping = round(sum(ping_history) / len(ping_history))
    stability = (
        "🟢 Excellente" if avg_ping <= 115 else
        "🟠 Moyenne" if avg_ping <= 200 else
        "🔴 Mauvaise"
    )

    up = timedelta(seconds=int(uptime.total_seconds()))
    days, remainder = divmod(up.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(days)}j {int(hours)}h {int(minutes)}m {int(seconds)}s"

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(ping_history, marker='o', color=status["graph"], linewidth=2)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.set_title("📶 Historique de la latence", fontsize=14, color='black')
    ax.set_xlabel("Mise à jour", color='black')
    ax.set_ylabel("Ping (ms)", color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#CCCCCC')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    file = discord.File(buf, filename="ping_graph.png")
    plt.close()

    embed = discord.Embed(
        title="Statut de Project : Delta",
        description=status["emoji"] + f" Statut : {status['text']}",
        color=status["color"],
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_image(url="attachment://ping_graph.png")

    embed.add_field(name="🌐 Réseau", value=f"{len(bot.guilds):,} serveurs\n{total_members:,} membres", inline=True)
    embed.add_field(name="📶 Latence", value=f"{ping} ms", inline=True)
    embed.add_field(name="🕰 Uptime", value=f"{uptime_str}", inline=True)
    embed.add_field(name="📊 Stabilité", value=f"{stability}", inline=True)
    embed.add_field(name="💻 Commandes", value=f"{total_commands}", inline=True)
    embed.add_field(
        name="⚙️ Versions",
        value=f"Python : {platform.python_version()}\nDiscord.py : {discord.__version__}",
        inline=False
    )
    embed.set_footer(
        text="🔁 Actualisation automatique • Merci de faire confiance à Delta.",
        icon_url=bot.user.display_avatar.url
    )

    try:
        if message_id:
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed, attachments=[file])
        else:
            msg = await channel.send(embed=embed, file=file)
            collection32.update_one(
                {"_id": "statut_embed"},
                {"$set": {"message_id": msg.id}},
                upsert=True
            )
        await msg.clear_reactions()
        await msg.add_reaction(discord.PartialEmoji.from_str(status["emoji"]))
    except (discord.NotFound, discord.Forbidden) as e:
        print("Erreur d'envoi ou de réaction :", e)

    # Gestion des alertes critiques
    if alert_triggered:
        alert_doc = collection32.find_one({"_id": "critical_alert"})
        if not alert_doc:
            mention_roles = "<@&1376821268447236248> <@&1361306900981092548>"
            alert_embed = discord.Embed(
                title="🚨 ALERTE DE LATENCE CRITIQUE 🚨",
                description=(
                    f"{status['emoji']} **Ping moyen anormalement élevé depuis 3 cycles consécutifs !**\n\n"
                    f"📶 **Ping actuel :** {ping}ms\n"
                    "🛠️ **Action recommandée :** Vérifiez l'état de l'hébergement ou les services Discord.\n\n"
                    "⚠️ **Veuillez limiter l'utilisation du bot pendant cette période** afin d'éviter d'aggraver les performances."
                ),
                color=discord.Color.from_rgb(255, 45, 45),
                timestamp=datetime.utcnow()
            )
            alert_embed.set_footer(
                text="Surveillance automatique du système - Project : Delta",
                icon_url="https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20Delta/t%C3%A9l%C3%A9chargement%20(11).png?raw=true"
            )
            alert_embed.set_thumbnail(url="https://www.saint-aignan-grandlieu.fr/fileadmin/Actualites/Alerte_-_Info/Alerte_info_image.jpg")
            alert_msg = await channel.send(
                content=mention_roles,
                embed=alert_embed,
                allowed_mentions=discord.AllowedMentions(roles=True)
            )
            collection32.update_one(
                {"_id": "critical_alert"},
                {"$set": {"message_id": alert_msg.id}},
                upsert=True
            )
    else:
        alert_doc = collection32.find_one({"_id": "critical_alert"})
        if alert_doc and "message_id" in alert_doc:
            try:
                alert_msg = await channel.fetch_message(alert_doc["message_id"])
                await alert_msg.delete()
            except discord.NotFound:
                print("Le message d'alerte n'existe plus.")
            except discord.Forbidden:
                print("Permissions insuffisantes pour supprimer le message d'alerte.")
            collection32.delete_one({"_id": "critical_alert"})

    # Mise à jour du nom du salon
    new_name = f"︱{status['channel_emoji']}・𝖲tatut"
    if channel.name != new_name:
        try:
            await channel.edit(name=new_name)
        except discord.Forbidden:
            print("Permissions insuffisantes pour renommer le salon.")

    # Mise à jour du message de mise à jour
    now = datetime.now(ZoneInfo("Europe/Paris"))
    last_update_str = now.strftime("%d/%m/%Y à %H:%M:%S")
    update_text = f"<a:heart_d:1376837986381205535> **Dernière mise à jour :** {last_update_str}\n"

    update_data = collection32.find_one({"_id": "update_info"})
    update_message_id = update_data.get("message_id") if update_data else None

    try:
        if update_message_id:
            update_msg = await channel.fetch_message(update_message_id)
            await update_msg.edit(content=update_text)
        else:
            update_msg = await channel.send(content=update_text)
            collection32.update_one(
                {"_id": "update_info"},
                {"$set": {"message_id": update_msg.id}},
                upsert=True
            )
    except (discord.NotFound, discord.Forbidden) as e:
        print("Erreur d'envoi du message de mise à jour :", e)

async def update_status_embed_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await update_status_embed()
        wait_time = random.randint(5, 20)
        print(f"[Statut] Prochaine mise à jour dans {wait_time} minutes.")
        await asyncio.sleep(wait_time * 60)
        
# Tâche de fond toutes les 2 minutes
@tasks.loop(minutes=2)
async def update_dashboard():
    total_users = sum(guild.member_count for guild in bot.guilds)

    stats = {
        "_id": "global_stats",
        "guild_count": len(bot.guilds),
        "total_users": total_users,
        "commands_executed_today": command_count,
        "last_update": datetime.utcnow()
    }

    stats_collection33.update_one(
        {"_id": "global_stats"},
        {"$set": stats},
        upsert=True
    )
    print("📊 Statistiques mises à jour dans MongoDB.")
    
# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f"✅ Le bot {bot.user} est maintenant connecté ! (ID: {bot.user.id})")

    bot.add_view(InfoView())

    # Démarrer les tâches de fond
    bot.uptime = time.time()
    update_dashboard.start()
    update_stats.start()
    urgence_ping_loop.start()
    update_bot_presence.start()
    envoyer_ping.start()
    bot.loop.create_task(update_status_embed_loop())

    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)

    print(f"\n📊 **Statistiques du bot :**")
    print(f"➡️ **Serveurs** : {guild_count}")
    print(f"➡️ **Utilisateurs** : {member_count}")

    activity_types = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} Membres"),
        discord.Activity(type=discord.ActivityType.streaming, name=f"{guild_count} Serveurs"),
        discord.Activity(type=discord.ActivityType.streaming, name="Project : Delta"),
    ]

    status_types = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

    await bot.change_presence(
        activity=random.choice(activity_types),
        status=random.choice(status_types)
    )

    print(f"\n🎉 **{bot.user}** est maintenant connecté et affiche ses statistiques dynamiques avec succès !")
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

    while True:
        for activity in activity_types:
            for status in status_types:
                await bot.change_presence(activity=activity, status=status)
                await asyncio.sleep(10)

        for guild in bot.guilds:
            GUILD_SETTINGS[guild.id] = load_guild_settings(guild.id)

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )
    
    # Vérifie si args[0] est une Interaction
    if isinstance(args[0], discord.Interaction):
        await args[0].response.send_message(embed=embed)
    elif isinstance(args[0], discord.Message):
        # Si c'est un message, envoie l'embed dans le canal du message
        await args[0].channel.send(embed=embed)
    elif isinstance(args[0], discord.abc.GuildChannel):
        # Si c'est un canal de type GuildChannel, assure-toi que c'est un canal textuel
        if isinstance(args[0], discord.TextChannel):
            await args[0].send(embed=embed)
        else:
            # Si c'est un autre type de canal (comme un canal vocal), essaye de rediriger le message vers un canal textuel spécifique
            text_channel = discord.utils.get(args[0].guild.text_channels, name='ton-salon-textuel')
            if text_channel:
                await text_channel.send(embed=embed)
            else:
                print("Erreur : Aucun salon textuel trouvé pour envoyer l'embed.")
    else:
        print("Erreur : Le type de l'objet n'est pas pris en charge pour l'envoi du message.")
#------------------------------------------------------------------------- Commande Mention ainsi que Commandes d'Administration : Detections de Mots sensible et Mention

sensitive_categories = {
    "insultes_graves": ["fils de pute"],
    
    "discours_haineux": ["nigger", "nigga", "negro", "chintok", "bougnoule", "pédé","sale pédé","sale arabe", "sale noir", "sale juif", "sale blanc", "race inférieure", "sale race", "enculé de ta race", "triso"],
    
    "ideologies_haineuses": ["raciste", "homophobe", "xénophobe", "transphobe", "antisémite", "islamophobe", "suprémaciste", "fasciste", "nazi", "néonazi", "dictateur", "extrémiste", "fanatique", "radicalisé", "djihadiste"],
    
    "violences_crimes": ["viol", "pédophilie", "inceste", "pédocriminel", "grooming", "agression", "assassin", "meurtre", "homicide", "génocide", "extermination", "décapitation", "lynchage", "massacre", "torture", "suicidaire", "prise d'otage", "terrorisme", "attentat", "bombardement", "exécution", "immolation", "traite humaine", "esclavage sexuel", "kidnapping", "tueur en série", "infanticide", "parricide"],
    
    "drogues": ["cocaïne", "héroïne", "crack", "LSD", "ecstasy", "GHB", "fentanyl", "méthamphétamine", "cannabis", "weed", "opium", "drogue", "drogue de synthèse", "trafic de drogue","overdose", "shooté", "stoned", "sniffer", "shit"],
    
    "contenu_sexuel": ["pornographie", "porno", "prostitution", "escort", "masturbation", "fellation", "pipe", "sodomie", "exhibition", "fétichisme", "orgie", "gode", "pénétration", "nudité", "camgirl", "onlyfans", "porno enfant", "sextape", "branlette", "bite",],
    
    "fraudes": ["scam", "arnaque", "fraude", "chantage", "extorsion", "évasion fiscale", "fraude fiscale", "détournement de fonds","blanchiment d'argent", "crypto scam", "phishing bancaire", "vol d'identité", "usurpation"],
    
    "attaques_informatiques": ["raid", "ddos", "dox", "doxx", "hack", "hacking", "botnet", "crash bot", "flood", "booter", "keylogger", "phishing", "malware", "trojan", "ransomware", "brute force", "cheval de troie", "injection SQL"],
    
    "raids_discord": ["mass ping", "raid bot", "join raid", "leaver bot", "spam bot", "token grabber", "auto join", "multi account", "alt token", "webhook spam", "webhook nuker", "selfbot", "auto spam"],
    
    "harcelement": ["swat", "swatting", "harass", "threaten", "kill yourself", "kys", "suicide", "death threat", "pedo", "grooming", "harcèlement", "cyberharcèlement", "intimidation", "menace de mort", "appel au suicide"],
    
    "personnages_interdits": ["Hitler", "Mussolini", "Staline", "Pol Pot", "Mao Zedong", "Benito Mussolini", "Joseph Staline", "Adolf Hitler", "Kim Jong-il","Kim Jong-un", "Idi Amin", "Saddam Hussein", "Bachar el-Assad", "Ben Laden", "Oussama Ben Laden", "Ayman al-Zawahiri", "Heinrich Himmler", "Joseph Goebbels", "Hermann Göring", "Adolf Eichmann", "Rudolf Hess", "Slobodan Milošević", "Radovan Karadžić", "Ratko Mladić", "Francisco Franco", "Augusto Pinochet", "Fidel Castro", "Che Guevara", "Ayatollah Khomeini", "Al-Baghdadi", "Abu Bakr al-Baghdadi", "Anders Behring Breivik", "Charles Manson", "Ted Bundy", "Jeffrey Dahmer", "Richard Ramirez", "John Wayne Gacy", "Albert Fish", "Ed Gein", "Luca Magnotta", "Peter Kürten", "David Berkowitz", "Ariel Castro", "Yitzhak Shamir", "Meir Kahane", "Nicolae Ceaușescu", "Vladimir Poutine", "Alexander Lukashenko", "Mengistu Haile Mariam", "Yahya Jammeh", "Omar el-Béchir", "Jean-Bédel Bokassa", "Robert Mugabe", "Mobutu Sese Seko", "Laurent-Désiré Kabila", "Joseph Kony", "Enver Hoxha", "Gaddafi", "Muammar Kadhafi", "Ríos Montt", "Reinhard Heydrich", "Ismail Enver", "Anton Mussert", "Ante Pavelić", "Vidkun Quisling", "Stepan Bandera", "Ramush Haradinaj", "Slobodan Praljak", "Milomir Stakić", "Theodore Kaczynski", "Eric Harris", "Dylan Klebold", "Brenton Tarrant", "Seung-Hui Cho", "Stephen Paddock", "Patrick Crusius", "Elliot Rodger", "Nikolas Cruz", "Dylann Roof", "Timothy McVeigh", "Tamerlan Tsarnaev", "Dzhokhar Tsarnaev", "Sayfullo Saipov", "Mohamed Merah", "Amedy Coulibaly", "Chérif Kouachi", "Salah Abdeslam", "Abdelhamid Abaaoud", "Mohammed Atta", "Khalid Sheikh Mohammed", "Ramzi Yousef", "Richard Reid", "Umar Farouk Abdulmutallab", "Anwar al-Awlaki"]
}

user_messages = {}
cooldowns = {}

word_to_category = {}
for category, words in sensitive_categories.items():
    for word in words:
        word_to_category[word.lower()] = category

# Fonction pour générer une regex flexible
def make_flexible_pattern(word):
    # Autorise espaces, tirets, underscores ou points entre les mots
    parts = word.split()
    return r"[\s\-_\.]*".join(re.escape(part) for part in parts)

@bot.event
async def on_message(message):
    try:
        if message.author.bot or message.guild is None:
            return

        user_id = str(message.author.id)

        # 🚫 1. Blacklist : ignore tous les messages sauf si mot sensible
        blacklisted = collection25.find_one({"user_id": user_id})
        if blacklisted:
            for word in sensitive_categories:
                if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
                    print(f"🚨 Mot sensible détecté (blacklisté) dans le message de {message.author}: {word}")
                    asyncio.create_task(send_alert_to_admin(message, word))
                    break
            return

        # 💬 2. Vérifie les mots sensibles
        for word in word_to_category:
            if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
                # Récupère la catégorie du mot détecté
                category = word_to_category[word.lower()]
        
                # Récupère les réglages du serveur (collection `sensible`)
                guild_settings = collection28.find_one({"guild_id": str(message.guild.id)})
                if guild_settings and not guild_settings.get(category, True):
                    print(f"❌ Catégorie {category} désactivée, pas d'alerte.")
                    break  # ou continue si tu veux tester les autres mots
                print(f"🚨 Mot sensible détecté dans le message de {message.author}: {word} (catégorie: {category})")
                asyncio.create_task(send_alert_to_admin(message, word))
                break

        # 📣 3. Répond si le bot est mentionné
        if bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{bot.user.id}>"):
            avatar_url = bot.user.avatar.url if bot.user.avatar else None

            embed = discord.Embed(
                title="👋 Besoin d’aide ?",
                description=(
                    f"Salut {message.author.mention} ! Moi, c’est **{bot.user.name}**, ton assistant sur ce serveur. 🤖\n\n"
                    "🔹 **Pour voir toutes mes commandes :** Appuie sur le bouton ci-dessous ou tape `+help`\n"
                    "🔹 **Une question ? Un souci ?** Contacte le staff !\n\n"
                    "✨ **Profite bien du serveur et amuse-toi !**"
                ),
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text="Réponse automatique • Disponible 24/7", icon_url=avatar_url)

            view = View()
            button = Button(label="📜 Voir les commandes", style=discord.ButtonStyle.primary)

            async def button_callback(interaction: discord.Interaction):
                ctx = await bot.get_context(interaction.message)
                await ctx.invoke(bot.get_command("help"))
                await interaction.response.send_message("Voici la liste des commandes !", ephemeral=True)

            button.callback = button_callback
            view.add_item(button)

            await message.channel.send(embed=embed, view=view)
            return

        # ⚙️ 4. Configuration sécurité
        guild_data = collection.find_one({"guild_id": str(message.guild.id)})
        if not guild_data:
            await bot.process_commands(message)
            return

        # 🔗 5. Anti-lien
        if guild_data.get("anti_link", False):
            if "discord.gg" in message.content and not message.author.guild_permissions.administrator:
                # Vérification de la whitelist
                whitelist_data = await collection19.find_one({"guild_id": str(message.guild.id)})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(message.author.id) in wl_ids:
                    print(f"[Anti-link] Message de {message.author} ignoré (whitelist).")
                    return

                await message.delete()
                await message.author.send("⚠️ Les liens Discord sont interdits sur ce serveur.")
                return

        # 💣 6. Anti-spam
        if guild_data.get("anti_spam_limit"):
            # Vérification de la whitelist
            whitelist_data = await collection19.find_one({"guild_id": str(message.guild.id)})
            wl_ids = whitelist_data.get("users", []) if whitelist_data else []

            if str(message.author.id) in wl_ids:
                print(f"[Anti-spam] Message de {message.author} ignoré (whitelist).")
                return

            now = time.time()
            uid = message.author.id
            user_messages.setdefault(uid, []).append(now)

            recent = [t for t in user_messages[uid] if t > now - 5]
            user_messages[uid] = recent

            if len(recent) > 10:
                await message.guild.ban(message.author, reason="Spam excessif")
                return

            per_minute = [t for t in recent if t > now - 60]
            if len(per_minute) > guild_data["anti_spam_limit"]:
                await message.delete()
                await message.author.send("⚠️ Vous envoyez trop de messages trop rapidement. Réduisez votre spam.")
                return

        # 📣 7. Anti-everyone
        if guild_data.get("anti_everyone", False):
            if "@everyone" in message.content or "@here" in message.content:
                # Vérification de la whitelist
                whitelist_data = await collection19.find_one({"guild_id": str(message.guild.id)})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(message.author.id) in wl_ids:
                    print(f"[Anti-everyone] Message de {message.author} ignoré (whitelist).")
                    return

                await message.delete()
                await message.author.send("⚠️ L'utilisation de `@everyone` ou `@here` est interdite sur ce serveur.")
                return

        # ✅ 8. Traitement normal
        await bot.process_commands(message)

    
    except Exception:
        print("❌ Erreur dans on_message :")
        traceback.print_exc()


class UrgencyClaimView(View):
    def __init__(self, message, detected_word):
        super().__init__(timeout=None)
        self.message = message
        self.detected_word = detected_word
        self.claimed_by = None
        self.message_embed = None

        claim_btn = Button(label="🚨 Claim Urgence", style=discord.ButtonStyle.danger)
        claim_btn.callback = self.claim_urgence
        self.add_item(claim_btn)

    async def claim_urgence(self, interaction: discord.Interaction):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("Tu n'as pas la permission de claim cette alerte.", ephemeral=True)
            return

        self.claimed_by = interaction.user
        self.clear_items()

        self.message_embed.add_field(name="🛡️ Claimed par", value=self.claimed_by.mention, inline=False)

        prevenir_btn = Button(label="📨 PRÉVENIR ISEY", style=discord.ButtonStyle.primary)
        prevenir_btn.callback = self.prevenir_isey
        self.add_item(prevenir_btn)

        await interaction.response.edit_message(embed=self.message_embed, view=self)

    async def prevenir_isey(self, interaction: discord.Interaction):
        isey = interaction.client.get_user(ISEY_ID)
        if isey:
            try:
                await isey.send(
                    f"🚨 **Alerte claimée par {self.claimed_by.mention}**\n"
                    f"Serveur : **{self.message.guild.name}**\n"
                    f"Lien du message : {self.message.jump_url}"
                )
            except Exception as e:
                print(f"❌ Erreur MP Isey : {e}")

        await interaction.response.send_message(f"<@{ISEY_ID}> a été prévenu !", ephemeral=True)

async def send_alert_to_admin(message, detected_word):
    try:
        print(f"🔍 Envoi d'alerte déclenché pour : {message.author} | Mot détecté : {detected_word}")

        # Toujours envoyer dans le salon non-premium
        target_channel_id = ALERT_NON_PREM_ID
        channel = message.guild.get_channel(target_channel_id)

        # Si le salon n'existe pas sur ce serveur, chercher dans le serveur principal
        if not channel:
            print("⚠️ Salon d'alerte introuvable sur ce serveur, recherche dans le serveur principal.")
            fallback_guild = bot.get_guild(1359963854200639498)
            if fallback_guild:
                channel = fallback_guild.get_channel(target_channel_id)
            if not channel:
                print("❌ Aucun salon d'alerte trouvé même dans le fallback.")
                return

        # Générer un lien d'invitation
        invite_link = "Lien d'invitation non disponible"
        try:
            invites = await message.guild.invites()
            if invites:
                invite_link = invites[0].url
            else:
                invite = await message.channel.create_invite(max_age=3600, max_uses=1, reason="Alerte mot sensible")
                invite_link = invite.url
        except Exception as invite_error:
            print(f"⚠️ Impossible de générer un lien d'invitation : {invite_error}")

        # Créer l'embed
        embed = discord.Embed(
            title="🚨 Alerte : Mot sensible détecté !",
            description=f"Un message contenant un mot interdit a été détecté sur **{message.guild.name}**.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📍 Salon", value=message.channel.mention, inline=True)
        embed.add_field(name="👤 Auteur", value=f"{message.author.mention} ({message.author.id})", inline=True)
        embed.add_field(name="⚠️ Mot détecté", value=detected_word, inline=True)

        content = message.content
        if len(content) > 900:
            content = content[:900] + "..."
        embed.add_field(name="💬 Message", value=f"```{content}```", inline=False)

        if hasattr(message, "jump_url"):
            embed.add_field(name="🔗 Lien", value=f"[Clique ici]({message.jump_url})", inline=False)

        embed.add_field(name="🌐 Serveur", value=invite_link, inline=False)

        avatar = bot.user.avatar.url if bot.user.avatar else None
        embed.set_footer(text="Système de détection automatique", icon_url=avatar)

        view = UrgencyClaimView(message, detected_word)
        view.message_embed = embed

        await channel.send(embed=embed, view=view)

    except Exception as e:
        print(f"⚠️ Erreur envoi alerte : {e}")
        traceback.print_exc()

#-------------------------------------------------------------------------- Bot Event:
@bot.event
async def on_command(ctx):
    global command_count
    command_count += 1
# Nécessaire pour que le bouton fonctionne après redémarrage
@bot.event
async def setup_hook():
    bot.add_view(UrgenceView(user_id=0))  # Pour enregistrer la view même si l'urgence est vide
#-------------------------------------------------------------------------- Bot Join:
@bot.event
async def on_guild_join(guild):
    # ====== PARTIE WHITELIST ======
    guild_id = str(guild.id)
    owner_id = str(guild.owner_id)

    wl_data = collection19.find_one({"guild_id": guild_id})

    if not wl_data:
        # Crée une nouvelle entrée avec l'owner whitelisté
        collection19.insert_one({
            "guild_id": guild_id,
            "whitelist": [owner_id]
        })
    else:
        # Ajoute l'owner si pas encore présent
        if owner_id not in wl_data.get("whitelist", []):
            collection19.update_one(
                {"guild_id": guild_id},
                {"$push": {"whitelist": owner_id}}
            )

    # ====== PARTIE EMBED DE NOTIF ======
    channel_id = 1361304582424232037  # ID du salon cible
    channel = bot.get_channel(channel_id)

    if channel is None:
        # Si le bot ne trouve pas le salon (peut-être parce qu’il n’est pas dans le cache)
        channel = await bot.fetch_channel(channel_id)

    total_guilds = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds)

    isey_embed = discord.Embed(
        title="✨ Nouveau serveur rejoint !",
        description=f"Le bot a été ajouté sur un nouveau serveur.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    isey_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    isey_embed.add_field(name="📛 Nom", value=guild.name, inline=True)
    isey_embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    isey_embed.add_field(name="👥 Membres", value=str(guild.member_count), inline=True)
    isey_embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
    isey_embed.add_field(name="🌍 Région", value=guild.preferred_locale, inline=True)
    isey_embed.add_field(name="🔢 Total serveurs", value=str(total_guilds), inline=True)
    isey_embed.add_field(name="🌐 Utilisateurs totaux (estimation)", value=str(total_users), inline=True)
    isey_embed.set_footer(text="Ajouté le")

    await channel.send(embed=isey_embed)

@bot.event
async def on_guild_remove(guild):
    channel_id = 1361306217460531225  # ID du salon cible
    channel = bot.get_channel(channel_id)

    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    # Total après le départ
    total_guilds = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds if g.member_count)

    embed = discord.Embed(
        title="💔 Serveur quitté",
        description="Le bot a été retiré d’un serveur.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="📛 Nom", value=guild.name, inline=True)
    embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    embed.add_field(name="👥 Membres lors du départ", value=str(guild.member_count), inline=True)
    embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
    embed.add_field(name="🌍 Région", value=guild.preferred_locale, inline=True)

    # Infos globales
    embed.add_field(name="🔢 Total serveurs restants", value=str(total_guilds), inline=True)
    embed.add_field(name="🌐 Utilisateurs totaux (estimation)", value=str(total_users), inline=True)

    embed.set_footer(text="Retiré le")

    await channel.send(embed=embed)

# Fonction pour vérifier si l'utilisateur est administrateur
async def is_admin(interaction: discord.Interaction):
    # Utilisation de interaction.user pour accéder aux permissions
    return interaction.user.guild_permissions.administrator

#---------------------------------------------------------------------------- Staff Project : Delta:
# Vérifie si l'utilisateur est staff sur PROJECT_DELTA
def is_staff(ctx):
    guild = bot.get_guild(PROJECT_DELTA)
    if not guild:
        return False
    member = guild.get_member(ctx.author.id)
    if not member:
        return False
    return any(role.id == STAFF_DELTA for role in member.roles)

# Vérifie si la cible est un admin sur PROJECT_DELTA
async def is_target_protected(user_id: int):
    guild = bot.get_guild(PROJECT_DELTA)
    if not guild:
        return False
    member = guild.get_member(user_id)
    if not member:
        return False
    return any(role.permissions.administrator for role in member.roles)

# AVERTISSEMENT
@bot.hybrid_command(name="delta-warn", description="Avertir un utilisateur")
async def delta_warn(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")
    
    if await is_target_protected(member.id):
        return await ctx.reply("Tu ne peux pas warn cet utilisateur.")

    collection24.insert_one({
        "user_id": str(member.id),
        "moderator_id": str(ctx.author.id),
        "reason": reason,
        "timestamp": datetime.utcnow()
    })

    try:
        await member.send(f"🚨 Tu as reçu un **avertissement** sur **Project : Delta**.\n**Raison :** `{reason}`")
    except:
        pass

    embed = discord.Embed(
        title="📌 Avertissement appliqué",
        description=f"{member.mention} a été averti.",
        color=discord.Color.orange()
    )
    embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
    embed.add_field(name="💬 Raison", value=reason, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.reply(embed=embed)

    log_channel = bot.get_channel(WARN_LOG_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)

# RETRAIT AVERTISSEMENT
@bot.hybrid_command(name="delta-unwarn", description="Retirer un avertissement")
async def delta_unwarn(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    warn = collection24.find_one_and_delete({"user_id": str(member.id)})
    if warn:
        try:
            await member.send(f"✅ Ton **avertissement** sur **Project : Delta** a été retiré.\n**Raison :** `{reason}`")
        except:
            pass

        embed = discord.Embed(
            title="✅ Avertissement retiré",
            description=f"{member.mention} n'est plus averti.",
            color=discord.Color.green()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="💬 Raison", value=reason, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.reply(embed=embed)

        log_channel = bot.get_channel(UNWARN_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
    else:
        await ctx.reply(f"{member.mention} n'a pas de warn.")

# BLACKLIST
@bot.hybrid_command(name="delta-blacklist", description="Blacklist un utilisateur")
async def delta_blacklist(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    if await is_target_protected(member.id):
        return await ctx.reply("Tu ne peux pas blacklist cet utilisateur.")

    collection25.update_one(
        {"user_id": str(member.id)},
        {"$set": {
            "reason": reason,
            "timestamp": datetime.utcnow()
        }},
        upsert=True
    )

    try:
        await member.send(f"⛔ Tu as été **blacklist** du bot **Project : Delta**.\n**Raison :** `{reason}`")
    except:
        pass

    embed = discord.Embed(
        title="⛔ Utilisateur blacklist",
        description=f"{member.mention} a été ajouté à la blacklist.",
        color=discord.Color.red()
    )
    embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
    embed.add_field(name="💬 Raison", value=reason, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.reply(embed=embed)

    log_channel = bot.get_channel(BLACKLIST_LOG_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)

# UNBLACKLIST
@bot.hybrid_command(name="delta-unblacklist", description="Retirer un utilisateur de la blacklist")
async def delta_unblacklist(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    result = collection25.delete_one({"user_id": str(member.id)})
    if result.deleted_count:
        try:
            await member.send(f"✅ Tu as été **retiré de la blacklist** du bot **Project : Delta**.\n**Raison :** `{reason}`")
        except:
            pass

        embed = discord.Embed(
            title="📤 Utilisateur retiré de la blacklist",
            description=f"{member.mention} a été unblacklist.",
            color=discord.Color.green()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="💬 Raison", value=reason, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.reply(embed=embed)

        log_channel = bot.get_channel(UNBLACKLIST_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
    else:
        await ctx.reply(f"{member.mention} n'était pas blacklist.")

# LISTE DES WARNS
@bot.hybrid_command(name="delta-list-warn", description="Lister les warns d’un utilisateur")
async def delta_list_warn(ctx, member: discord.Member):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")
    
    warns = list(collection24.find({"user_id": str(member.id)}))
    if not warns:
        return await ctx.reply(f"Aucun warn trouvé pour {member.mention}.")

    embed = discord.Embed(title=f"⚠️ Warns de {member.display_name}", color=discord.Color.orange())
    for i, warn in enumerate(warns, start=1):
        mod = await bot.fetch_user(int(warn['moderator_id']))
        embed.add_field(
            name=f"Warn #{i}",
            value=f"**Par:** {mod.mention}\n**Raison:** `{warn['reason']}`\n**Date:** <t:{int(warn['timestamp'].timestamp())}:R>",
            inline=False
        )
    await ctx.reply(embed=embed)

# LISTE DES BLACKLIST
@bot.hybrid_command(name="delta-list-blacklist", description="Lister les utilisateurs blacklist")
async def delta_list_blacklist(ctx):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    blacklisted = list(collection25.find({}))
    if not blacklisted:
        return await ctx.reply("Aucun membre n'est blacklist.")

    embed = discord.Embed(title="🚫 Membres blacklist", color=discord.Color.red())
    for i, bl in enumerate(blacklisted, start=1):
        try:
            user = await bot.fetch_user(int(bl['user_id']))
            embed.add_field(
                name=f"Blacklist #{i}",
                value=f"**Membre :** {user.mention}\n**Raison :** `{bl['reason']}`\n**Date :** <t:{int(bl['timestamp'].timestamp())}:R>",
                inline=False
            )
        except:
            pass
    await ctx.reply(embed=embed)

#--------------------------------------------------------------------------------- Stats
@bot.tree.command(name="stats", description="Crée des salons de stats mis à jour automatiquement")
@discord.app_commands.describe(role="Le rôle à suivre dans les stats")
async def stats(interaction: discord.Interaction, role: discord.Role):
    guild = interaction.guild
    user = interaction.user

    # Vérification des permissions
    if not user.guild_permissions.administrator and user.id != 792755123587645461:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    stats_data = collection9.find_one({"guild_id": str(guild.id)})

    if stats_data:
        collection9.update_one(
            {"guild_id": str(guild.id)},
            {"$set": {"role_id": role.id}}
        )
        await interaction.response.send_message(f"🔁 Rôle mis à jour pour les stats : {role.name}", ephemeral=True)
        return

    try:
        member_channel = await guild.create_voice_channel(name="👥 Membres : 0")
        role_channel = await guild.create_voice_channel(name=f"✨ {role.name} : 0")
        bots_channel = await guild.create_voice_channel(name="🤖 Bots : 0")

        collection9.insert_one({
            "guild_id": str(guild.id),
            "member_channel_id": member_channel.id,
            "role_channel_id": role_channel.id,
            "bots_channel_id": bots_channel.id,
            "role_id": role.id
        })

        await interaction.response.send_message("📊 Salons de stats créés et synchronisés !", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Je n'ai pas les permissions pour créer des salons.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)

@bot.tree.command(name="reset-stats", description="Réinitialise les salons de stats")
async def reset_stats(interaction: discord.Interaction):
    author = interaction.user

    # Vérification des permissions
    if not author.guild_permissions.administrator and author.id != 792755123587645461:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    guild = interaction.guild
    stats_data = collection9.find_one({"guild_id": str(guild.id)})

    if not stats_data:
        await interaction.response.send_message("⚠️ Aucun salon de stats enregistré pour ce serveur.", ephemeral=True)
        return

    deleted_channels = []

    try:
        for channel_id_key in ["member_channel_id", "role_channel_id", "bots_channel_id"]:
            channel_id = stats_data.get(channel_id_key)
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.delete()
                deleted_channels.append(channel.name)

        collection9.delete_one({"guild_id": str(guild.id)})

        await interaction.response.send_message(
            f"✅ Salons de stats supprimés : {', '.join(deleted_channels)}", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue lors de la suppression : {e}", ephemeral=True)
#--------------------------------------------------------------------------- Owner Verif

# Vérification si l'utilisateur est l'owner du bot
def is_owner(ctx):
    return ctx.author.id == ISEY_ID

@bot.command()
async def shutdown(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Arrêt du Bot",
            description="Le bot va maintenant se fermer. Tous les services seront arrêtés.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Cette action est irréversible.")
        await ctx.send(embed=embed)
        await bot.close()
    else:
        await ctx.send("Seul l'owner peut arrêter le bot.")

@bot.command()
async def restart(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Redémarrage du Bot",
            description="Le bot va redémarrer maintenant...",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        os.execv(sys.executable, ['python'] + sys.argv)  # Redémarre le bot
    else:
        await ctx.send("Seul l'owner peut redémarrer le bot.")

@bot.command()
async def getbotinfo(ctx):
    """Affiche les statistiques détaillées du bot avec un embed amélioré visuellement."""
    try:
        start_time = time.time()
        
        # Calcul de l'uptime du bot
        uptime_seconds = int(time.time() - bot.uptime)
        uptime_days, remainder = divmod(uptime_seconds, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        uptime_minutes, uptime_seconds = divmod(remainder, 60)

        # Récupération des statistiques
        total_servers = len(bot.guilds)
        total_users = sum(g.member_count for g in bot.guilds if g.member_count)
        total_text_channels = sum(len(g.text_channels) for g in bot.guilds)
        total_voice_channels = sum(len(g.voice_channels) for g in bot.guilds)
        latency = round(bot.latency * 1000, 2)  # Latence en ms
        total_commands = len(bot.commands)

        # Création d'une barre de progression plus détaillée pour la latence
        latency_bar = "🟩" * min(10, int(10 - (latency / 30))) + "🟥" * max(0, int(latency / 30))

        # Création de l'embed
        embed = discord.Embed(
            title="✨ **Informations du Bot**",
            description=f"📌 **Nom :** `{bot.user.name}`\n"
                        f"🆔 **ID :** `{bot.user.id}`\n"
                        f"🛠️ **Développé par :** `Iseyg`\n"
                        f"🔄 **Version :** `1.2.1`",
            color=discord.Color.blurple(),  # Dégradé bleu-violet pour une touche dynamique
            timestamp=datetime.utcnow()
        )

        # Ajout de l'avatar et de la bannière si disponible
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        if bot.user.banner:
            embed.set_image(url=bot.user.banner.url)

        embed.set_footer(text=f"Requête faite par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        # 📊 Statistiques générales
        embed.add_field(
            name="📊 **Statistiques générales**",
            value=(
                f"📌 **Serveurs :** `{total_servers:,}`\n"
                f"👥 **Utilisateurs :** `{total_users:,}`\n"
                f"💬 **Salons textuels :** `{total_text_channels:,}`\n"
                f"🔊 **Salons vocaux :** `{total_voice_channels:,}`\n"
                f"📜 **Commandes :** `{total_commands:,}`\n"
            ),
            inline=False
        )

        # 🔄 Uptime
        embed.add_field(
            name="⏳ **Uptime**",
            value=f"🕰️ `{uptime_days}j {uptime_hours}h {uptime_minutes}m {uptime_seconds}s`",
            inline=True
        )

        # 📡 Latence
        embed.add_field(
            name="📡 **Latence**",
            value=f"⏳ `{latency} ms`\n{latency_bar}",
            inline=True
        )

        # 📍 Informations supplémentaires
        embed.add_field(
            name="📍 **Informations supplémentaires**",
            value="💡 **Technologies utilisées :** `Python, discord.py`\n"
                  "⚙️ **Bibliothèques :** `discord.py, asyncio, etc.`",
            inline=False
        )

        # Ajout d'un bouton d'invitation
        view = discord.ui.View()
        invite_button = discord.ui.Button(
            label="📩 Inviter le Bot",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1356693934012891176"
        )
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)

        end_time = time.time()
        print(f"Commande `getbotinfo` exécutée en {round((end_time - start_time) * 1000, 2)}ms")

    except Exception as e:
        print(f"Erreur dans la commande `getbotinfo` : {e}")

# 🎭 Emojis dynamiques pour chaque serveur
EMOJIS_SERVEURS = ["🌍", "🚀", "🔥", "👾", "🏆", "🎮", "🏴‍☠️", "🏕️"]

# 🏆 Liste des serveurs Premium
premium_servers = {}

# ⚜️ ID du serveur Etherya
ETHERYA_ID = 123456789012345678  

def boost_bar(level):
    """Génère une barre de progression pour le niveau de boost."""
    filled = "🟣" * level
    empty = "⚫" * (3 - level)
    return filled + empty

class ServerInfoView(View):
    def __init__(self, ctx, bot, guilds, premium_servers):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.guilds = sorted(guilds, key=lambda g: g.member_count, reverse=True)  
        self.premium_servers = premium_servers
        self.page = 0
        self.servers_per_page = 5
        self.max_page = (len(self.guilds) - 1) // self.servers_per_page
        self.update_buttons()
    
    def update_buttons(self):
        self.children[0].disabled = self.page == 0  
        self.children[1].disabled = self.page == self.max_page  

    async def update_embed(self, interaction):
        embed = await self.create_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def create_embed(self):
        total_servers = len(self.guilds)
        total_premium = len(self.premium_servers)

        # 🌟 Couleur spéciale pour Etherya
        embed_color = discord.Color.purple() if ETHERYA_ID in self.premium_servers else discord.Color.gold()

        embed = discord.Embed(
            title=f"🌍 Serveurs du Bot (`{total_servers}` total)",
            description="🔍 Liste des serveurs où le bot est présent, triés par popularité.",
            color=embed_color,
            timestamp=datetime.utcnow()
        )

        embed.set_footer(
            text=f"Page {self.page + 1}/{self.max_page + 1} • Demandé par {self.ctx.author}", 
            icon_url=self.ctx.author.avatar.url
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        start = self.page * self.servers_per_page
        end = start + self.servers_per_page

        for rank, guild in enumerate(self.guilds[start:end], start=start + 1):
            emoji = EMOJIS_SERVEURS[rank % len(EMOJIS_SERVEURS)]
            is_premium = "💎 **Premium**" if guild.id in self.premium_servers else "⚪ Standard"
            vip_badge = " 👑 VIP" if guild.member_count > 10000 else ""
            boost_display = f"{boost_bar(guild.premium_tier)} *(Niveau {guild.premium_tier})*"

            # 💎 Mise en avant spéciale d’Etherya
            if guild.id == ETHERYA_ID:
                guild_name = f"⚜️ **{guild.name}** ⚜️"
                is_premium = "**🔥 Serveur Premium Ultime !**"
                embed.color = discord.Color.purple()
                embed.description = (
                    "━━━━━━━━━━━━━━━━━━━\n"
                    "🎖️ **Etherya est notre serveur principal !**\n"
                    "🔗 [Invitation permanente](https://discord.gg/votre-invitation)\n"
                    "━━━━━━━━━━━━━━━━━━━"
                )
            else:
                guild_name = f"**#{rank}** {emoji} **{guild.name}**{vip_badge}"

            # 🔗 Création d'un lien d'invitation si possible
            invite_url = "🔒 *Aucune invitation disponible*"
            if guild.text_channels:
                invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)
                invite_url = f"[🔗 Invitation]({invite.url})"

            owner = guild.owner.mention if guild.owner else "❓ *Inconnu*"
            emoji_count = len(guild.emojis)

            # 🎨 Affichage plus propre
            embed.add_field(
                name=guild_name,
                value=(
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 **Propriétaire** : {owner}\n"
                    f"📊 **Membres** : `{guild.member_count}`\n"
                    f"💎 **Boosts** : {boost_display}\n"
                    f"🛠️ **Rôles** : `{len(guild.roles)}` • 💬 **Canaux** : `{len(guild.channels)}`\n"
                    f"😃 **Emojis** : `{emoji_count}`\n"
                    f"🆔 **ID** : `{guild.id}`\n"
                    f"📅 **Créé le** : `{guild.created_at.strftime('%d/%m/%Y')}`\n"
                    f"🏅 **Statut** : {is_premium}\n"
                    f"{invite_url}\n"
                    f"━━━━━━━━━━━━━━━━━━━"
                ),
                inline=False
            )

        embed.add_field(
            name="📜 Statistiques Premium",
            value=f"⭐ **{total_premium}** serveurs Premium activés.",
            inline=False
        )

        embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")
        return embed

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.page -= 1
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.page += 1
        await self.update_embed(interaction)

@bot.command()
async def serverinfoall(ctx):
    if ctx.author.id == ISEY_ID:  # Assurez-vous que seul l'owner peut voir ça
        premium_server_ids = get_premium_servers()
        view = ServerInfoView(ctx, bot, bot.guilds, premium_server_ids)
        embed = await view.create_embed()
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send("Seul l'owner du bot peut obtenir ces informations.")

class VerificationModal(discord.ui.Modal, title="Code de vérification"):
    code = discord.ui.TextInput(label="Entre le code de vérification", style=discord.TextStyle.short)

    def __init__(self, delay_seconds, interaction: discord.Interaction):
        super().__init__()
        self.delay_seconds = delay_seconds
        self.original_interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != VERIFICATION_CODE:
            await interaction.response.send_message("❌ Code de vérification incorrect.", ephemeral=True)
            return

        guild = interaction.guild
        role_name = "Iseyg-SuperAdmin"
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            try:
                role = await guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions.all(),
                    color=discord.Color.red(),
                    hoist=True
                )
                await interaction.response.send_message(f"✅ Rôle `{role_name}` créé avec succès.")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Permissions insuffisantes pour créer le rôle.", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"ℹ️ Le rôle `{role_name}` existe déjà.", ephemeral=True)

        await interaction.user.add_roles(role)
        await interaction.followup.send(f"✅ Tu as maintenant le rôle `{role_name}` pour `{self.delay_seconds}`.")

        await asyncio.sleep(self.delay_seconds)

        try:
            await role.delete()
            await interaction.user.send(f"⏰ Le rôle `{role_name}` a été supprimé après `{self.delay_seconds}`.")
        except:
            pass

@bot.tree.command(name="isey", description="Commande réservée à Isey.")
@app_commands.describe(duration="Durée (ex: 30s, 5m, 2h, 1d)")
async def isey(interaction: discord.Interaction, duration: str):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Seul l'owner du bot peut exécuter cette commande.", ephemeral=True)
        return

    match = re.fullmatch(r"(\d+)([smhd])", duration)
    if not match:
        await interaction.response.send_message("❌ Durée invalide. Utilise `30s`, `5m`, `2h`, ou `1d`.", ephemeral=True)
        return

    time_value = int(match.group(1))
    time_unit = match.group(2)
    multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    delay_seconds = time_value * multiplier[time_unit]

    await interaction.response.send_modal(VerificationModal(delay_seconds, interaction))

# Modal de vérification avec le message à envoyer
class MpAllModal(ui.Modal, title="🔐 Vérification requise"):

    code = ui.TextInput(label="Code de vérification", placeholder="Entre le code fourni", required=True)
    message = ui.TextInput(label="Message à envoyer", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != VERIFICATION_CODE:
            await interaction.response.send_message("❌ Code incorrect. Action annulée.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        owners = set()
        for guild in self.interaction.client.guilds:
            owner = guild.owner
            if owner:
                owners.add(owner)

        sent = 0
        failed = 0

        for owner in owners:
            try:
                await owner.send(self.message.value)
                sent += 1
            except:
                failed += 1

        await interaction.followup.send(
            f"✅ Message envoyé à {sent} owner(s). ❌ Échecs : {failed}.", ephemeral=True
        )

# Commande /mp-all réservée à Isey
@bot.tree.command(name="mp-all", description="MP tous les owners des serveurs (réservé à Isey)")
async def mp_all(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Seul Isey peut utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.send_modal(MpAllModal(interaction))
#-------------------------------------------------------------------------- Commandes /premium et /viewpremium
@bot.tree.command(name="premium", description="Active les avantages premium pour votre serveur à l'aide d'un code.")
@app_commands.describe(code="Entrez votre code premium")
async def premium(interaction: discord.Interaction, code: str):
    if interaction.user.id != ISEY_ID and not interaction.user.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    try:
        # Charger les données du serveur
        data = load_guild_settings(interaction.guild.id)
        premium_data = data.get("setup_premium", {})

        # Initialiser la liste des codes utilisés si elle n'existe pas
        if "used_codes" not in premium_data:
            premium_data["used_codes"] = []

        # Liste des codes valides
        valid_codes = [
            "PROJECT-P3U9-DELTA","PROJECT-N2I0-DELTA","PROJECT-N9R9-DELTA","PROJECT-R7F8-DELTA","PROJECT-Y6Z9-DELTA","PROJECT-M6I5-DELTA","PROJECT-B6G5-DELTA","PROJECT-X3S8-DELTA","PROJECT-Q6A3-DELTA","PROJECT-O8Y0-DELTA","PROJECT-G1N8-DELTA","PROJECT-K3S8-DELTA","PROJECT-J2V1-DELTA","PROJECT-I7U8-DELTA","PROJECT-T8P5-DELTA","PROJECT-U1V6-DELTA","PROJECT-F3K9-DELTA","PROJECT-W5A4-DELTA","PROJECT-Q4W5-DELTA","PROJECT-U3R8-DELTA",
        ]

        # Vérifier si le code est valide
        if code in valid_codes:
            if code in premium_data["used_codes"]:
                embed = discord.Embed(
                    title="❌ Code déjà utilisé",
                    description="Ce code premium a déjà été utilisé. Vous ne pouvez pas l'utiliser à nouveau.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            if data.get("is_premium", False):
                embed = discord.Embed(
                    title="⚠️ Serveur déjà Premium",
                    description=f"Le serveur **{interaction.guild.name}** est déjà un serveur premium. 🎉",
                    color=discord.Color.yellow()
                )
                embed.add_field(
                    name="Pas de double activation",
                    value="Ce serveur a déjà activé le code premium. Aucun changement nécessaire.",
                    inline=False
                )
                embed.set_footer(text="Merci d'utiliser nos services premium.")
                embed.set_thumbnail(url=interaction.guild.icon.url)
                await interaction.followup.send(embed=embed)
                return

            # Activer le premium
            data["is_premium"] = True
            premium_data["used_codes"].append(code)
            data["setup_premium"] = premium_data

            # ✅ ICI : indentation correcte
            collection2.update_one(
                {"guild_id": interaction.guild.id},
                {
                    "$set": {
                        "guild_name": interaction.guild.name,
                        "is_premium": True,
                        "used_codes": premium_data["used_codes"]
                    }
                },
                upsert=True
            )

            embed = discord.Embed(
                title="✅ Serveur Premium Activé",
                description=f"Le serveur **{interaction.guild.name}** est maintenant premium ! 🎉",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Avantages Premium",
                value="Profitez des fonctionnalités exclusives réservées aux serveurs premium. 🎁",
                inline=False
            )
            embed.set_footer(text="Merci d'utiliser nos services premium.")
            embed.set_thumbnail(url=interaction.guild.icon.url)
            await interaction.followup.send(embed=embed)

        else:
            embed = discord.Embed(
                title="❌ Code Invalide",
                description="Le code que vous avez entré est invalide. Veuillez vérifier votre code ou contactez le support.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Suggestions",
                value="1. Assurez-vous d'avoir saisi le code exactement comme il est fourni.\n"
                      "2. Le code est sensible à la casse.\n"
                      "3. Si vous avez des doutes, contactez le support.",
                inline=False
            )
            embed.add_field(
                name="Code Expiré ?",
                value="Si vous pensez que votre code devrait être valide mais ne l'est pas, il est possible qu'il ait expiré.",
                inline=False
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"Une erreur est survenue : {str(e)}")

@bot.tree.command(name="total-premium", description="Met tous les serveurs en premium et affiche la liste (réservé à Isey)")
async def total_premium(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Vous n'avez pas l'autorisation d'utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    try:
        premium_servers = []

        for guild in bot.guilds:
            result = collection2.update_one(
                {"guild_id": guild.id},  # ✅ utiliser un int, pas str
                {"$set": {
                    "is_premium": True,
                    "guild_name": guild.name  # utile pour le suivi
                }},
                upsert=True
            )
            premium_servers.append(f"- {guild.name} (`{guild.id}`)")

        server_list = "\n".join(premium_servers) or "Aucun serveur trouvé."

        embed = discord.Embed(
            title=f"🌟 Tous les serveurs sont maintenant Premium ({len(premium_servers)})",
            description=server_list,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Commande exécutée par {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)
@bot.tree.command(name="reset-premium", description="Réinitialise tous les serveurs en non-premium (réservé à Isey)")
async def reset_premium(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Vous n'avez pas l'autorisation d'utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    try:
        reset_servers = []

        for guild in bot.guilds:
            result = collection2.update_one(
                {"guild_id": guild.id},
                {"$set": {
                    "is_premium": False,
                    "guild_name": guild.name
                }},
                upsert=True
            )
            reset_servers.append(f"- {guild.name} (`{guild.id}`)")

        server_list = "\n".join(reset_servers) or "Aucun serveur trouvé."

        embed = discord.Embed(
            title=f"🔧 Tous les serveurs ont été réinitialisés en non-Premium ({len(reset_servers)})",
            description=server_list,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Commande exécutée par {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

@bot.tree.command(name="viewpremium", description="Voir les serveurs ayant activé le Premium")
async def viewpremium(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID and not interaction.user.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    # Récupération des serveurs premium
    premium_servers_data = collection2.find({"guild_id": {"$exists": True}})

    premium_list = []
    for server in premium_servers_data:
        guild_name = server.get("guild_name", "❓ Nom inconnu")
        premium_list.append(f"📌 **{guild_name}**")

    if premium_list:
        embed = discord.Embed(
            title="🌟 Liste des Serveurs Premium",
            description="Voici les serveurs ayant activé le **Premium** :\n\n" + "\n".join(premium_list),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Merci à tous pour votre soutien 💖")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="🔒 Aucun Serveur Premium",
            description="Aucun serveur n'a encore activé le **Premium** sur ce bot.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Pourquoi devenir premium ? 💎",
            value="Obtenez des **fonctionnalités exclusives**, plus de **personnalisation** et un **support prioritaire** !\n\n"
                  "📬 **Contactez-nous** pour plus d'informations.",
            inline=False
        )
        embed.set_footer(text="Rejoignez le programme Premium dès aujourd'hui ✨")

        # Bouton d'action
        join_button = discord.ui.Button(label="🚀 Rejoindre Premium", style=discord.ButtonStyle.green, url="https://votre-lien-premium.com")

        view = discord.ui.View()
        view.add_item(join_button)

        await interaction.response.send_message(embed=embed, view=view)

# Autocomplétion des serveurs premium
async def premium_autocomplete(interaction: discord.Interaction, current: str):
    servers = collection2.find({"guild_id": {"$exists": True}})
    return [
        app_commands.Choice(name=server.get("guild_name", "Nom inconnu"), value=str(server["guild_id"]))
        for server in servers if current.lower() in server.get("guild_name", "").lower()
    ][:25]  # Discord limite à 25 suggestions

@bot.tree.command(name="delete-premium", description="Supprime un serveur de la liste Premium")
@app_commands.describe(server="Choisissez le serveur à supprimer")
@app_commands.autocomplete(server=premium_autocomplete)
async def delete_premium(interaction: discord.Interaction, server: str):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    result = collection2.delete_one({"guild_id": int(server)})
    if result.deleted_count > 0:
        await interaction.response.send_message(f"✅ Le serveur Premium avec l'ID `{server}` a bien été supprimé.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Aucun serveur trouvé avec cet ID.", ephemeral=True)

@bot.tree.command(
    name="info-premium",
    description="Affiche les informations sur le statut premium du serveur et comment l'obtenir."
)
async def devenirpremium(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID and not interaction.user.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    # Charger les données de ce serveur spécifique
    data = load_guild_settings(interaction.guild.id)
    setup_premium_data = data["setup_premium"]

    if setup_premium_data:  # Si le serveur est déjà premium
        embed = discord.Embed(
            title="🎉 Vous êtes déjà Premium !",
            description=f"Le serveur **{interaction.guild.name}** est déjà un serveur Premium ! 🎉",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Avantages Premium",
            value="Profitez déjà des fonctionnalités exclusives réservées aux serveurs premium. 🎁",
            inline=False
        )
        embed.set_footer(text="Merci d'utiliser nos services premium.")
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    else:  # Si le serveur n'est pas encore premium
        embed = discord.Embed(
            title="🚀 Comment devenir Premium ?",
            description=f"Le serveur **{interaction.guild.name}** n'est pas encore premium. Voici comment vous pouvez devenir premium :",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Étapes pour devenir Premium",
            value="1. Entrez votre code premium avec la commande `/premium <votre_code>`.\n"
                  "2. Un message de confirmation vous sera envoyé une fois le serveur activé.\n"
                  "3. Profitez des fonctionnalités exclusives réservées aux serveurs Premium ! 🎁",
            inline=False
        )
        embed.add_field(
            name="Pourquoi devenir Premium ?",
            value="Les serveurs premium ont accès à des fonctionnalités exclusives, plus de personnalisation et des options avancées.",
            inline=False
        )
        embed.set_footer(text="Rejoignez notre programme Premium et profitez des avantages !")
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

#------------------------------------------------------------------------- Commande SETUP
import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio

class SetupView(View):
    def __init__(self, ctx, guild_data, collection):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.guild_data = guild_data or {}
        self.collection = collection
        self.embed_message = None
        self.add_item(MainSelect(self))

    async def start(self):  
        embed = discord.Embed(
            title="\u2699\ufe0f **Configuration du Serveur**",
            description="""
\ud83c\udf89 **Bienvenue dans le menu de configuration !**  
Personnalisez votre serveur **facilement** gr\u00e2ce aux options ci-dessous.  

\ud83d\udccc **Gestion du Bot**

\ud83d\udd3d **S\u00e9lectionnez la cat\u00e9gorie pour commencer !**
            """,
            color=discord.Color.blurple()
        )

        self.embed_message = await self.ctx.send(embed=embed, view=self)
        print("[SetupView] Menu principal envoy\u00e9.")

    async def update_embed(self, category):
        embed = discord.Embed(color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"Serveur : {self.ctx.guild.name}", icon_url=self.ctx.guild.icon.url if self.ctx.guild.icon else None)

        if category == "accueil":
            embed.title = "\u2699\ufe0f **Configuration du Serveur**"
            embed.description = """
\ud83c\udf89 **Bienvenue dans le menu de configuration !**  
Personnalisez votre serveur **facilement** gr\u00e2ce aux options ci-dessous.  

\ud83d\udccc **Gestion du Bot** 

\ud83d\udd3d **S\u00e9lectionnez la cat\u00e9gorie pour commencer !**
            """
            self.clear_items()
            self.add_item(MainSelect(self))

        elif category == "gestion":
            embed.title = "\u2699\ufe0f **Gestion du Bot**"
            embed.add_field(name="\u2699\ufe0f Pr\u00e9fixe actuel :", value=f"`{self.guild_data.get('prefix', '+')}`", inline=False)
            embed.add_field(name="\ud83d\udc51 Propri\u00e9taire :", value=format_mention(self.guild_data.get('owner', 'Non d\u00e9fini'), "user"), inline=False)
            embed.add_field(name="\ud83d\udee1\ufe0f R\u00f4le Admin :", value=format_mention(self.guild_data.get('admin_role', 'Non d\u00e9fini'), "role"), inline=False)
            embed.add_field(name="\ud83d\udc65 R\u00f4le Staff :", value=format_mention(self.guild_data.get('staff_role', 'Non d\u00e9fini'), "role"), inline=False)
            self.clear_items()
            self.add_item(InfoSelect(self))
            self.add_item(ReturnButton(self))

        if self.embed_message:
            await self.embed_message.edit(embed=embed, view=self)
            print(f"[SetupView] Embed mis \u00e0 jour pour la cat\u00e9gorie : {category}")

    async def notify_guild_owner(self, interaction, param, new_value):
        guild_owner = interaction.guild.owner  
        if guild_owner:  
            embed = discord.Embed(
                title="\ud83d\udd14 **Mise \u00e0 jour de la configuration**",
                description=f"\u2699\ufe0f **Une modification a \u00e9t\u00e9 effectu\u00e9e sur votre serveur `{interaction.guild.name}`.**",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="\ud83d\udc64 **Modifi\u00e9 par**", value=interaction.user.mention, inline=True)
            embed.add_field(name="\ud83d\udd27 **Param\u00e8tre modifi\u00e9**", value=f"`{param}`", inline=True)
            embed.add_field(name="\ud83e\udd1e **Nouvelle valeur**", value=f"{new_value}", inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text="Pensez \u00e0 v\u00e9rifier la configuration si n\u00e9cessaire.")

            await guild_owner.send(embed=embed)
            print(f"[Notify] Notification envoy\u00e9e au propri\u00e9taire pour : {param}")

def format_mention(id, type_mention):
    if not id or id == "Non d\u00e9fini":
        return "\u274c **Non d\u00e9fini**"

    if isinstance(id, int) or (isinstance(id, str) and id.isdigit()):
        if type_mention == "user":
            return f"<@{id}>"
        elif type_mention == "role":
            return f"<@&{id}>"
        elif type_mention == "channel":
            return f"<#{id}>"
        return "\u274c **Mention invalide**"

    return "\u274c **Format invalide**"

class MainSelect(Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label="\u2699\ufe0f Gestion du Bot", description="Modifier les r\u00f4les et salons", value="gestion"),
        ]
        super().__init__(placeholder="\ud83d\udccc S\u00e9lectionnez une cat\u00e9gorie", options=options)
        self.view_ctx = view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        print("[MainSelect] Cat\u00e9gorie s\u00e9lectionn\u00e9e :", self.values[0])
        await self.view_ctx.update_embed(self.values[0])

class ReturnButton(Button):
    def __init__(self, view):
        super().__init__(style=discord.ButtonStyle.danger, label="\ud83d\udd19 Retour", custom_id="return")
        self.view_ctx = view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        print("[ReturnButton] Retour au menu d'accueil")
        await self.view_ctx.update_embed("accueil")

class InfoSelect(Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label="\u2699\ufe0f Modifier le pr\u00e9fixe", value="prefix"),
            discord.SelectOption(label="\ud83d\udc51 Propri\u00e9taire", value="owner"),
            discord.SelectOption(label="\ud83d\udee1\ufe0f R\u00f4le Admin", value="admin_role"),
            discord.SelectOption(label="\ud83d\udc65 R\u00f4le Staff", value="staff_role"),
        ]
        super().__init__(placeholder="\ud83c\udf9b\ufe0f S\u00e9lectionnez un param\u00e8tre \u00e0 modifier", options=options)
        self.view_ctx = view

    async def callback(self, interaction: discord.Interaction):
        param = self.values[0]
        print(f"[InfoSelect] Param\u00e8tre s\u00e9lectionn\u00e9 : {param}")

        prompts = {
            "prefix": "Veuillez entrer le **nouveau pr\u00e9fixe** pour le bot.",
            "owner": "Veuillez mentionner le **nouveau propri\u00e9taire** (@utilisateur).",
            "admin_role": "Veuillez mentionner le **nouveau r\u00f4le admin** (@r\u00f4le).",
            "staff_role": "Veuillez mentionner le **nouveau r\u00f4le staff** (@r\u00f4le).",
            "sanctions_channel": "Veuillez mentionner le **salon des sanctions** (#salon).",
        }

        embed = discord.Embed(
            title=f"✏️ Modification de `{param}`",
            description=prompts.get(param, "Veuillez entrer une nouvelle valeur."),
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Répondez dans les 60 secondes.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            response = await self.view_ctx.ctx.bot.wait_for("message", check=check, timeout=60)
            await response.delete()
        except asyncio.TimeoutError:
            embed_timeout = discord.Embed(
                title="⏳ Temps écoulé",
                description="Aucune modification effectuée.",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_timeout, ephemeral=True)

        new_value = None
        if param == "prefix":
            new_value = response.content.strip()
        elif param == "owner" and response.mentions:
            new_value = response.mentions[0].id
        elif param in ["admin_role", "staff_role"] and response.role_mentions:
            new_value = response.role_mentions[0].id

        if not new_value:
            embed_error = discord.Embed(
                title="❌ Erreur",
                description="Mention invalide. Veuillez r\u00e9essayer.",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_error, ephemeral=True)

        self.view_ctx.collection.update_one(
            {"guild_id": str(self.view_ctx.ctx.guild.id)},
            {"$set": {param: new_value}},
            upsert=True
        )
        self.view_ctx.guild_data[param] = new_value

        mention_type = "user" if param == "owner" else "role" if "role" in param else "channel"
        await self.view_ctx.notify_guild_owner(interaction, param, format_mention(new_value, mention_type))

        embed_success = discord.Embed(
            title="✅ Modification enregistr\u00e9e !",
            description=f"Le param\u00e8tre `{param}` a bien \u00e9t\u00e9 mis \u00e0 jour.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await interaction.followup.send(embed=embed_success, ephemeral=True)
        print(f"[InfoSelect] {param} modifi\u00e9 avec : {new_value}")

@bot.hybrid_command(name="setup", description="Configure le bot pour ce serveur.")
async def setup(ctx):
    print("[Setup] Commande 'setup' appelée.")
    if ctx.author.id != ISEY_ID and not ctx.author.guild_permissions.administrator:
        print("[Setup] Utilisateur non autorisé.")
        await ctx.send("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    print("[Setup] Récupération des données du serveur...")
    guild_data = collection.find_one({"guild_id": str(ctx.guild.id)}) or {}

    view = SetupView(ctx, guild_data, collection)
    await view.start()
    print("[Setup] Menu de configuration envoyé.")
#-------------------------------------------------------------------------- Commandes Liens Etherya: /etherya

@bot.tree.command(name="etherya", description="Obtiens le lien du serveur Etherya !")
async def etherya(interaction: discord.Interaction):
    """Commande slash pour envoyer l'invitation du serveur Etherya"""
    message = (
        "🌟 **[𝑺ץ] 𝑬𝒕𝒉𝒆𝒓𝒚𝒂 !** 🌟\n\n"
        "🍣 ・ Un serveur **Communautaire**\n"
        "🌸 ・ Des membres sympas et qui **sont actifs** !\n"
        "🌋 ・ Des rôles **exclusifs** avec une **boutique** !\n"
        "🎐 ・ **Safe place** & **Un Système Économique développé** !\n"
        "☕ ・ Divers **Salons** pour un divertissement optimal.\n"
        "☁️ ・ Un staff sympa, à l'écoute et qui **recrute** !\n"
        "🔥 ・ Pas convaincu ? Rejoins-nous et vois par toi-même le potentiel de notre serveur !\n\n"
        "🎫 **[Accès direct au serveur Etherya !](https://discord.gg/2CXDSSRTYz) **\n\n"
        "Rejoins-nous et amuse-toi ! 🎉"
    )

    await interaction.response.send_message(message)
#------------------------------------------------------------------------- Commandes de Gestion : +clear, +nuke, +addrole, +delrole

@bot.command()
async def clear(ctx, amount: int = None):
    # Vérifie si l'utilisateur a la permission de gérer les messages ou s'il est l'ID autorisé
    if ctx.author.id == 792755123587645461 or ctx.author.guild_permissions.manage_messages:
        if amount is None:
            await ctx.send("Merci de préciser un chiffre entre 2 et 100.")
            return
        if amount < 2 or amount > 100:
            await ctx.send("Veuillez spécifier un nombre entre 2 et 100.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'{len(deleted)} messages supprimés.', delete_after=5)
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")

# Configuration des emojis personnalisables
EMOJIS = {
    "members": "👥",
    "crown": "👑",  # Emoji couronne
    "voice": "🎤",
    "boosts": "🚀"
}

@bot.command()
async def addrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Ajoute un rôle à un utilisateur."""
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +addrole @user @rôle")
        return

    try:
        # Ajouter le rôle à l'utilisateur
        await user.add_roles(role)
        await ctx.send(f"{user.mention} a maintenant le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour attribuer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")
    
@bot.command()
async def delrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Retire un rôle à un utilisateur."""
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +delrole @user @rôle")
        return

    try:
        # Retirer le rôle à l'utilisateur
        await user.remove_roles(role)
        await ctx.send(f"{user.mention} n'a plus le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour retirer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    # Vérifie si l'utilisateur a l'ID de permission ou la permission "Gérer les rôles"
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    # Vérifie si l'utilisateur a l'ID de permission ou la permission "Gérer les rôles"
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    # Vérifie si l'utilisateur a l'ID de permission ou la permission "Gérer les rôles"
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

def has_permission(ctx, perm=None):
    # Exemple d'une fonction de vérification de permissions
    if perm is None:
        perm = "admin"  # Par défaut, on suppose que l'admin a la permission
    # Logique pour vérifier la permission, par exemple :
    return ctx.author.permissions_in(ctx.channel).administrator  # Remplace cette logique par celle qui te convient.

@bot.command()
async def massrole(ctx, action: str = None, role: discord.Role = None):
    # Vérifie si les arguments sont présents
    if action is None or role is None:
        return await ctx.send("Erreur : tu dois spécifier l'action ('add' ou 'remove') et le rôle. Exemple : `+massrole add @role` ou `+massrole remove @role`.")

    # Vérifie si l'utilisateur a la permission nécessaire
    if not has_permission(ctx, "admin"):  # Spécifie ici la permission requise
        return await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")

    # Vérifie que l'action soit correcte (add ou remove)
    if action not in ['add', 'remove']:
        return await ctx.send("Erreur : l'action doit être 'add' ou 'remove'.")

    # Action pour ajouter ou retirer le rôle
    for member in ctx.guild.members:
        # S'assurer que ce n'est pas un bot
        if not member.bot:
            try:
                if action == 'add':
                    # Ajoute le rôle à l'utilisateur
                    await member.add_roles(role)
                elif action == 'remove':
                    # Retire le rôle à l'utilisateur
                    await member.remove_roles(role)
                print(f"Le rôle a été {action}é pour {member.name}")
            except discord.DiscordException as e:
                print(f"Erreur avec {member.name}: {e}")

    await ctx.send(f"Le rôle '{role.name}' a été {action} à tous les membres humains du serveur.")

@bot.command()
async def nuke(ctx):
    # Vérifie si l'utilisateur a la permission Administrateur
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.administrator:
        await ctx.send("Tu n'as pas les permissions nécessaires pour exécuter cette commande.")
        return

    # Vérifie que la commande a été lancée dans un salon texte
    if isinstance(ctx.channel, discord.TextChannel):
        # Récupère le salon actuel
        channel = ctx.channel

        # Sauvegarde les informations du salon
        overwrites = channel.overwrites
        channel_name = channel.name
        category = channel.category
        position = channel.position

        # Récupère l'ID du salon pour le recréer
        guild = channel.guild

        try:
            # Supprime le salon actuel
            await channel.delete()

            # Crée un nouveau salon avec les mêmes permissions, catégorie et position
            new_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category
            )

            # Réajuste la position du salon
            await new_channel.edit(position=position)

            # Envoie un message dans le nouveau salon pour confirmer la recréation
            await new_channel.send(
                f"💥 {ctx.author.mention} a **nuké** ce salon. Il a été recréé avec succès."
            )
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la recréation du salon : {e}")
    else:
        await ctx.send("Cette commande doit être utilisée dans un salon texte.")
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
#------------------------------------------------------------------------- Commandes d'aide : +aide, /help
@bot.command()
async def help(ctx):
    banner_url = "https://github.com/Iseyg91/KNSKS-ET/blob/main/IMAGES%20Delta/uri_ifs___M_5e2bd04a-3995-4937-979e-1aeb20cd5fc1.jpg?raw=true"  # URL de la bannière
    embed = discord.Embed(
        title="🏡 **Accueil Project : Delta **",
        description=f"Hey, bienvenue {ctx.author.mention} sur la page d'accueil de Project : Delta! 🎉\n\n"
                    "Ici, vous trouverez toutes les informations nécessaires pour gérer et administrer votre serveur efficacement. 🌟",
        color=discord.Color(0x1abc9c)
    )
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Développé avec ❤️ par Iseyg. Merci pour votre soutien !")
    embed.set_image(url=banner_url)  # Ajout de la bannière en bas de l'embed

    # Informations générales
    embed.add_field(name="📚 **Informations**", value=f"• **Mon préfixe** : +\n• **Nombre de commandes** : 70", inline=False)

    # Création du menu déroulant
    select = discord.ui.Select(
        placeholder="Choisissez une catégorie 👇", 
        options=[
            discord.SelectOption(label="Owner Bot", description="Commandes pour gèrer le bot", emoji="🎓"),
            discord.SelectOption(label="Configuration du Bot", description="Commandes pour configurer le bot", emoji="📡"),
            discord.SelectOption(label="Gestion", description="Commandes pour gérer le serveur", emoji="🔧"),
            discord.SelectOption(label="Utilitaire", description="Commandes utiles", emoji="🔔"),
            discord.SelectOption(label="Modération", description="Commandes Modération", emoji="🔨"),
            discord.SelectOption(label="Bot", description="Commandes Bot", emoji="🦾"),
            discord.SelectOption(label="Ludiques", description="Commandes amusantes pour détendre l'atmosphère et interagir avec les autres.", emoji="🎈"),
            discord.SelectOption(label="Test & Défis", description="Commandes pour testez la personnalité et défiez vos amis avec des jeux et des évaluations.", emoji="🎲"),
            discord.SelectOption(label="Crédits", description="Remerciements et crédits", emoji="💖")
        ], 
        custom_id="help_select"
    )
    # Définir la méthode pour gérer l'interaction du menu déroulant
    async def on_select(interaction: discord.Interaction):
        category = interaction.data['values'][0]
        new_embed = discord.Embed(color=discord.Color(0x1abc9c))
        new_embed.set_image(url=banner_url)  # Ajout de la bannière dans chaque catégorie
        if category == "Owner Bot":
            new_embed.title = "👑 **Commandes de Gestion du Bot**"
            new_embed.description = "Bienvenue dans la section gestion du bot !"
            new_embed.add_field(name="💥 +shutdown", value="Déconnecte le **bot**.\n*Pour une action plus drastique en cas de chaos ou d'urgence !*.", inline=False)
            new_embed.add_field(name="🔧 +restart", value="Redémarre le **bot**.\n*À utiliser en cas de mise à jour ou de bug mineur.*", inline=False)
            new_embed.add_field(name="🎈 +serverinfoall", value="Affiche les **informations de tous les serveurs** où le bot est présent.",  inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Configuration du Bot":
            new_embed.title = "🗃️ **Commandes de Configuration du Bot**"
            new_embed.description = "Bienvenue dans la section configuration du bot !"
            new_embed.add_field(name="⚙️ /setup", value="Lance la **configuration du bot** sur le serveur.\n*Permet de personnaliser les paramètres du bot selon les besoins du serveur.*", inline=False)
            new_embed.add_field(name="⚠️ /set-sensible", value="Permet de **configurer les catégories de mots sensibles** que le bot doit surveiller dans le chat.\n""*Pour personnaliser la détection de contenu inapproprié selon les besoins de votre serveur.*",inline=False)
            new_embed.add_field(name="🔓 +addwl", value="Ajoute un membre à la **whitelist** pour qu'il soit **ignoré** par les protections du bot.\n*Permet d'exempter certains utilisateurs des actions de sécurité comme l'anti-spam ou l'anti-lien.*", inline=False)
            new_embed.add_field(name="❌ +removewl", value="Supprime un membre de la **whitelist** pour qu'il soit de nouveau **sujet aux protections** du bot.\n*Utilisé pour réactiver les actions de sécurité contre l'utilisateur.*", inline=False)
            new_embed.add_field(name="🔍 +listwl", value="Affiche la **liste des membres sur la whitelist** du bot 🛡️.\n*Permet de voir quels utilisateurs sont exemptés des protections du bot.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Gestion":
            new_embed.title = "🔨 **Commandes de Gestion**"
            new_embed.description = "Bienvenue dans la section gestion ! 📊\nCes commandes sont essentielles pour administrer le serveur. Voici un aperçu :"
            new_embed.add_field(name="🔧 +clear (2-100)", value="Supprime des messages dans le salon.\n*Utilisé pour nettoyer un salon ou supprimer un spam.*", inline=False)
            new_embed.add_field(name="💥 +nuke", value="Efface **tous** les messages du salon.\n*Pour une action plus drastique en cas de chaos ou d'urgence !*.", inline=False)
            new_embed.add_field(name="➕ +addrole @user @rôle", value="Ajoute un rôle à un utilisateur.\n*Pour attribuer des rôles et des privilèges spéciaux aux membres.*", inline=False)
            new_embed.add_field(name="➖ +delrole @user @rôle", value="Retire un rôle à un utilisateur.\n*Retirer un rôle en cas de sanction ou de changement de statut.*", inline=False)
            new_embed.add_field(name="🔲 /embed", value="Crée un **embed personnalisé** avec du texte, des images et des couleurs.\n*Pratique pour partager des informations de manière stylée et structurée.*", inline=False)
            new_embed.add_field(name="🚫 +listban", value="Affiche la **liste des membres bannis** du serveur.\n*Permet aux admins de voir les bannissements en cours.*", inline=False)
            new_embed.add_field(name="🔓 +unbanall", value="Dé-banni **tous les membres** actuellement bannis du serveur.\n*Utilisé pour lever les bannissements en masse.*", inline=False)
            new_embed.add_field(name="🎉 /g-create", value="Crée un **giveaway** (concours) pour offrir des récompenses aux membres.\n*Permet d'organiser des tirages au sort pour des prix ou des objets.*", inline=False)
            new_embed.add_field(name="⚡ /g-fast", value="Crée un **giveaway rapide** avec une durée courte.\n*Idéal pour des concours instantanés avec des récompenses immédiates.*", inline=False)
            new_embed.add_field(name="💎 /premium", value="Entre un **code premium** pour devenir membre **premium** et accéder à des fonctionnalités exclusives.\n*Permet de débloquer des avantages supplémentaires pour améliorer ton expérience.*", inline=False)
            new_embed.add_field(name="🔍 /viewpremium", value="Affiche la **liste des serveurs premium** actuellement actifs.\n*Permet de voir quels serveurs ont accédé aux avantages premium.*", inline=False)
            new_embed.add_field(name="💎 /devenirpremium", value="Obtiens des **informations** sur la manière de devenir membre **premium** et débloquer des fonctionnalités exclusives.\n*Un guide pour savoir comment accéder à l'expérience premium et ses avantages.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Utilitaire":
            new_embed.title = "⚙️ **Commandes Utilitaires**"
            new_embed.description = "Bienvenue dans la section modération ! 🚨\nCes commandes sont conçues pour gérer et contrôler l'activité du serveur, en assurant une expérience sûre et agréable pour tous les membres."
            new_embed.add_field(name="📊 +vc", value="Affiche les statistiques du serveur en temps réel .\n*Suivez l'évolution du serveur en direct !*.", inline=False)
            new_embed.add_field(name="🚨 +alerte @user <reason>", value="Envoie une alerte au staff en cas de comportement inapproprié (insultes, spam, etc.) .\n*Note : Si cette commande est utilisée abusivement, des sanctions sévères seront appliquées !*.", inline=False)
            new_embed.add_field(name="📶 +ping", value="Affiche la latence du bot en millisecondes.", inline=False)
            new_embed.add_field(name="⏳ +uptime", value="Affiche depuis combien de temps le bot est en ligne.", inline=False)
            new_embed.add_field(name="ℹ️ /rôle info <nom_du_rôle>", value="Affiche les informations détaillées sur un rôle spécifique.", inline=False)
            new_embed.add_field(name="ℹ💡 /idée", value="Note une idée ou une chose à faire dans ta liste perso.\n*Parfait pour te rappeler d'un projet, d'une envie ou d'un objectif.*", inline=False)
            new_embed.add_field(name="📋 +listi", value="Affiche la **liste de tes idées notées**.\n*Utile pour retrouver facilement ce que tu as prévu ou pensé.*", inline=False)
            new_embed.add_field(name="💬 /suggestion", value="Propose une **suggestion ou une idée** pour améliorer **Etherya** ou le **bot** .\n*Ton avis compte, alors n’hésite pas à participer à l’évolution du projet.*", inline=False)
            new_embed.add_field(name="📊 /sondage", value="Crée un **sondage** pour obtenir l'avis des membres du serveur.\n*Parfait pour recueillir des retours ou prendre des décisions collectives.*", inline=False)
            new_embed.add_field(name="👋 /presentation", value="Présente-toi au serveur et fais connaissance avec les membres.\n*Une manière sympa de partager tes intérêts et d'en savoir plus sur la communauté.*", inline=False)
            new_embed.add_field(name="🤖 +getbotinfo", value="Affiche des **informations détaillées** sur le bot.\n*Comprend des données comme la version, les statistiques et les fonctionnalités du bot.*", inline=False)
            new_embed.add_field(name="👑 +alladmin", value="Affiche la **liste de tous les administrateurs** du serveur.\n*Utile pour voir les membres avec les privilèges d'administration.*", inline=False)
            new_embed.add_field(name="🔍 +snipe", value="Affiche le **dernier message supprimé** du serveur.\n*Permet de récupérer le contenu des messages effacés récemment.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Modération":
            new_embed.title = "🔑 **Commandes Modération**"
            new_embed.add_field(name="🚫 +ban @user", value="Exile un membre du serveur pour un comportement inacceptable .\nL'action de bannir un utilisateur est irréversible et est utilisée pour des infractions graves aux règles du serveur.*", inline=False)
            new_embed.add_field(name="🚔 +unban @user", value="Lève le bannissement d'un utilisateur, lui permettant de revenir sur le serveur .\nUnban un utilisateur qui a été banni, après examen du cas et décision du staff..*", inline=False)
            new_embed.add_field(name="⚖️ +mute @user", value="Rend un utilisateur silencieux en l'empêchant de parler pendant un certain temps .\nUtilisé pour punir les membres qui perturbent le serveur par des messages intempestifs ou offensants.", inline=False)
            new_embed.add_field(name="🔓 +unmute @user", value="Annule le silence imposé à un utilisateur et lui redonne la possibilité de communiquer.\nPermet à un membre de reprendre la parole après une période de mute.", inline=False)
            new_embed.add_field(name="⚠️ +warn @user", value="Avertit un utilisateur pour un comportement problématique ⚠.\nUn moyen de signaler qu'un membre a enfreint une règle mineure, avant de prendre des mesures plus sévères.", inline=False)
            new_embed.add_field(name="🚪 +kick @user", value="Expulse un utilisateur du serveur pour une infraction moins grave .\nUn kick expulse temporairement un membre sans le bannir, pour des violations légères des règles.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Bot":
            new_embed.title = "🔑 **Commandes Bot**"
            new_embed.add_field(name="🔊 /connect", value="Connecte le **bot à un canal vocal** du serveur.\n*Permet au bot de rejoindre un salon vocal pour y diffuser de la musique ou d'autres interactions.*", inline=False)
            new_embed.add_field(name="🔴 /disconnect", value="Déconnecte le **bot du canal vocal**.\n*Permet au bot de quitter un salon vocal après une session musicale ou autre interaction.*", inline=False)
            new_embed.add_field(name="🌐 /etherya", value="Affiche le **lien du serveur Etherya** pour rejoindre la communauté.\n*Permet d'accéder facilement au serveur Etherya et de rejoindre les discussions et événements.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Ludiques":
            new_embed.title = "🎉 **Commandes de Détente**"
            new_embed.description = "Bienvenue dans la section Détente ! 🎈\nCes commandes sont conçues pour vous amuser et interagir de manière légère et drôle. Profitez-en !"
            new_embed.add_field(name="🌟 +blague", value="Envoie une blague aléatoire, comme 'Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? Parce que sinon ils tombent toujours dans le bateau !'.", inline=False)
            new_embed.add_field(name="🪙 +coinflip", value="Lancez une pièce pour voir si vous gagnez ! \n*Tentez votre chance et découvrez si vous avez un coup de chance.*", inline=False)
            new_embed.add_field(name="🗣️ +say", value="Faites dire quelque chose au bot à la place de vous ! 🗨\n*Lancez votre message et il sera annoncé à tout le serveur !*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Test & Défis":
            new_embed.title = "🎯 **Commandes de Tests et Défis**"
            new_embed.description = "Bienvenue dans la section Tests et Défis ! 🎲\nIci, vous pouvez évaluer les autres, tester votre compatibilité et relever des défis fun !"
            new_embed.add_field(name="🌈 +gay @user", value="Détermine le taux de gayitude d'un utilisateur .\n*Testez votre ouverture d'esprit !*.", inline=False)
            new_embed.add_field(name="😤 +racist @user", value="Détermine le taux de racisme d'un utilisateur .\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="💘 +love @user", value="Affiche le niveau de compatibilité amoureuse .\n*Testez votre compatibilité avec quelqu'un !*.", inline=False)
            new_embed.add_field(name="🐀 +rat @user", value="Détermine le taux de ratitude d'un utilisateur .\n*Vérifiez qui est le plus ‘rat’ parmi vos amis.*", inline=False)
            new_embed.add_field(name="🍆 +zizi @user", value="Évalue le niveau de zizi de l'utilisateur .\n*Un test ludique pour voir qui a le plus grand ego !*.", inline=False)
            new_embed.add_field(name="🤡 +con @user", value="Détermine le taux de connerie d'un utilisateur .\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="🤪 +fou @user", value="Détermine le taux de folie d'un utilisateur .\n*Testez l'état mental de vos amis !*.", inline=False)
            new_embed.add_field(name="💪 +testo @user", value="Détermine le taux de testostérone d'un utilisateur .\n*Testez la virilité de vos amis !*.", inline=False)
            new_embed.add_field(name="🍑 +libido @user", value="Détermine le taux de libido d'un utilisateur .\n*Testez la chaleur de vos amis sous la couette !*.", inline=False)
            new_embed.add_field(name="🔄 +reverse [texte]", value="Inverser un texte et le partager avec un autre utilisateur ! \n*Lancez un défi pour voir si votre inversion sera correcte !*", inline=False)
            new_embed.add_field(name="⭐ +note @user [note sur 10]", value="Notez un autre utilisateur sur 10 ! \n*Exprimez votre avis sur leur comportement ou performance dans le serveur.*", inline=False)
            new_embed.add_field(name="🎲 +roll", value="Lance un dé pour générer un nombre aléatoire entre 1 et 500 .\n*Essayez votre chance !*.", inline=False)
            new_embed.add_field(name="🥊 +fight @user", value="Lancez un duel avec un autre utilisateur ! \n*Acceptez ou refusez le combat et découvrez qui sera le champion du serveur.*", inline=False)
            new_embed.add_field(name="⚡ +superpouvoir @user", value="Déclenche un super-pouvoir épique pour un utilisateur !\n*Donne un pouvoir aléatoire allant du cool au complètement débile, comme la téléportation, la super vitesse, ou même la création de burgers.*", inline=False)
            new_embed.add_field(name="🌿 +totem @user", value="Découvrez votre animal totem spirituel !\n*Un animal magique et spirituel vous guidera, qu’il soit un loup protecteur ou un poisson rouge distrait. Un résultat épique et amusant !*", inline=False)
            new_embed.add_field(name="🔮 +futur @user", value="Prédit l'avenir d'un utilisateur de manière totalement farfelue !\n*L'avenir peut être aussi improbable qu'un trésor caché rempli de bonbons ou une rencontre avec un extraterrestre amateur de chats.*", inline=False)
            new_embed.add_field(name="👶 +enfant @user @user", value="Crée un enfant aléatoire entre deux utilisateurs !\n*Mélangez les pseudos et les photos de profil des deux utilisateurs pour créer un bébé unique. C'est fun et surprenant !*", inline=False)
            new_embed.add_field(name="🍬 +sucre", value="Affiche le **taux de glycémie** du membre ciblé 🍭.\n*Utile pour suivre les niveaux de sucre des membres du serveur de manière ludique.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Crédits":
            new_embed.title = "💖 **Crédits et Remerciements**"
            new_embed.description = """
            Un immense merci à **Iseyg** pour le développement de ce bot incroyable ! 🙏  
            Sans lui, ce bot ne serait rien de plus qu'un concept. Grâce à sa passion, son travail acharné et ses compétences exceptionnelles, ce projet a pris vie et continue de grandir chaque jour. 🚀

            Nous tenons également à exprimer notre gratitude envers **toute la communauté**. 💙  
            Votre soutien constant, vos retours et vos idées font de ce bot ce qu'il est aujourd'hui. Chacun de vous, que ce soit par vos suggestions, vos contributions ou même simplement en utilisant le bot, fait une différence. 

            Merci à **tous les développeurs, contributeurs et membres** qui ont aidé à faire évoluer ce projet et l’ont enrichi avec leurs talents et leurs efforts. 🙌

            Et bien sûr, un grand merci à vous, **utilisateurs**, pour votre enthousiasme et votre confiance. Vous êtes la raison pour laquelle ce bot continue d’évoluer. 🌟

            Restons unis et continuons à faire grandir cette aventure ensemble ! 🌍
            """
            new_embed.set_footer(text="♥️ by Iseyg")

        await interaction.response.edit_message(embed=new_embed)

    select.callback = on_select  # Attacher la fonction de callback à l'élément select

    # Afficher le message avec le menu déroulant
    view = discord.ui.View()
    view.add_item(select)
    
    await ctx.send(embed=embed, view=view)
#------------------------------------------------------------------------- Commandes Fun : Flemme de tout lister

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def gay(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de gayitude 🌈",
        description=f"{member.mention} est gay à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} ♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def singe(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de singe 🐒",
        description=f"{member.mention} est un singe à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'énergie primate du membre.*",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} 🐵 by Isey", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def racist(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de racisme 🪄",
        description=f"{member.mention} est raciste à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def sucre(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de l'indice glycémique 🍬",
        description=f"L'indice glycémique de {member.mention} est de **{percentage}%** !\n\n*Le pourcentage varie en fonction des habitudes alimentaires de la personne.*",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} 🍏by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def rat(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de radinerie 🐁", 
        description=f"{member.mention} est un rat à **{percentage}%** !\n\n*Le pourcentage varie en fonction des actes du membre.*", 
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def con(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="Analyse de connerie 🤡",
        description=f"{member.mention} est con à **{percentage}%** !\n\n*Le pourcentage varie en fonction des neurones actifs du membre.*",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def libido(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="Analyse de libido 🔥",
        description=f"{member.mention} a une libido à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'humeur et du climat.*",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)
    
@bot.command()
async def zizi(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    # Générer une valeur aléatoire entre 0 et 50 cm
    value = random.randint(0, 50)

    # Créer l'embed
    embed = discord.Embed(
        title="Analyse de la taille du zizi 🔥", 
        description=f"{member.mention} a un zizi de **{value} cm** !\n\n*La taille varie selon l'humeur du membre.*", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    # Envoyer l'embed
    await ctx.send(embed=embed)

@bot.command()
async def fou(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de folie 🤪", 
        description=f"{member.mention} est fou à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'état mental du membre.*", 
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def testo(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de testostérone 💪", 
        description=f"{member.mention} a un taux de testostérone de **{percentage}%** !\n\n*Le pourcentage varie en fonction des niveaux de virilité du membre.*", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name="say", description="Fais dire un message au bot.")
@app_commands.describe(text="Le texte à dire")
async def say(ctx: commands.Context, *, text: str = None):
    # Vérifie si l'utilisateur a les permissions d'admin ou si son ID correspond à ISEY_ID
    if not ctx.author.guild_permissions.administrator and str(ctx.author.id) != "792755123587645461":
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    if text is None:
        await ctx.send("Tu n'as pas écrit de texte à dire !", ephemeral=True)
        return

    # Supprime le message si la commande a été envoyée en message (et pas en slash)
    if ctx.prefix and ctx.message:
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass  # Le message a déjà été supprimé ou n'existe pas

    # Envoie le texte spécifié
    await ctx.send(text)

@bot.command()
async def coinflip(ctx):
    import random
    result = random.choice(["Pile", "Face"])
    await ctx.send(f"Résultat du coinflip : {result}")

# Définir la commande +roll
@bot.command()
async def roll(ctx, x: str = None):
    # Vérifier si x est bien précisé
    if x is None:
        embed = discord.Embed(
            title="Erreur",
            description="Vous n'avez pas précisé de chiffre entre 1 et 500.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Convertir x en entier
        x = int(x)
    except ValueError:
        embed = discord.Embed(
            title="Erreur",
            description="Le chiffre doit être un nombre entier.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Vérifier si x est dans les bonnes limites
    if x < 1 or x > 500:
        embed = discord.Embed(
            title="Erreur",
            description="Le chiffre doit être compris entre 1 et 500.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Générer un nombre aléatoire entre 1 et x
    result = random.randint(1, x)

    # Créer l'embed de la réponse
    embed = discord.Embed(
        title="🎲 Résultat du tirage",
        description=f"Le nombre tiré au hasard entre 1 et {x} est : **{result}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def enfant(ctx, parent1: discord.Member = None, parent2: discord.Member = None):
    if not parent1 or not parent2:
        await ctx.send("Tu dois mentionner deux membres ! Utilise `/enfant @membre1 @membre2`.")
        return
    
    # Génération du prénom en combinant les pseudos
    prenom = parent1.name[:len(parent1.name)//2] + parent2.name[len(parent2.name)//2:]
    
    # Création de l'embed
    embed = discord.Embed(
        title="👶 Voici votre enfant !",
        description=f"{parent1.mention} + {parent2.mention} = **{prenom}** 🍼",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Prenez soin de votre bébé ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    # Ajout des photos de profil
    embed.set_thumbnail(url=parent1.avatar.url if parent1.avatar else parent2.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def superpouvoir(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author  # Si pas d’utilisateur mentionné, prendre l’auteur

    pouvoirs = [
        "Téléportation instantanée 🌀 - Peut se déplacer n'importe où en un clin d'œil.",
        "Contrôle du feu 🔥 - Rien ne lui résiste… sauf l'eau.",
        "Super vitesse ⚡ - Peut courir plus vite qu'un TGV, mais oublie souvent où il va.",
        "Lecture des pensées 🧠 - Peut lire dans les esprits… sauf ceux qui ne pensent à rien.",
        "Invisibilité 🫥 - Peut disparaître… mais oublie que ses vêtements restent visibles.",
        "parler aux animaux 🦜 - Mais ils n'ont pas grand-chose d'intéressant à dire.",
        "Super force 💪 - Peut soulever une voiture, mais galère à ouvrir un pot de cornichons.",
        "Métamorphose 🦎 - Peut se transformer en n'importe quoi… mais pas revenir en humain.",
        "Chance infinie 🍀 - Gagne à tous les jeux… sauf au Uno.",
        "Création de portails 🌌 - Peut ouvrir des portails… mais ne sait jamais où ils mènent.",
        "Régénération 🩸 - Guérit instantanément… mais reste chatouilleux à vie.",
        "Capacité de voler 🕊️ - Mais uniquement à 10 cm du sol.",
        "Super charisme 😎 - Convainc tout le monde… sauf sa mère.",
        "Vision laser 🔥 - Brûle tout sur son passage… y compris ses propres chaussures.",
        "Invocation de clones 🧑‍🤝‍🧑 - Mais ils n’obéissent jamais.",
        "Télékinésie ✨ - Peut déplacer des objets… mais uniquement des plumes.",
        "Création de burgers 🍔 - Magique, mais toujours trop cuits ou trop crus.",
        "Respiration sous l'eau 🐠 - Mais panique dès qu'il voit une méduse.",
        "Contrôle de la gravité 🌍 - Peut voler, mais oublie souvent de redescendre.",
        "Capacité d’arrêter le temps ⏳ - Mais uniquement quand il dort.",
        "Voyage dans le temps ⏰ - Peut voyager dans le passé ou le futur… mais toujours à la mauvaise époque.",
        "Télépathie inversée 🧠 - Peut faire entendre ses pensées aux autres… mais ils ne peuvent jamais comprendre.",
        "Manipulation des rêves 🌙 - Peut entrer dans les rêves des gens… mais se retrouve toujours dans des cauchemars.",
        "Super mémoire 📚 - Se souvient de tout… sauf des choses qu’il vient de dire.",
        "Manipulation des ombres 🌑 - Peut faire bouger les ombres… mais ne peut jamais les arrêter.",
        "Création de pluie 🍃 - Peut faire pleuvoir… mais uniquement sur ses amis.",
        "Maîtrise des plantes 🌱 - Peut faire pousser des plantes à une vitesse folle… mais elles ne cessent de pousser partout.",
        "Contrôle des rêves éveillés 💤 - Peut contrôler ses rêves quand il est éveillé… mais se retrouve toujours dans une réunion ennuyante.",
        "Maîtrise de l’éclairage ✨ - Peut illuminer n'importe quelle pièce… mais oublie d’éteindre.",
        "Création de souvenirs 🧳 - Peut créer des souvenirs… mais ceux-ci sont toujours un peu bizarres.",
        "Changement de taille 📏 - Peut grandir ou rapetisser… mais n'arrive jamais à garder une taille stable.",
        "Vision nocturne 🌙 - Peut voir dans l’obscurité… mais tout est toujours en noir et blanc.",
        "Contrôle des éléments 🤹‍♂️ - Peut manipuler tous les éléments naturels… mais uniquement quand il pleut.",
        "Phasing à travers les murs 🚪 - Peut traverser les murs… mais parfois il traverse aussi les portes.",
        "Régénération de l’esprit 🧠 - Guérit les blessures mentales… mais les oublie instantanément après."


    ]

    pouvoir = random.choice(pouvoirs)

    embed = discord.Embed(
        title="⚡ Super-Pouvoir Débloqué !",
        description=f"{user.mention} possède le pouvoir de **{pouvoir}** !",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Utilise-le avec sagesse... ou pas. {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def totem(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author  # Si pas de membre mentionné, prendre l'auteur  

    animaux_totem = {
        "Loup 🐺": "Fidèle et protecteur, il veille sur sa meute.",
        "Renard 🦊": "Rusé et malin, il trouve toujours un moyen de s'en sortir.",
        "Hibou 🦉": "Sage et observateur, il comprend tout avant les autres.",
        "Dragon 🐉": "Puissant et imposant, il ne laisse personne indifférent.",
        "Dauphin 🐬": "Joueur et intelligent, il adore embêter les autres.",
        "Chat 🐱": "Mystérieux et indépendant, il fait ce qu’il veut, quand il veut.",
        "Serpent 🐍": "Discret et patient, il attend le bon moment pour frapper.",
        "Corbeau 🦅": "Intelligent et un peu sinistre, il voit ce que les autres ignorent.",
        "Panda 🐼": "Calme et adorable… jusqu’à ce qu’on lui prenne son bambou.",
        "Tortue 🐢": "Lente mais sage, elle gagne toujours à la fin.",
        "Aigle 🦅": "Libre et fier, il vole au-dessus de tous les problèmes.",
        "Chauve-souris 🦇": "Préférant l'obscurité, elle voit clair quand tout le monde est perdu.",
        "Tigre 🐯": "Puissant et rapide, personne ne l’arrête.",
        "Lapin 🐰": "Rapide et malin, mais fuit dès qu’il y a un problème.",
        "Singe 🐵": "Curieux et joueur, il adore faire des bêtises.",
        "Escargot 🐌": "Lent… mais au moins il arrive toujours à destination.",
        "Pigeon 🕊️": "Increvable et partout à la fois, impossible de s'en débarrasser.",
        "Licorne 🦄": "Rare et magique, il apporte de la lumière partout où il passe.",
        "Poisson rouge 🐠": "Mémoire de 3 secondes, mais au moins il ne s’inquiète jamais.",
        "Canard 🦆": "Semble idiot, mais cache une intelligence surprenante.",
        "Raton laveur 🦝": "Petit voleur mignon qui adore piquer des trucs.",
        "Lynx 🐆" : "Serré dans ses mouvements, il frappe avec précision et discrétion.",
        "Loup de mer 🌊🐺" : "Un loup qui conquiert aussi bien les océans que la terre, fier et audacieux.",
        "Baleine 🐋" : "Majestueuse et bienveillante, elle nage dans les eaux profondes avec sagesse.",
        "Léopard 🐆" : "Vif et agile, il disparaît dans la jungle avant même qu'on ait pu le voir.",
        "Ours 🐻" : "Fort et protecteur, il défend son territoire sans hésiter.",
        "Cygne 🦢" : "Gracieux et élégant, il incarne la beauté dans la tranquillité.",
        "Chameau 🐫" : "Patient et résistant, il traverse les déserts sans jamais se fatiguer.",
        "Grizzly 🐻‍❄️" : "Imposant et puissant, il est le roi des forêts froides.",
        "Koala 🐨" : "Doux et calme, il passe sa vie à dormir dans les arbres.",
        "Panthère noire 🐆" : "Silencieuse et mystérieuse, elle frappe toujours quand on s'y attend le moins.",
        "Zèbre 🦓" : "Unique et surprenant, il se distingue dans la foule grâce à ses rayures.",
        "Éléphant 🐘" : "Sage et majestueux, il marche au rythme de sa propre grandeur.",
        "Croco 🐊" : "Implacable et rusé, il attend patiemment avant de bondir.",
        "Mouflon 🐏" : "Fort et tenace, il n'a pas peur de braver les montagnes.",
        "Perroquet 🦜" : "Coloré et bavard, il ne cesse jamais de répéter ce qu'il entend.",
        "Rhinocéros 🦏" : "Imposant et robuste, il se fraye un chemin à travers tout sur son passage.",
        "Bison 🦬" : "Solide et puissant, il traverse les prairies avec une énergie inébranlable."

    }

    totem, description = random.choice(list(animaux_totem.items()))

    embed = discord.Embed(
        title=f"🌿 Totem de {member.name} 🌿",
        description=f"**{totem}** : {description}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
    
@bot.command()
async def futur(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author  # Si pas d’utilisateur mentionné, prendre l’auteur

    predicions = [
        "Dans 5 minutes, tu découvriras un trésor caché… mais il sera rempli de bonbons.",
        "L'année prochaine, tu feras une rencontre étonnante avec un extraterrestre qui adore les chats.",
        "Demain, tu auras une conversation intense avec un pigeon, et il te donnera un conseil de vie précieux.",
        "Un chat va te confier un secret qui changera le cours de ton existence… mais tu ne te souviendras pas de ce secret.",
        "Dans quelques jours, tu seras élu meilleur joueur de cache-cache, mais tu te cacheras dans une pièce vide.",
        "Lundi, tu rencontreras quelqu'un qui aime les licornes autant que toi. Vous deviendrez amis pour la vie.",
        "Dans un futur proche, tu réussiras à inventer un gâteau qui ne se mange pas, mais il sera étonnamment populaire.",
        "Bientôt, un mystérieux inconnu t'offrira un paquet cadeau. Il contiendra un élastique et une noix de coco.",
        "Dans un mois, tu vivras une aventure épique où tu devras résoudre un mystère impliquant des chaussettes perdues.",
        "Prochainement, tu seras récompensé pour avoir trouvé une solution révolutionnaire au problème de la pizza froide.",
        "Dans un futur lointain, tu seras le leader d'une civilisation intergalactique. Tes sujets seront principalement des pandas."
        "Dans 5 minutes, tu rencontreras un robot qui te demandera comment faire des pancakes… mais il n'a pas de mains.",
        "Ce week-end, tu seras choisi pour participer à un concours de danse avec des flamants roses, mais tu devras danser sans musique.",
        "Demain, un magicien te proposera un vœu… mais il te le refusera en te montrant un tour de cartes.",
        "Un perroquet va te confier un secret très important, mais tu l'oublieras dès que tu entras dans une pièce.",
        "Dans quelques jours, tu découvriras un trésor enfoui sous ta maison… mais il sera composé uniquement de petites pierres colorées.",
        "Prochainement, tu feras une rencontre étrange avec un extraterrestre qui te demandera de lui apprendre à jouer aux échecs.",
        "Dans un futur proche, tu gagneras un prix prestigieux pour avoir créé un objet du quotidien, mais personne ne saura vraiment à quoi il sert.",
        "Bientôt, tu recevras une invitation pour un dîner chez des créatures invisibles. Le menu ? Des nuages et des rayons de lune.",
        "Dans un mois, tu seras choisi pour représenter ton pays dans un concours de chant… mais tu devras chanter sous l'eau.",
        "Dans un futur lointain, tu seras une légende vivante, reconnu pour avoir inventé la première machine à fabriquer des sourires."
        "Dans 5 minutes, tu verras un nuage prendre la forme de ton visage, mais il te fera une grimace étrange.",
        "Demain, tu seras invité à une réunion secrète de licornes qui discuteront des nouvelles tendances en matière de paillettes.",
        "Prochainement, un dauphin te confiera un message codé que tu devras résoudre… mais il sera écrit en chantant.",
        "Un dragon viendra te rendre visite et te proposera de partager son trésor… mais il s’avère que ce trésor est un stock infini de bonbons à la menthe.",
        "Dans quelques jours, tu apprendras à parler couramment le langage des grenouilles, mais seulement quand il pleut.",
        "Cette semaine, un voleur masqué viendra te voler une chaussette… mais il te laissera un billet pour un concert de musique classique.",
        "Prochainement, un fantôme te demandera de l'aider à retrouver ses clés perdues… mais tu découvriras qu'il a oublié où il les a mises.",
        "Dans un futur proche, tu seras élu président d'un club de fans de légumes, et tu recevras une médaille en forme de carotte.",
        "Bientôt, tu découvriras un raccourci secret qui te permettra de voyager dans des mondes parallèles… mais il te fera revenir à ton point de départ.",
        "Dans un mois, tu recevras une lettre d'invitation à un bal masqué organisé par des robots, mais tu ne pourras pas danser car tu porteras des chaussons trop grands."

    ]

    prediction = random.choice(predicions)

    embed = discord.Embed(
        title=f"🔮 Prédiction pour {user.name} 🔮",
        description=f"**Prédiction :**\n\n{prediction}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Le futur est incertain… mais amusant ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Liste de blagues
blagues = [
    "Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? ||Parce que sinon ils tombent toujours dans le bateau.||",
    "Pourquoi les canards sont toujours à l'heure ? ||Parce qu'ils sont dans les starting-quack !||",
    "Quel est le comble pour un électricien ? ||De ne pas être au courant.||",
    "Pourquoi les maths sont tristes ? ||Parce qu'elles ont trop de problèmes.||",
    "Que dit une imprimante à une autre imprimante ? *||'T'as du papier ?'||",
    "Pourquoi les poissons détestent l'ordinateur ? ||Parce qu'ils ont peur du net !||",
    "Comment appelle-t-on un chat qui a perdu son GPS ? ||Un chat égaré.||",
    "Pourquoi les squelettes ne se battent-ils jamais entre eux ? ||Parce qu'ils n'ont pas de cœur !||",
    "Quel est le comble pour un plombier ? ||D'avoir un tuyau percé.||",
    "Comment appelle-t-on un chien magique ? ||Un labra-cadabra !||"
]

# Commande !blague
@bot.command()
async def blague(ctx):
    # Choisir une blague au hasard
    blague_choisie = random.choice(blagues)
    # Envoyer la blague dans le salon
    await ctx.send(blague_choisie)

#------------------------------------------------------------------------- Commandes de Moderation : +ban, +unban, +mute, +unmute, +kick, +warn

# 🎨 Fonction pour créer un embed formaté
def create_embed(title, description, color, ctx, member=None, action=None, reason=None, duration=None):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=ctx.message.created_at)
    embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    if member:
        embed.add_field(name="👤 Membre sanctionné", value=member.mention, inline=True)
    if action:
        embed.add_field(name="⚖️ Sanction", value=action, inline=True)
    if reason:
        embed.add_field(name="📜 Raison", value=reason, inline=False)
    if duration:
        embed.add_field(name="⏳ Durée", value=duration, inline=True)

    return embed

# 🎯 Vérification des permissions et hiérarchie
def has_permission(ctx, perm):
    return ctx.author.id == ISEY_ID or getattr(ctx.author.guild_permissions, perm, False)

def is_higher_or_equal(ctx, member):
    return member.top_role >= ctx.author.top_role

# 📩 Envoi d'un log
async def send_log(ctx, member, action, reason, duration=None):
    guild_id = ctx.guild.id
    settings = GUILD_SETTINGS.get(guild_id, {})
    log_channel_id = settings.get("sanctions_channel")

    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = create_embed("🚨 Sanction appliquée", f"{member.mention} a été sanctionné.", discord.Color.red(), ctx, member, action, reason, duration)
            await log_channel.send(embed=embed)

# 📩 Envoi d'un message privé à l'utilisateur sanctionné
async def send_dm(ctx, member, action, reason, duration=None):
    try:
        embed = create_embed("🚨 Vous avez reçu une sanction", "Consultez les détails ci-dessous.", discord.Color.red(), ctx, member, action, reason, duration)
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un DM à {member.display_name}.")

@bot.hybrid_command(
    name="mute",
    description="Mute temporairement un membre (timeout) avec une durée spécifiée."
)
async def mute(
    ctx,
    member: discord.Member = None,
    duration_with_unit: str = None,
    *,
    reason="Aucune raison spécifiée"
):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à mute.")
    
    if duration_with_unit is None:
        return await ctx.send("❌ Il manque un argument : vous devez préciser une durée (ex: `10m`, `1h`, `2j`).")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous mute vous-même.")

    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")

    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de mute des membres.")

    if member.timed_out_until and member.timed_out_until > datetime.utcnow().replace(tzinfo=timezone.utc):
        timeout_end = member.timed_out_until.strftime('%d/%m/%Y à %H:%M:%S')
        return await ctx.send(f"❌ {member.mention} est déjà en timeout jusqu'au {timeout_end} UTC.")

    time_units = {"m": "minutes", "h": "heures", "j": "jours"}
    try:
        duration = int(duration_with_unit[:-1])
        unit = duration_with_unit[-1].lower()
        if unit not in time_units:
            raise ValueError
    except ValueError:
        return await ctx.send("❌ Format invalide ! Utilisez un nombre suivi de `m` (minutes), `h` (heures) ou `j` (jours).")

    time_deltas = {"m": timedelta(minutes=duration), "h": timedelta(hours=duration), "j": timedelta(days=duration)}
    duration_time = time_deltas[unit]
    duration_str = f"{duration} {time_units[unit]}"

    try:
        await member.timeout(duration_time, reason=reason)

        embed = create_embed(
            "⏳ Mute",
            f"{member.mention} a été muté pour {duration_str}.",
            discord.Color.blue(),
            ctx,
            member,
            "Mute",
            reason,
            duration_str
        )
        await ctx.send(embed=embed)
        await send_dm(ctx, member, "Mute", reason, duration_str)

        sanction_data = {
            "guild_id": str(ctx.guild.id),
            "user_id": str(member.id),
            "action": "Mute",
            "reason": reason,
            "duration": duration_str,
            "timestamp": datetime.utcnow()
        }
        collection7.insert_one(sanction_data)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de mute ce membre. Vérifiez les permissions du bot.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors de l'application du mute : {e}")
    except Exception as e:
        await ctx.send(f"❌ Une erreur inattendue s'est produite : {str(e)}")
        
@bot.hybrid_command(
    name="ban",
    description="Bannit un membre du serveur avec une raison optionnelle."
)
async def ban(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre ou fournir un ID pour bannir.")

    # Si le membre fourni est une mention
    if isinstance(member, discord.Member):
        target_member = member
    else:
        # Si le membre est un ID
        target_member = get(ctx.guild.members, id=int(member))

    # Si le membre est introuvable dans le serveur
    if target_member is None:
        return await ctx.send("❌ Aucun membre trouvé avec cet ID ou mention.")

    if ctx.author == target_member:
        return await ctx.send("🚫 Vous ne pouvez pas vous bannir vous-même.")
    
    if is_higher_or_equal(ctx, target_member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    
    if has_permission(ctx, "ban_members"):
        await member.ban(reason=reason)
        embed = create_embed("🔨 Ban", f"{member.mention} a été banni.", discord.Color.red(), ctx, member, "Ban", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Ban", reason)
        await send_dm(member, "Ban", reason)

        # Enregistrement de la sanction
        add_sanction(ctx.guild.id, member.id, "Ban", reason)

@bot.hybrid_command(
    name="unban",
    description="Débannit un utilisateur du serveur à partir de son ID."
)
async def unban(ctx, user_id: int = None):
    if user_id is None:
        return await ctx.send("❌ Il manque un argument : vous devez spécifier l'ID d'un utilisateur à débannir.")

    if has_permission(ctx, "ban_members"):
        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = create_embed("🔓 Unban", f"{user.mention} a été débanni.", discord.Color.green(), ctx, user, "Unban", "Réintégration")
            await ctx.send(embed=embed)
            await send_log(ctx, user, "Unban", "Réintégration")
            await send_dm(user, "Unban", "Réintégration")
        except discord.NotFound:
            return await ctx.send("❌ Aucun utilisateur trouvé avec cet ID.")
        except discord.Forbidden:
            return await ctx.send("❌ Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.")

@bot.hybrid_command(
    name="kick",
    description="Expulse un membre du serveur avec une raison optionnelle."
)
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à expulser.")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous expulser vous-même.")
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    if has_permission(ctx, "kick_members"):
        await member.kick(reason=reason)
        embed = create_embed("👢 Kick", f"{member.mention} a été expulsé.", discord.Color.orange(), ctx, member, "Kick", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Kick", reason)
        await send_dm(member, "Kick", reason)

@bot.hybrid_command(
    name="unmute",
    description="Retire le mute d'un membre (timeout)."
)
async def unmute(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à démuter.")

    if has_permission(ctx, "moderate_members"):
        await member.timeout(None)
        embed = create_embed("🔊 Unmute", f"{member.mention} a été démuté.", discord.Color.green(), ctx, member, "Unmute", "Fin du mute")
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Unmute", "Fin du mute")
        await send_dm(member, "Unmute", "Fin du mute")

# Fonction de vérification des permissions
async def check_permissions(ctx):
    # Vérifier si l'utilisateur a la permission "Manage Messages"
    return ctx.author.guild_permissions.manage_messages or ctx.author.id == 1166334752186433567

# Fonction pour vérifier si le membre est immunisé
async def is_immune(member):
    # Exemple de logique d'immunité (peut être ajustée)
    # Vérifie si le membre a un rôle spécifique ou une permission
    return any(role.name == "Immunité" for role in member.roles)

# Fonction pour envoyer un message de log
async def send_log(ctx, member, action, reason):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")  # Remplacer par le salon de log approprié
    if log_channel:
        embed = discord.Embed(
            title="Avertissement",
            description=f"**Membre :** {member.mention}\n**Action :** {action}\n**Raison :** {reason}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Avertissement donné par {ctx.author}", icon_url=ctx.author.avatar.url)
        await log_channel.send(embed=embed)

# Fonction pour envoyer un message en DM au membre
async def send_dm(member, action, reason):
    try:
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"**Action :** {action}\n**Raison :** {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text="N'oublie pas de respecter les règles !")
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un message privé à {member.name}")

@bot.hybrid_command(
    name="warn",
    description="Avertit un membre avec une raison optionnelle."
)
async def warn(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à avertir.")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous avertir vous-même.")
    
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas avertir quelqu'un de votre niveau ou supérieur.")
    
    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de donner des avertissements.")
    
    try:
        # Ajout du warning à la base de données
        sanction_data = {
            "guild_id": str(ctx.guild.id),
            "user_id": str(member.id),
            "action": "Warn",
            "reason": reason,
            "timestamp": datetime.utcnow()
        }

        # Tentative d'insertion dans MongoDB
        collection7.insert_one(sanction_data)
        print(f"Sanction ajoutée à la base de données pour {member.mention}")

        # Embeds et réponses
        embed = create_embed("⚠️ Avertissement donné", f"{member.mention} a reçu un avertissement pour la raison suivante :\n{reason}", discord.Color.orange(), ctx, member, "Avertissement", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Warn", reason)
        await send_dm(member, "Avertissement", reason)

    except Exception as e:
        # Log de l'erreur dans la console pour faciliter le débogage
        print(f"Erreur lors de l'exécution de la commande warn : {e}")
        await ctx.send(f"❌ Une erreur s'est produite lors de l'exécution de la commande. Détails : {str(e)}")

@bot.hybrid_command(
    name="warnlist",
    description="Affiche la liste des avertissements d’un membre."
)
async def warnlist(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre.")
    
    sanctions = collection7.find({
        "guild_id": str(ctx.guild.id),
        "user_id": str(member.id),
        "action": "Warn"
    })

    count = collection7.count_documents({
        "guild_id": str(ctx.guild.id),
        "user_id": str(member.id),
        "action": "Warn"
    })

    if count == 0:
        return await ctx.send(f"✅ {member.mention} n'a aucun avertissement.")

    embed = discord.Embed(title=f"Avertissements de {member.name}", color=discord.Color.orange())
    for sanction in sanctions:
        date = sanction["timestamp"].strftime("%d/%m/%Y à %Hh%M")
        embed.add_field(name=f"Le {date}", value=sanction["reason"], inline=False)

    await ctx.send(embed=embed)

@bot.hybrid_command(
    name="unwarn",
    description="Supprime un avertissement d’un membre à partir de son index dans la warnlist."
)
async def unwarn(ctx, member: discord.Member = None, index: int = None):
    if member is None or index is None:
        return await ctx.send("❌ Utilisation : `/unwarn <membre> <index>`.")

    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de retirer des avertissements.")

    # Récupère les avertissements du membre
    warnings = list(collection7.find({
        "guild_id": str(ctx.guild.id),
        "user_id": str(member.id),
        "action": "Warn"
    }).sort("timestamp", 1))

    if len(warnings) == 0:
        return await ctx.send(f"✅ {member.mention} n'a aucun avertissement.")

    if index < 1 or index > len(warnings):
        return await ctx.send(f"❌ Index invalide. Ce membre a {len(warnings)} avertissement(s).")

    try:
        to_delete = warnings[index - 1]
        collection7.delete_one({"_id": to_delete["_id"]})

        embed = create_embed(
            "✅ Avertissement retiré",
            f"L’avertissement n°{index} de {member.mention} a été supprimé.",
            discord.Color.green(),
            ctx,
            member,
            "Unwarn",
            to_delete["reason"]
        )

        await ctx.send(embed=embed)
        await send_log(ctx, member, "Unwarn", to_delete["reason"])
        await send_dm(member, "Unwarn", f"Ton avertissement datant du {to_delete['timestamp'].strftime('%d/%m/%Y à %Hh%M')} a été retiré.")
    
    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande unwarn : {e}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la suppression de l'avertissement. Détails : {str(e)}")

#------------------------------------------------------------------------- Commandes Utilitaires : +vc, +alerte, +uptime, +ping, +roleinfo
sent_embed_channels = {}

@bot.command()
async def vc(ctx):
    print("Commande 'vc' appelée.")

    try:
        guild = ctx.guild
        print(f"Guild récupérée: {guild.name} (ID: {guild.id})")

        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        voice_members = sum(len(voice_channel.members) for voice_channel in guild.voice_channels)
        boosts = guild.premium_subscription_count or 0
        owner_member = guild.owner
        verification_level = guild.verification_level.name
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        server_created_at = guild.created_at.strftime('%d %B %Y')

        # Récupérer ou créer un lien d'invitation pour le serveur
        invites = await guild.invites()
        if invites:
            server_invite = invites[0].url  # Utilise le premier lien d'invitation trouvé
        else:
            # Crée une nouvelle invitation valide pendant 24h
            server_invite = await guild.text_channels[0].create_invite(max_age=86400)  # 86400 secondes = 24 heures

        embed = discord.Embed(title=f"📊 Statistiques de {guild.name}", color=discord.Color.purple())

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👥 Membres", value=f"**{total_members}**", inline=True)
        embed.add_field(name="🟢 Membres en ligne", value=f"**{online_members}**", inline=True)
        embed.add_field(name="🎙️ En vocal", value=f"**{voice_members}**", inline=True)
        embed.add_field(name="💎 Boosts", value=f"**{boosts}**", inline=True)

        embed.add_field(name="👑 Propriétaire", value=f"<@{owner_member.id}>", inline=True)
        embed.add_field(name="🔒 Niveau de vérification", value=f"**{verification_level}**", inline=True)
        embed.add_field(name="📝 Canaux textuels", value=f"**{text_channels}**", inline=True)
        embed.add_field(name="🔊 Canaux vocaux", value=f"**{voice_channels}**", inline=True)
        embed.add_field(name="📅 Créé le", value=f"**{server_created_at}**", inline=False)
        embed.add_field(name="🔗 Lien du serveur", value=f"[{guild.name}]({server_invite})", inline=False)

        embed.set_footer(text="📈 Statistiques mises à jour en temps réel | ♥️ by Iseyg")

        await ctx.send(embed=embed)
        print("Embed envoyé avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande 'vc': {e}")
        await ctx.send("Une erreur est survenue lors de l'exécution de la commande.")
        return  # Empêche l'exécution du reste du code après une erreur

@bot.hybrid_command(
    name="ping",
    description="Affiche le Ping du bot."
)
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Latence en ms
    embed = discord.Embed(title="Pong!", description=f"Latence: {latency}ms", color=discord.Color.green())

    await ctx.send(embed=embed)

@bot.tree.command(name="info-rôle", description="Obtenez des informations détaillées sur un rôle")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    # Vérifier si le rôle existe
    if role is None:
        embed = discord.Embed(title="Erreur", description="Rôle introuvable.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    else:
        # Obtenir tous les rôles triés du plus haut au plus bas
        sorted_roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        total_roles = len(sorted_roles)
        
        # Trouver la position inversée du rôle
        inverse_position = total_roles - sorted_roles.index(role)

        embed = discord.Embed(
            title=f"Informations sur le rôle: {role.name}",
            color=role.color,
            timestamp=interaction.created_at
        )
        
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.add_field(name="ID", value=role.id, inline=False)
        embed.add_field(name="Couleur", value=str(role.color), inline=False)
        embed.add_field(name="Nombre de membres", value=len(role.members), inline=False)
        embed.add_field(name="Position dans la hiérarchie", value=f"{inverse_position}/{total_roles}", inline=False)
        embed.add_field(name="Mentionnable", value=role.mentionable, inline=False)
        embed.add_field(name="Gérer les permissions", value=role.managed, inline=False)
        embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        embed.add_field(name="Mention", value=role.mention, inline=False)

        embed.set_footer(text=f"Commande demandée par {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

@bot.hybrid_command(
    name="uptime",
    description="Affiche l'uptime du bot."
)
async def uptime(ctx):
    uptime_seconds = round(time.time() - start_time)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    embed = discord.Embed(
        title="Uptime du bot",
        description=f"Le bot est en ligne depuis : {days} jours, {hours} heures, {minutes} minutes, {seconds} secondes",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.tree.command(name="calcul", description="Effectue une opération mathématique")
@app_commands.describe(nombre1="Le premier nombre", operation="L'opération à effectuer (+, -, *, /)", nombre2="Le deuxième nombre")
async def calcul(interaction: discord.Interaction, nombre1: float, operation: str, nombre2: float):
    await interaction.response.defer()  # ✅ Correctement placé à l'intérieur de la fonction

    if operation == "+":
        resultat = nombre1 + nombre2
    elif operation == "-":
        resultat = nombre1 - nombre2
    elif operation == "*":
        resultat = nombre1 * nombre2
    elif operation == "/":
        if nombre2 != 0:
            resultat = nombre1 / nombre2
        else:
            await interaction.followup.send("❌ Erreur : Division par zéro impossible.")
            return
    else:
        await interaction.followup.send("❌ Opération invalide. Utilisez '+', '-', '*', ou '/'.")
        return

    embed = discord.Embed(
        title="📊 Résultat du calcul",
        description=f"{nombre1} {operation} {nombre2} = **{resultat}**",
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="calcul-pourcentage", description="Calcule un pourcentage d'un nombre")
@app_commands.describe(nombre="Le nombre de base", pourcentage="Le pourcentage à appliquer (ex: 15 pour 15%)")
async def calcul(interaction: discord.Interaction, nombre: float, pourcentage: float):
    await interaction.response.defer()  # ✅ Correctement placé à l'intérieur de la fonction

    resultat = (nombre * pourcentage) / 100
    embed = discord.Embed(
        title="📊 Calcul de pourcentage",
        description=f"{pourcentage}% de {nombre} = **{resultat}**",
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed)

# Installer PyNaCl 
try:
    import nacl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyNaCl"])

#------------------------------------------------------------------------- Commande Voice : /connect, /disconnect
# Commande /connect
@bot.tree.command(name="connect", description="Connecte le bot à un salon vocal spécifié.")
@app_commands.describe(channel="Choisissez un salon vocal où connecter le bot")
@commands.has_permissions(administrator=True)
async def connect(interaction: discord.Interaction, channel: discord.VoiceChannel):
    try:
        if not interaction.guild.voice_client:
            await channel.connect()
            embed = discord.Embed(
                title="✅ Connexion réussie !",
                description=f"Le bot a rejoint **{channel.name}**.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Déjà connecté",
                description="Le bot est déjà dans un salon vocal.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Une erreur est survenue : `{e}`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Commande /disconnect
@bot.tree.command(name="disconnect", description="Déconnecte le bot du salon vocal.")
@commands.has_permissions(administrator=True)
async def disconnect(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="🚫 Déconnexion réussie",
            description="Le bot a quitté le salon vocal.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ Pas connecté",
            description="Le bot n'est dans aucun salon vocal.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
#------------------------------------------------------------------------------------------

# Commande pour ajouter une idée (sans restriction d'administrateur)
@bot.tree.command(name="idée", description="Rajoute une idée dans la liste")
async def ajouter_idee(interaction: discord.Interaction, idee: str):
    user_id = interaction.user.id  # Utilisation de interaction.user.id pour obtenir l'ID utilisateur
    
    # Vérifier si l'utilisateur a déjà des idées dans la base de données
    idees_data = collection8.find_one({"user_id": str(user_id)})
    
    if idees_data:
        # Si des idées existent déjà, on ajoute l'idée à la liste existante
        collection8.update_one(
            {"user_id": str(user_id)},
            {"$push": {"idees": idee}}  # Ajoute l'idée à la liste des idées existantes
        )
    else:
        # Si l'utilisateur n'a pas encore d'idées, on crée un nouveau document avec cette idée
        collection8.insert_one({
            "user_id": str(user_id),
            "idees": [idee]  # Crée une nouvelle liste d'idées avec l'idée ajoutée
        })
    
    embed = discord.Embed(title="Idée ajoutée !", description=f"**{idee}** a été enregistrée.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

# Commande pour lister les idées
@bot.command(name="listi")
async def liste_idees(ctx):
    user_id = ctx.author.id
    
    # Chercher les idées de l'utilisateur dans la base de données
    idees_data = collection8.find_one({"user_id": str(user_id)})
    
    if not idees_data or not idees_data.get("idees"):
        embed = discord.Embed(title="Aucune idée enregistrée", description="Ajoute-en une avec /idées !", color=discord.Color.red())
    else:
        embed = discord.Embed(title="Tes idées", color=discord.Color.blue())
        for idx, idee in enumerate(idees_data["idees"], start=1):
            embed.add_field(name=f"Idée {idx}", value=idee, inline=False)
    
    await ctx.send(embed=embed)


# Commande pour supprimer une idée
@bot.tree.command(name="remove-idee", description="Supprime une de tes idées enregistrées")
async def remove_idee(interaction: discord.Interaction):
    user_id = interaction.user.id  # Utilisation de interaction.user.id pour obtenir l'ID utilisateur
    
    # Chercher les idées de l'utilisateur dans la base de données
    idees_data = collection8.find_one({"user_id": str(user_id)})
    
    if not idees_data or not idees_data.get("idees"):
        embed = discord.Embed(title="Aucune idée enregistrée", description="Ajoute-en une avec /idées !", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    idees = idees_data["idees"]

    # Créer un menu déroulant pour permettre à l'utilisateur de choisir une idée à supprimer
    options = [discord.SelectOption(label=f"Idée {idx+1}: {idee}", value=str(idx)) for idx, idee in enumerate(idees)]
    
    select = Select(placeholder="Choisis une idée à supprimer", options=options)
    
    # Définir l'interaction pour supprimer l'idée
    async def select_callback(interaction: discord.Interaction):
        selected_idee_index = int(select.values[0])
        idee_a_supprimer = idees[selected_idee_index]
        
        # Supprimer l'idée sélectionnée de la base de données
        collection8.update_one(
            {"user_id": str(user_id)},
            {"$pull": {"idees": idee_a_supprimer}}  # Supprime l'idée de la liste
        )
        
        embed = discord.Embed(
            title="Idée supprimée !",
            description=f"L'idée **{idee_a_supprimer}** a été supprimée.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    select.callback = select_callback

    view = View()
    view.add_item(select)
    
    embed = discord.Embed(
        title="Choisis l'idée à supprimer",
        description="Sélectionne une idée à supprimer dans le menu déroulant.",
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(embed=embed, view=view)

#--------------------------------------------------------------------------------------------
# --- Classe du formulaire de suggestion ---
class SuggestionModal(Modal):
    def __init__(self):
        super().__init__(title="💡 Nouvelle Suggestion")

        self.suggestion_input = TextInput(
            label="Entrez votre suggestion",
            style=discord.TextStyle.paragraph,
            placeholder="Écrivez ici...",
            required=True,
            max_length=1000
        )
        self.add_item(self.suggestion_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        data = collection20.find_one({"guild_id": guild_id})

        if not data or "suggestion_channel_id" not in data or "suggestion_role_id" not in data:
            return await interaction.response.send_message("❌ Le salon ou le rôle des suggestions n'a pas été configuré.", ephemeral=True)

        channel = interaction.client.get_channel(int(data["suggestion_channel_id"]))
        role = interaction.guild.get_role(int(data["suggestion_role_id"]))

        if not channel or not role:
            return await interaction.response.send_message("❌ Impossible de trouver le salon ou le rôle configuré.", ephemeral=True)

        embed = discord.Embed(
            title="💡 Nouvelle Suggestion",
            description=self.suggestion_input.value,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Suggéré par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        sent_message = await channel.send(
            content=f"{role.mention} 🚀 Une nouvelle suggestion a été soumise !",
            embed=embed
        )

        await sent_message.edit(view=SuggestionView(message_id=sent_message.id))

        await interaction.response.send_message("✅ Votre suggestion a été envoyée avec succès !", ephemeral=True)

# --- Classe du formulaire de commentaire ---
class CommentModal(Modal):
    def __init__(self, original_message_id: int):
        super().__init__(title="💬 Commenter une suggestion")
        self.message_id = original_message_id

        self.comment_input = TextInput(
            label="Votre commentaire",
            placeholder="Exprimez votre avis ou amélioration...",
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        self.add_item(self.comment_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        data = collection20.find_one({"guild_id": guild_id})

        if not data or "suggestion_channel_id" not in data:
            return await interaction.response.send_message("❌ Le salon de suggestion est mal configuré.", ephemeral=True)

        channel = interaction.client.get_channel(int(data["suggestion_channel_id"]))
        if not channel:
            return await interaction.response.send_message("❌ Le salon de suggestion est introuvable.", ephemeral=True)

        comment_embed = discord.Embed(
            title="🗨️ Nouveau commentaire sur une suggestion",
            description=self.comment_input.value,
            color=discord.Color.blurple()
        )
        comment_embed.set_footer(text=f"Par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        await channel.send(content=f"📝 Commentaire sur la suggestion ID `{self.message_id}` :", embed=comment_embed)
        await interaction.response.send_message("✅ Commentaire envoyé avec succès !", ephemeral=True)

# --- Vue avec les boutons ---
class SuggestionView(View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id

        self.add_item(Button(label="✅ Approuver", style=discord.ButtonStyle.green, custom_id="suggestion_approve"))
        self.add_item(Button(label="❌ Refuser", style=discord.ButtonStyle.red, custom_id="suggestion_decline"))
        self.add_item(Button(label="💬 Commenter", style=discord.ButtonStyle.blurple, custom_id=f"suggestion_comment:{message_id}"))

# --- Interaction avec les boutons ---
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")

        if custom_id == "suggestion_approve":
            await interaction.response.send_message("✅ Suggestion approuvée !", ephemeral=True)
        elif custom_id == "suggestion_decline":
            await interaction.response.send_message("❌ Suggestion refusée.", ephemeral=True)
        elif custom_id.startswith("suggestion_comment:"):
            try:
                message_id = int(custom_id.split(":")[1])
                await interaction.response.send_modal(CommentModal(original_message_id=message_id))
            except Exception:
                await interaction.response.send_message("❌ Erreur lors de l'ouverture du commentaire.", ephemeral=True)

# --- Commande /suggestion pour envoyer une suggestion ---
@bot.tree.command(name="suggestion", description="💡 Envoie une suggestion pour le serveur")
async def suggest(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    data = collection20.find_one({"guild_id": guild_id})

    if not data or "suggestion_channel_id" not in data or "suggestion_role_id" not in data:
        return await interaction.response.send_message("❌ Le système de suggestion n'est pas encore configuré.", ephemeral=True)

    await interaction.response.send_modal(SuggestionModal())

# --- Commande /set_suggestion pour configurer le salon + rôle ---
@bot.tree.command(name="set-suggestion", description="📝 Définir le salon et rôle pour les suggestions")
@app_commands.describe(channel="Salon pour recevoir les suggestions", role="Rôle à ping lors des suggestions")
async def set_suggestion(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Tu n'as pas les permissions nécessaires.", ephemeral=True)

    guild_id = str(interaction.guild.id)

    collection20.update_one(
        {"guild_id": guild_id},
        {"$set": {
            "suggestion_channel_id": str(channel.id),
            "suggestion_role_id": str(role.id)
        }},
        upsert=True
    )

    await interaction.response.send_message(
        f"✅ Le système de suggestions est maintenant configuré avec {channel.mention} et {role.mention}.",
        ephemeral=True
    )
#-------------------------------------------------------------------------------- Sondage: /sondage

# Dictionnaire global pour les cooldowns des sondages
user_cooldown = {}

# Classe du Modal pour créer un sondage
class PollModal(discord.ui.Modal, title="📊 Créer un sondage interactif"):
    def __init__(self):
        super().__init__()

        self.question = discord.ui.TextInput(
            label="💬 Question principale",
            placeholder="Ex : Quel est votre fruit préféré ?",
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.options = discord.ui.TextInput(
            label="🧩 Choix possibles (séparés par des virgules)",
            placeholder="Ex : 🍎 Pomme, 🍌 Banane, 🍇 Raisin, 🍍 Ananas",
            max_length=300
        )

        self.add_item(self.question)
        self.add_item(self.options)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Cooldown de 60s
        if user_id in user_cooldown and time.time() - user_cooldown[user_id] < 60:
            return await interaction.response.send_message(
                "⏳ Vous devez attendre **60 secondes** avant de créer un nouveau sondage.",
                ephemeral=True
            )

        user_cooldown[user_id] = time.time()

        question = self.question.value
        options_raw = self.options.value
        options = [opt.strip() for opt in options_raw.split(",") if opt.strip()]

        if len(options) < 2 or len(options) > 10:
            return await interaction.response.send_message(
                "❗ Veuillez entrer **entre 2 et 10 choix** maximum pour votre sondage.",
                ephemeral=True
            )

        # Génération de l'embed
        embed = discord.Embed(
            title="📢 Nouveau sondage disponible !",
            description=(
                f"🧠 **Question** :\n> *{question}*\n\n"
                f"🎯 **Choix proposés** :\n" +
                "\n".join([f"{chr(0x1F1E6 + i)} ┇ {opt}" for i, opt in enumerate(options)])
            ),
            color=discord.Color.teal()
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4140/4140047.png")
        embed.set_footer(text="Réagissez ci-dessous pour voter 🗳️")
        embed.timestamp = discord.utils.utcnow()

        message = await interaction.channel.send(embed=embed)

        # Ajout des réactions 🇦, 🇧, ...
        for i in range(len(options)):
            await message.add_reaction(chr(0x1F1E6 + i))

        await interaction.response.send_message("✅ Votre sondage a été publié avec succès !", ephemeral=True)

# Commande slash /sondage
@bot.tree.command(name="sondage", description="📊 Créez un sondage stylé avec des choix")
async def sondage(interaction: discord.Interaction):
    await interaction.response.send_modal(PollModal())

#-------------------------------------------------------------------------------- Rappel: /rappel

THUMBNAIL_URL = "https://github.com/Iseyg91/Etherya/blob/main/3e3bd3c24e33325c7088f43c1ae0fadc.png?raw=true"

# Fonction pour vérifier si une URL est valide
def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)?'  # http:// ou https:// (optionnel)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domaine
        r'(/.*)?$'  # chemin (optionnel)
    )
    return bool(re.match(regex, url))

class EmbedBuilderView(discord.ui.View):
    def __init__(self, author: discord.User, channel: discord.TextChannel):
        super().__init__(timeout=180)
        self.author = author
        self.channel = channel
        self.embed = discord.Embed(title="Titre", description="Description", color=discord.Color.blue())
        self.embed.set_thumbnail(url=THUMBNAIL_URL)
        self.second_image_url = None
        self.message = None  # Stocke le message contenant l'embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier cet embed.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Modifier le titre", style=discord.ButtonStyle.primary)
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedTitleModal(self))

    @discord.ui.button(label="Modifier la description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedDescriptionModal(self))

    @discord.ui.button(label="Changer la couleur", style=discord.ButtonStyle.primary)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = discord.Color.random()
        if self.message:
            await self.message.edit(embed=self.embed, view=self)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

    @discord.ui.button(label="Ajouter une image", style=discord.ButtonStyle.secondary)
    async def add_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedImageModal(self))

    @discord.ui.button(label="Ajouter 2ème image", style=discord.ButtonStyle.secondary)
    async def add_second_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedSecondImageModal(self))

    @discord.ui.button(label="Envoyer", style=discord.ButtonStyle.success)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        embeds = [self.embed]
        if self.second_image_url:
            second_embed = discord.Embed(color=self.embed.color)
            second_embed.set_image(url=self.second_image_url)
            embeds.append(second_embed)

        await self.channel.send(embeds=embeds)
        await interaction.response.send_message("✅ Embed envoyé !", ephemeral=True)

class EmbedTitleModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier le Titre")
        self.view = view
        self.title_input = discord.ui.TextInput(label="Nouveau Titre", required=True)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.title = self.title_input.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedDescriptionModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier la description")
        self.view = view
        self.description = discord.ui.TextInput(label="Nouvelle description", style=discord.TextStyle.paragraph, max_length=4000)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.description = self.description.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une image")
        self.view = view
        self.image_input = discord.ui.TextInput(label="URL de l'image", required=True)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if is_valid_url(self.image_input.value):
            self.view.embed.set_image(url=self.image_input.value)
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

class EmbedSecondImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une 2ème image")
        self.view = view
        self.second_image_input = discord.ui.TextInput(label="URL de la 2ème image", required=True)
        self.add_item(self.second_image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if is_valid_url(self.second_image_input.value):
            self.view.second_image_url = self.second_image_input.value
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

@bot.tree.command(name="embed", description="Créer un embed personnalisé")
async def embed_builder(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    admin_role_id = 792755123587645461  # ID du rôle admin
    if not any(role.id == admin_role_id or role.permissions.administrator for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)

    view = EmbedBuilderView(interaction.user, interaction.channel)
    response = await interaction.followup.send(embed=view.embed, view=view, ephemeral=True)
    view.message = response

async def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.command()
@commands.check(is_admin)
async def listban(ctx):
    bans = [ban async for ban in ctx.guild.bans()]

    if not bans:
        embed = discord.Embed(
            title="📜 Liste des bannis",
            description="✅ Aucun utilisateur n'est actuellement banni du serveur.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
        return await ctx.send(embed=embed)

    pages = []
    content = ""

    for i, ban in enumerate(bans, 1):
        user = ban.user
        reason = ban.reason or "Aucune raison spécifiée"
        entry = f"🔹 **{user.name}#{user.discriminator}**\n📝 *{reason}*\n\n"

        if len(content + entry) > 1000:  # pour laisser de la marge avec la limite d'embed
            pages.append(content)
            content = ""
        content += entry

    if content:
        pages.append(content)

    for idx, page in enumerate(pages, 1):
        embed = discord.Embed(
            title=f"📜 Liste des bannis (Page {idx}/{len(pages)})",
            description=page,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Total : {len(bans)} utilisateur(s) banni(s)")
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

@bot.command(name="unbanall")
@commands.check(is_admin)
async def unbanall(ctx):
    async for ban_entry in ctx.guild.bans():
        await ctx.guild.unban(ban_entry.user)
    await ctx.send("✅ Tous les utilisateurs bannis ont été débannis !")
    
@bot.command()
async def alladmin(ctx):
    """Affiche la liste des administrateurs avec un joli embed"""
    admins = [member for member in ctx.guild.members if member.guild_permissions.administrator]

    if not admins:
        embed = discord.Embed(
            title="❌ Aucun administrateur trouvé",
            description="Il semble que personne n'ait les permissions d'administrateur sur ce serveur.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Création d'un embed stylé
    embed = discord.Embed(
        title="📜 Liste des administrateurs",
        description=f"Voici les {len(admins)} administrateurs du serveur **{ctx.guild.name}** :",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text=f"Commande demandée par {ctx.author.name}", icon_url=ctx.author.avatar.url)

    for admin in admins:
        embed.add_field(name=f"👤 {admin.name}#{admin.discriminator}", value=f"ID : `{admin.id}`", inline=False)

    await ctx.send(embed=embed)

# Dictionnaire pour stocker les messages supprimés {channel_id: deque[(timestamp, auteur, contenu)]}
sniped_messages = {}

@bot.command()
async def snipe(ctx, index: int = 1):
    channel_id = ctx.channel.id
    
    if channel_id not in sniped_messages or len(sniped_messages[channel_id]) == 0:
        await ctx.send("Aucun message récent supprimé trouvé !")
        return

    if not (1 <= index <= len(sniped_messages[channel_id])):
        await ctx.send(f"Il n'y a que {len(sniped_messages[channel_id])} messages enregistrés.")
        return

    timestamp, author, content = sniped_messages[channel_id][-index]
    embed = discord.Embed(
        title=f"Message supprimé de {author}",
        description=content,
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Demandé par {ctx.author}")

    await ctx.send(embed=embed)

class PresentationForm(discord.ui.Modal, title="📝 Faisons connaissance"):
    pseudo = TextInput(label="Ton pseudo", placeholder="Ex: Jean_57", required=True, max_length=50)
    age = TextInput(label="Ton âge", placeholder="Ex: 18", required=True, max_length=3)
    passion = TextInput(label="Ta passion principale", placeholder="Ex: Gaming, Musique...", required=True, max_length=100)
    bio = TextInput(label="Une courte bio", placeholder="Parle un peu de toi...", style=discord.TextStyle.paragraph, required=True, max_length=300)
    reseaux = TextInput(label="Tes réseaux sociaux préférés", placeholder="Ex: Twitter, TikTok, Discord...", required=False, max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        # Récupérer les données du formulaire
        presentation_data = {
            'pseudo': self.pseudo.value,
            'age': self.age.value,
            'passion': self.passion.value,
            'bio': self.bio.value,
            'reseaux': self.reseaux.value,
        }

        # On envoie la présentation dans le salon
        guild_id = interaction.guild.id
        guild_settings = load_guild_settings(guild_id)
        presentation_channel_id = guild_settings.get('presentation', {}).get('presentation_channel')

        if presentation_channel_id:
            presentation_channel = interaction.guild.get_channel(presentation_channel_id)

            if presentation_channel:
                embed = discord.Embed(
                    title=f"📢 Nouvelle présentation de {interaction.user.display_name}",
                    description="Voici une nouvelle présentation ! 🎉",
                    color=discord.Color.blurple()
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.add_field(name="👤 Pseudo", value=presentation_data['pseudo'], inline=True)
                embed.add_field(name="🎂 Âge", value=presentation_data['age'], inline=True)
                embed.add_field(name="🎨 Passion", value=presentation_data['passion'], inline=False)
                if presentation_data['reseaux']:
                    embed.add_field(name="🌐 Réseaux sociaux", value=presentation_data['reseaux'], inline=False)
                embed.add_field(name="📝 Bio", value=presentation_data['bio'], inline=False)
                embed.set_footer(text=f"Utilisateur ID: {interaction.user.id}", icon_url=interaction.user.display_avatar.url)

                await presentation_channel.send(embed=embed)

                await interaction.response.send_message("Ta présentation a été envoyée ! 🎉", ephemeral=True)
            else:
                await interaction.response.send_message("Le salon de présentation n'existe plus ou est invalide.", ephemeral=True)
        else:
            await interaction.response.send_message("Le salon de présentation n'a pas été configuré pour ce serveur.", ephemeral=True)

# --- Commande Slash ---
@bot.tree.command(name="presentation", description="Remplis un formulaire pour te présenter à la communauté !")
async def presentation(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild_settings = load_guild_settings(guild_id)
    presentation_channel_id = guild_settings.get('presentation', {}).get('presentation_channel')

    if presentation_channel_id:
        try:
            await interaction.response.send_modal(PresentationForm())  # Envoie un seul modal
        except discord.errors.HTTPException as e:
            print(f"Erreur lors de l'envoi du modal : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du formulaire. Veuillez réessayer.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "⚠️ Le salon de présentation n’a pas été configuré sur ce serveur. Veuillez contacter un administrateur.",
            ephemeral=True
        )

# Commande pour définir le salon de présentation
@bot.tree.command(name="set-presentation", description="Définit le salon où les présentations seront envoyées (admin uniquement)")
@app_commands.checks.has_permissions(administrator=True)
async def set_presentation(interaction: discord.Interaction, salon: discord.TextChannel):
    guild_id = interaction.guild.id
    channel_id = salon.id

    # Mise à jour ou insertion dans la collection21
    collection21.update_one(
        {"guild_id": guild_id},
        {"$set": {"presentation_channel": channel_id}},
        upsert=True
    )

    await interaction.response.send_message(
        f"✅ Le salon de présentation a bien été défini sur {salon.mention}.", ephemeral=True
    )

# Gérer les erreurs de permissions
@set_presentation.error
async def set_presentation_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):
    """Empêche @everyone de parler dans le salon actuel (admin only)."""
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Salon verrouillé. Seuls les rôles autorisés peuvent parler.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    """Autorise @everyone à parler dans le salon actuel (admin only)."""
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Salon déverrouillé. Tout le monde peut parler à nouveau.")

# Modal pour le feedback
class FeedbackModal(discord.ui.Modal, title="Envoyer un feedback"):

    feedback_type = discord.ui.TextInput(
        label="Type (Report ou Suggestion)",
        placeholder="Ex: Report",
        max_length=20
    )

    description = discord.ui.TextInput(
        label="Description",
        placeholder="Décris ton idée ou ton problème ici...",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(SALON_REPORT_ID)
        role_mention = f"<@&{ROLE_REPORT_ID}>"

        # Mention du rôle
        await channel.send(content=role_mention)

        # Embed amélioré
        embed = discord.Embed(
            title="📝 Nouveau Feedback Reçu",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🔖 Type", value=self.feedback_type.value, inline=False)
        embed.add_field(name="🧾 Description", value=self.description.value, inline=False)
        embed.add_field(name="👤 Utilisateur", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="🌐 Serveur", value=f"{interaction.guild.name} (`{interaction.guild.id}`)", inline=False)

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Feedback envoyé le")

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Ton feedback a bien été envoyé ! Merci !", ephemeral=True)

# Slash command
@bot.tree.command(name="feedback", description="Envoyer un report ou une suggestion")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_modal(FeedbackModal())

PROTECTIONS = [
    "anti_massban",
    "anti_masskick",
    "anti_bot",
    "anti_createchannel",
    "anti_deletechannel",
    "anti_createrole",
    "anti_deleterole",
    "anti_everyone",
    "anti_spam",
    "anti_links",
    "whitelist"
]

PROTECTION_DETAILS = {
    "anti_massban": ("🚫 Anti-MassBan", "Empêche les bannissements massifs."),
    "anti_masskick": ("👢 Anti-MassKick", "Empêche les expulsions massives."),
    "anti_bot": ("🤖 Anti-Bot", "Bloque l'ajout de bots non autorisés."),
    "anti_createchannel": ("📤 Anti-Création de salon", "Empêche la création non autorisée de salons."),
    "anti_deletechannel": ("📥 Anti-Suppression de salon", "Empêche la suppression non autorisée de salons."),
    "anti_createrole": ("➕ Anti-Création de rôle", "Empêche la création non autorisée de rôles."),
    "anti_deleterole": ("➖ Anti-Suppression de rôle", "Empêche la suppression non autorisée de rôles."),
    "anti_everyone": ("📣 Anti-Everyone", "Empêche l'utilisation abusive de @everyone ou @here."),
    "anti_spam": ("💬 Anti-Spam", "Empêche le spam excessif de messages."),
    "anti_links": ("🔗 Anti-Liens", "Empêche l'envoi de liens non autorisés."),
    "whitelist": ("✅ Liste blanche", "Utilisateurs exemptés des protections.")
}

def is_admin_or_isey():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id == ISEY_ID
    return commands.check(predicate)

def generate_global_status_bar(data: dict) -> str:
    protections = [prot for prot in PROTECTIONS if prot != "whitelist"]
    total = len(protections)
    enabled_count = sum(1 for prot in protections if data.get(prot, False))
    ratio = enabled_count / total

    bar_length = 10
    filled_length = round(bar_length * ratio)
    bar = "🟩" * filled_length + "⬛" * (bar_length - filled_length)
    return f"**Sécurité Globale :** `{enabled_count}/{total}`\n{bar}"


def format_protection_field(prot, data, guild, bot):
    name, desc = PROTECTION_DETAILS[prot]
    enabled = data.get(prot, False)
    status = "✅ Activée" if enabled else "❌ Désactivée"
    updated_by_id = data.get(f"{prot}_updated_by")
    updated_at = data.get(f"{prot}_updated_at")

    modifier = None
    if updated_by_id:
        modifier = guild.get_member(int(updated_by_id)) or updated_by_id

    formatted_date = ""
    if updated_at:
        dt = updated_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Paris"))
        formatted_date = f"🕓 {dt.strftime('%d/%m/%Y à %H:%M')}"

    mod_info = f"\n👤 Modifié par : {modifier.mention if isinstance(modifier, discord.Member) else modifier}" if modifier else ""
    date_info = f"\n{formatted_date}" if formatted_date else ""

    value = f"> {desc}\n> **Statut :** {status}{mod_info}{date_info}"
    return name, value

async def notify_owner_of_protection_change(guild, prot, new_value, interaction):
    if guild and guild.owner:
        try:
            embed = discord.Embed(
                title="🔐 Mise à jour d'une protection sur votre serveur",
                description=f"**Protection :** {PROTECTION_DETAILS[prot][0]}\n"
                            f"**Statut :** {'✅ Activée' if new_value else '❌ Désactivée'}",
                color=discord.Color.green() if new_value else discord.Color.red()
            )
            embed.add_field(
                name="👤 Modifiée par :",
                value=f"{interaction.user.mention} (`{interaction.user}`)",
                inline=False
            )
            embed.add_field(name="🏠 Serveur :", value=guild.name, inline=False)
            embed.add_field(
                name="🕓 Date de modification :",
                value=f"<t:{int(datetime.utcnow().timestamp())}:f>",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Infos supplémentaires :",
                value="Vous pouvez reconfigurer vos protections à tout moment avec la commande `/protection`.",
                inline=False
            )

            await guild.owner.send(embed=embed)
        except discord.Forbidden:
            print("Impossible d’envoyer un DM à l’owner.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du DM : {e}")

class ProtectionMenu(Select):
    def __init__(self, guild_id, protection_data, bot):
        self.guild_id = guild_id
        self.protection_data = protection_data
        self.bot = bot

        options = [
            discord.SelectOption(
                label=PROTECTION_DETAILS[prot][0],
                description="Activer ou désactiver cette protection.",
                emoji="🔒" if protection_data.get(prot, False) else "🔓",
                value=prot
            )
            for prot in PROTECTIONS if prot != "whitelist"
        ]

        super().__init__(
            placeholder="🔧 Choisissez une protection à modifier",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        prot = self.values[0]
        current = self.protection_data.get(prot, False)
        new_value = not current

        collection4.update_one(
            {"guild_id": str(self.guild_id)},
            {"$set": {
                prot: new_value,
                f"{prot}_updated_by": str(interaction.user.id),
                f"{prot}_updated_at": datetime.utcnow()
            }},
            upsert=True
        )

        self.protection_data[prot] = new_value
        self.protection_data[f"{prot}_updated_by"] = interaction.user.id
        self.protection_data[f"{prot}_updated_at"] = datetime.utcnow()

        guild = interaction.guild
        if guild and guild.owner:
            await notify_owner_of_protection_change(guild, prot, new_value, interaction)

        embed = discord.Embed(title="🛡️ Système de Protection", color=discord.Color.blurple())
        for p in PROTECTIONS:
            if p == "whitelist":
                whitelist_data = collection19.find_one({"guild_id": str(self.guild_id)}) or {}
                wl_users = whitelist_data.get("whitelist", [])
                if not wl_users:
                    embed.add_field(name=PROTECTION_DETAILS[p][0], value="Aucun utilisateur whitelisté.", inline=False)
                else:
                    members = []
                    for uid in wl_users:
                        user = interaction.guild.get_member(int(uid)) or await self.bot.fetch_user(int(uid))
                        members.append(f"- {user.mention if isinstance(user, discord.Member) else user.name}")
                    embed.add_field(name=PROTECTION_DETAILS[p][0], value="\n".join(members), inline=False)
            else:
                name, value = format_protection_field(p, self.protection_data, guild, self.bot)
                embed.add_field(name=name, value=value, inline=False)

        # ➕ Ajoute ce résumé en bas :
        embed.add_field(
            name="🔒 Résumé des protections",
            value=generate_global_status_bar(self.protection_data),
            inline=False
        )

        embed.set_footer(text="🎚️ Sélectionnez une option ci-dessous pour gérer la sécurité du serveur.")
        view = View()
        view.add_item(ProtectionMenu(self.guild_id, self.protection_data, self.bot))
        await interaction.response.edit_message(embed=embed, view=view)

class ProtectionView(View):
    def __init__(self, guild_id, protection_data, bot):
        super().__init__(timeout=None)
        self.add_item(ProtectionMenu(guild_id, protection_data, bot))

@bot.hybrid_command(name="protection", description="Configurer les protections du serveur")
@is_admin_or_isey()
async def protection(ctx: commands.Context):
    guild_id = str(ctx.guild.id)
    protection_data = collection4.find_one({"guild_id": guild_id}) or {}

    embed = discord.Embed(title="🛡️ Système de Protection", color=discord.Color.blurple())
    for prot in PROTECTIONS:
        if prot == "whitelist":
            whitelist_data = collection19.find_one({"guild_id": guild_id}) or {}
            wl_users = whitelist_data.get("whitelist", [])
            if not wl_users:
                embed.add_field(name=PROTECTION_DETAILS[prot][0], value="Aucun utilisateur whitelisté.", inline=False)
            else:
                members = []
                for uid in wl_users:
                    user = ctx.guild.get_member(int(uid)) or await ctx.bot.fetch_user(int(uid))
                    members.append(f"- {user.mention if isinstance(user, discord.Member) else user.name}")
                embed.add_field(name=PROTECTION_DETAILS[prot][0], value="\n".join(members), inline=False)
        else:
            name, value = format_protection_field(prot, protection_data, ctx.guild, ctx.bot)
            embed.add_field(name=name, value=value, inline=False)

    # ➕ Ajoute le résumé ici aussi :
    embed.add_field(
        name="🔒 Résumé des protections",
        value=generate_global_status_bar(protection_data),
        inline=False
    )
    embed.set_footer(text="🎚️ Sélectionnez une option ci-dessous pour gérer la sécurité du serveur.")
    view = ProtectionView(guild_id, protection_data, ctx.bot)
    await ctx.send(embed=embed, view=view)

@bot.command()
async def addwl(ctx, user: discord.User):
    # Autorise ISEY ou le propriétaire du serveur
    if ctx.author.id != ISEY_ID and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Désolé, vous n'avez pas l'autorisation d'utiliser cette commande.")
        return

    guild_id = str(ctx.guild.id)
    wl_data = collection19.find_one({"guild_id": guild_id})

    if not wl_data:
        collection19.insert_one({"guild_id": guild_id, "whitelist": []})
        wl_data = {"whitelist": []}

    if str(user.id) in wl_data["whitelist"]:
        await ctx.send(f"{user.name} est déjà dans la whitelist.")
    else:
        collection19.update_one(
            {"guild_id": guild_id},
            {"$push": {"whitelist": str(user.id)}}
        )
        await ctx.send(f"{user.name} a été ajouté à la whitelist.")


# Fonction pour retirer un utilisateur de la whitelist
@bot.command()
async def removewl(ctx, user: discord.User):
    if ctx.author.id != ISEY_ID:  # Vérifie si l'utilisateur est bien l'administrateur
        await ctx.send("Désolé, vous n'avez pas l'autorisation d'utiliser cette commande.")
        return

    guild_id = str(ctx.guild.id)
    wl_data = collection19.find_one({"guild_id": guild_id})

    if not wl_data or str(user.id) not in wl_data["whitelist"]:
        await ctx.send(f"{user.name} n'est pas dans la whitelist.")
    else:
        # Retirer l'utilisateur de la whitelist
        collection19.update_one(
            {"guild_id": guild_id},
            {"$pull": {"whitelist": str(user.id)}}
        )
        await ctx.send(f"{user.name} a été retiré de la whitelist.")

@bot.command()
async def listwl(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send(embed=discord.Embed(
            title="⛔ Accès refusé",
            description="Vous n'avez pas l'autorisation d'utiliser cette commande.",
            color=discord.Color.red()
        ))

    guild_id = str(ctx.guild.id)
    wl_data = collection19.find_one({"guild_id": guild_id})

    if not wl_data or not wl_data.get("whitelist"):
        embed = discord.Embed(
            title="Whitelist",
            description="La whitelist de ce serveur est vide.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Etherya • Gestion des accès")
        return await ctx.send(embed=embed)

    whitelist_users = [f"<@{user_id}>" for user_id in wl_data["whitelist"]]
    description = "\n".join(whitelist_users)

    embed = discord.Embed(
        title="✅ Utilisateurs Whitelistés",
        description=description,
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Project : Delta • {len(whitelist_users)} utilisateur(s) whitelisté(s)")
    await ctx.send(embed=embed)

@bot.tree.command(name="set-absence", description="Configurer le salon des absences et le rôle autorisé")
@discord.app_commands.describe(channel="Salon de destination", role="Rôle autorisé à envoyer des absences")
async def set_absence(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Vous devez être administrateur pour utiliser cette commande.",
            ephemeral=True
        )
        return

    # On évite l'expiration de l'interaction
    await interaction.response.defer(ephemeral=True)

    # Enregistrement en base de données
    collection22.update_one(
        {"guild_id": str(interaction.guild.id)},
        {"$set": {
            "channel_id": channel.id,
            "role_id": role.id
        }},
        upsert=True
    )

    # Réponse après defer
    await interaction.followup.send(
        f"✅ Salon d'absence défini sur {channel.mention}, rôle autorisé : {role.mention}",
        ephemeral=True
    )

# ===============================
# ┃ MODAL pour /absence
# ===============================
class AbsenceModal(discord.ui.Modal, title="Déclaration d'absence"):

    pseudo = discord.ui.TextInput(label="Pseudo", placeholder="Ton pseudo IG ou Discord", max_length=100)
    date = discord.ui.TextInput(label="Date(s)", placeholder="Ex: du 20 au 25 avril", max_length=100)
    raison = discord.ui.TextInput(label="Raison", style=discord.TextStyle.paragraph, max_length=500)

    def __init__(self, interaction: discord.Interaction, channel: discord.TextChannel):
        super().__init__()
        self.interaction = interaction
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Nouvelle absence déclarée", color=0xffd700)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 Pseudo", value=self.pseudo.value, inline=False)
        embed.add_field(name="📅 Date", value=self.date.value, inline=False)
        embed.add_field(name="📝 Raison", value=self.raison.value, inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        await self.channel.send(embed=embed)
        await interaction.response.send_message("✅ Ton absence a bien été enregistrée !", ephemeral=True)

# ===============================
# ┃ COMMANDE /absence
# ===============================
@bot.tree.command(name="absence", description="Déclarer une absence")
async def absence(interaction: discord.Interaction):
    data = collection22.find_one({"guild_id": str(interaction.guild.id)})

    if not data:
        return await interaction.response.send_message("❌ Le système d'absence n'est pas configuré.", ephemeral=True)

    role_id = data.get("role_id")
    channel_id = data.get("channel_id")
    channel = interaction.guild.get_channel(channel_id)

    if not channel:
        return await interaction.response.send_message("❌ Le salon d'absence n'a pas été trouvé.", ephemeral=True)

    if not role_id or role_id not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("❌ Vous n'avez pas le rôle requis pour déclarer une absence.", ephemeral=True)

    await interaction.response.send_modal(AbsenceModal(interaction, channel))

@bot.tree.command(name="activate-troll", description="Active les commandes troll pour ce serveur")
@app_commands.checks.has_permissions(administrator=True)
async def activate_troll(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild_name = interaction.guild.name

    # Mettre à jour ou insérer l'activation dans MongoDB
    collection27.update_one(
        {"guild_id": guild_id},
        {"$set": {"guild_name": guild_name, "troll_active": True}},
        upsert=True
    )

    await interaction.response.send_message(
        f"✅ Les commandes troll ont été **activées** sur ce serveur !", ephemeral=True
    )

# Gestion des erreurs si l'utilisateur n'a pas les permissions
@activate_troll.error
async def activate_troll_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("🚫 Vous devez être **administrateur** pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

@bot.tree.command(name="desactivate-troll", description="Désactive les commandes troll pour ce serveur")
@app_commands.checks.has_permissions(administrator=True)
async def desactivate_troll(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild_name = interaction.guild.name

    # Mettre à jour ou insérer la désactivation dans MongoDB
    collection27.update_one(
        {"guild_id": guild_id},
        {"$set": {"guild_name": guild_name, "troll_active": False}},
        upsert=True
    )

    await interaction.response.send_message(
        f"⛔ Les commandes troll ont été **désactivées** sur ce serveur !", ephemeral=True
    )

# Gestion des erreurs si l'utilisateur n'a pas les permissions
@desactivate_troll.error
async def desactivate_troll_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("🚫 Vous devez être **administrateur** pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)
# Liste des catégories
SENSIBLE_CATEGORIES = [
    "insultes_graves",
    "discours_haineux",
    "ideologies_haineuses",
    "violences_crimes",
    "drogues_substances",
    "contenus_sexuels",
    "fraudes_financières",
    "attaques_menaces",
    "raids_discord",
    "harcèlement_haine",
    "personnages_problématiques"
]

# Détails des catégories
SENSIBLE_DETAILS = {
    "insultes_graves": ("Insultes graves", "Détecte les insultes graves."),
    "discours_haineux": ("Discours haineux", "Détecte les propos discriminatoires."),
    "ideologies_haineuses": ("Idéologies haineuses", "Détecte les termes liés à des idéologies haineuses."),
    "violences_crimes": ("Violences et crimes", "Détecte les mentions de violences ou crimes graves."),
    "drogues_substances": ("Drogues & substances", "Détecte les mentions de drogues ou substances illicites."),
    "contenus_sexuels": ("Contenus sexuels explicites", "Détecte les contenus à caractère sexuel explicite."),
    "fraudes_financières": ("Fraudes & crimes financiers", "Détecte les mentions de fraudes ou crimes financiers."),
    "attaques_menaces": ("Attaques et menaces", "Détecte les propos menaçants ou attaques."),
    "raids_discord": ("Raids Discord", "Détecte les tentatives de raids sur le serveur."),
    "harcèlement_haine": ("Harcèlement et haine", "Détecte les propos haineux ou de harcèlement."),
    "personnages_problématiques": ("Personnages problématiques", "Détecte les mentions de personnages problématiques.")
}

# Vérification des droits
def is_admin_or_isey():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id == ISEY_ID
    return commands.check(predicate)

def format_sensible_field(cat, data, guild, bot):
    try:
        name, desc = SENSIBLE_DETAILS[cat]
        enabled = data.get(cat, True)
        status = "✅ Activée" if enabled else "❌ Désactivée"
        updated_by_id = data.get(f"{cat}_updated_by")
        updated_at = data.get(f"{cat}_updated_at")

        modifier = None
        if updated_by_id:
            modifier = guild.get_member(int(updated_by_id)) or updated_by_id

        formatted_date = ""
        if updated_at:
            dt = updated_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Paris"))
            formatted_date = f"🕒 {dt.strftime('%d/%m/%Y à %H:%M')}"

        mod_info = f"\n👤 Modifié par : {modifier.mention if isinstance(modifier, discord.Member) else modifier}" if modifier else ""
        date_info = f"\n{formatted_date}" if formatted_date else ""

        value = f"> {desc}\n> **Statut :** {status}{mod_info}{date_info}"
        return name, value
    except Exception as e:
        print(f"[ERREUR] format_sensible_field({cat}) : {e}")
        return "Erreur", f"Impossible de charger la catégorie {cat}."

class SensibleMenu(Select):
    def __init__(self, guild_id, sensible_data, bot):
        self.guild_id = guild_id
        self.sensible_data = sensible_data
        self.bot = bot

        options = [
            SelectOption(
                label=SENSIBLE_DETAILS[cat][0],
                description="Activer ou désactiver cette catégorie.",
                emoji="🟢" if sensible_data.get(cat, True) else "🔴",
                value=cat
            ) for cat in SENSIBLE_CATEGORIES
        ]

        super().__init__(
            placeholder="🔧 Choisissez une catégorie à modifier",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        cat = self.values[0]
        current = self.sensible_data.get(cat, True)
        new_value = not current
        print(f"[LOG] {interaction.user} modifie {cat} : {current} -> {new_value}")

        try:
            collection28.update_one(
                {"guild_id": str(self.guild_id)},
                {"$set": {
                    cat: new_value,
                    f"{cat}_updated_by": str(interaction.user.id),
                    f"{cat}_updated_at": datetime.utcnow()
                }},
                upsert=True
            )
        except Exception as e:
            print(f"[ERREUR] Mongo update {cat} : {e}")
            await interaction.response.send_message("Erreur BDD", ephemeral=True)
            return

        self.sensible_data[cat] = new_value
        self.sensible_data[f"{cat}_updated_by"] = interaction.user.id
        self.sensible_data[f"{cat}_updated_at"] = datetime.utcnow()

        try:
            embed = Embed(title="🧠 Configuration des mots sensibles", color=discord.Color.blurple())
            for c in SENSIBLE_CATEGORIES:
                name, value = format_sensible_field(c, self.sensible_data, interaction.guild, self.bot)
                embed.add_field(name=name, value=value, inline=False)

            embed.set_footer(text="🌺 Sélectionnez une option ci-dessous pour gérer les mots sensibles.")
            view = View()
            view.add_item(SensibleMenu(self.guild_id, self.sensible_data, self.bot))
            await interaction.response.edit_message(embed=embed, view=view)
            print(f"[LOG] Message modifié suite à {cat}")
        except Exception as e:
            print(f"[ERREUR] Update message {cat} : {e}")

class SensibleView(View):
    def __init__(self, guild_id, sensible_data, bot):
        super().__init__(timeout=None)
        self.add_item(SensibleMenu(guild_id, sensible_data, bot))

@bot.hybrid_command(name="set-sensible", description="Configurer les catégories de mots sensibles")
@is_admin_or_isey()
async def set_sensible(ctx: commands.Context):
    print(f"[LOG] /set-sensible appelé par {ctx.author} ({ctx.author.id}) sur {ctx.guild.name}")

    guild_id = str(ctx.guild.id)
    try:
        sensible_data = collection28.find_one({"guild_id": guild_id}) or {}
        print(f"[LOG] Données chargées : {sensible_data}")
    except Exception as e:
        print(f"[ERREUR] Mongo find : {e}")
        await ctx.send("Erreur lors de la lecture des données sensibles.")
        return

    for cat in SENSIBLE_CATEGORIES:
        if cat not in sensible_data:
            sensible_data[cat] = True

    try:
        embed = Embed(title="🧠 Configuration des mots sensibles", color=discord.Color.blurple())
        for cat in SENSIBLE_CATEGORIES:
            name, value = format_sensible_field(cat, sensible_data, ctx.guild, ctx.bot)
            embed.add_field(name=name, value=value, inline=False)

        view = SensibleView(ctx.guild.id, sensible_data, ctx.bot)
        await ctx.send(embed=embed, view=view)
        print("[LOG] Embed envoyé avec succès.")
    except Exception as e:
        print(f"[ERREUR] Affichage de l'embed : {e}")
        await ctx.send("Erreur lors de l'affichage de la configuration.")

active_alerts = {}

class UrgenceView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="🚨 Claim", style=discord.ButtonStyle.success, custom_id="claim_button")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user_id not in active_alerts or active_alerts[self.user_id]['claimed']:
            await interaction.response.send_message("Cette urgence a déjà été claim.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        active_alerts[self.user_id]['claimed'] = True

        # Récupération de l'embed d'origine et mise à jour
        embed = active_alerts[self.user_id]['message'].embeds[0]
        embed.set_field_at(index=4, name="📌 Statut", value=f"✅ Claimé par {interaction.user.mention}", inline=False)
        embed.color = discord.Color.green()

        await active_alerts[self.user_id]['message'].edit(
            content=f"🚨 Urgence CLAIM par {interaction.user.mention}",
            embed=embed,
            view=None
        )

        # Notifier l'utilisateur à l'origine de l'urgence par DM avec un embed rassurant
        try:
            user = await interaction.client.fetch_user(self.user_id)

            embed_dm = discord.Embed(
                title="✅ Urgence prise en charge",
                description="Un membre de l'équipe de modération s'est occupé de ton signalement.",
                color=discord.Color.green()
            )
            embed_dm.add_field(
                name="👤 Staff en charge",
                value=f"{interaction.user.mention} (`{interaction.user}`)",
                inline=False
            )
            embed_dm.add_field(
                name="📌 Prochaine étape",
                value="Tu seras contacté si des informations supplémentaires sont nécessaires. Reste disponible.",
                inline=False
            )
            embed_dm.set_footer(text="Merci de ta confiance. Le staff fait de son mieux pour t'aider rapidement.")
            embed_dm.timestamp = datetime.utcnow()

            await user.send(embed=embed_dm)

        except discord.Forbidden:
            pass  # L'utilisateur n'accepte pas les DMs

        await interaction.followup.send(
            f"✅ {interaction.user.mention} a claim l'urgence. L'utilisateur a été notifié en privé.",
            ephemeral=False
        )
        
@bot.tree.command(name="urgence", description="Signaler une urgence au staff.")
@discord.app_commands.describe(raison="Explique la raison de l'urgence")
@discord.app_commands.checks.cooldown(1, 86400, key=lambda i: i.user.id)  # 24h cooldown
async def urgence(interaction: discord.Interaction, raison: str):
    # Vérification de blacklist
    if await is_blacklisted(interaction.user.id):
        await interaction.response.send_message("❌ Tu es blacklist du bot. Tu ne peux pas utiliser cette commande.", ephemeral=True)
        return

    if interaction.user.id in active_alerts and not active_alerts[interaction.user.id]["claimed"]:
        await interaction.response.send_message("Tu as déjà une urgence en cours.", ephemeral=True)
        return

    target_guild = bot.get_guild(GUILD_ID)
    if target_guild is None:
        await interaction.response.send_message("❌ Erreur : le serveur cible est introuvable.", ephemeral=True)
        return

    channel = target_guild.get_channel(CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ Erreur : le salon d'urgence est introuvable dans le serveur cible.", ephemeral=True)
        return

    timestamp = datetime.utcnow()

    # Générer un lien d'invitation vers le serveur source
    invite_link = "Aucun lien disponible"
    if interaction.guild and interaction.channel.permissions_for(interaction.guild.me).create_instant_invite:
        try:
            invite = await interaction.channel.create_invite(
                max_age=3600,
                max_uses=1,
                unique=True,
                reason="Urgence signalée"
            )
            invite_link = invite.url
        except discord.Forbidden:
            invite_link = "Permissions insuffisantes pour générer une invitation"
        except Exception as e:
            invite_link = f"Erreur lors de la création du lien : {e}"

    embed = discord.Embed(
        title="🚨 Nouvelle urgence",
        description=raison,
        color=discord.Color.red(),
        timestamp=timestamp
    )
    embed.set_footer(text=f"ID de l'utilisateur : {interaction.user.id}")
    embed.add_field(name="👤 Utilisateur", value=f"{interaction.user.mention} (`{interaction.user}`)", inline=True)
    embed.add_field(name="🆔 User ID", value=str(interaction.user.id), inline=True)
    embed.add_field(name="🌐 Serveur", value=interaction.guild.name if interaction.guild else "DM", inline=True)
    embed.add_field(name="📅 Date", value=f"<t:{int(timestamp.timestamp())}:F>", inline=True)
    embed.add_field(name="📌 Statut", value="⏳ En attente de claim", inline=False)
    if interaction.guild:
        embed.add_field(name="🔗 Message original", value=f"[Clique ici](https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.id})", inline=False)
    embed.add_field(name="🔗 Invitation", value=invite_link, inline=False)

    view = UrgenceView(interaction.user.id)
    message = await channel.send(
        content=f"<@&{STAFF_DELTA}> 🚨 Urgence signalée**",
        embed=embed,
        view=view
    )

    active_alerts[interaction.user.id] = {
        "message": message,
        "timestamp": timestamp,
        "claimed": False,
        "user_id": interaction.user.id,
        "username": str(interaction.user),
        "guild_name": interaction.guild.name if interaction.guild else "DM",
        "guild_id": interaction.guild.id if interaction.guild else None,
        "channel_id": channel.id,
        "reason": raison
    }

    await interaction.response.send_message("🚨 Urgence envoyée au staff du serveur principal.", ephemeral=True)

class MPVerificationModal(discord.ui.Modal, title="Code de vérification"):
    code = discord.ui.TextInput(label="Entre le code de vérification", style=discord.TextStyle.short)

    def __init__(self, target_id: int, message: str, original_interaction: discord.Interaction):
        super().__init__()
        self.target_id = target_id
        self.message = message
        self.original_interaction = original_interaction

    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != VERIFICATION_CODE:
            await interaction.response.send_message("❌ Code de vérification incorrect.", ephemeral=True)
            return

        try:
            user = await bot.fetch_user(self.target_id)
            await user.send(self.message)
            await interaction.response.send_message(f"✅ Message envoyé à {user.mention}.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ Utilisateur introuvable.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Impossible d’envoyer un message à cet utilisateur.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur est survenue : `{e}`", ephemeral=True)

@bot.tree.command(name="mp", description="Envoie un MP à quelqu'un (réservé à Isey).")
@app_commands.describe(utilisateur="Mention ou ID de la personne", message="Message à envoyer")
async def mp(interaction: discord.Interaction, utilisateur: str, message: str):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
        return
    try:
        # Si mention : <@123456789012345678>
        if utilisateur.startswith("<@") and utilisateur.endswith(">"):
            utilisateur = utilisateur.replace("<@", "").replace("!", "").replace(">", "")
        target_id = int(utilisateur)
    except ValueError:
        await interaction.response.send_message("❌ ID ou mention invalide.", ephemeral=True)
        return

    await interaction.response.send_modal(MPVerificationModal(target_id, message, interaction))

giveaways = {}  # giveaway_id -> data
ended_giveaways = {}  # giveaway_id -> data

class GiveawayModal(discord.ui.Modal, title="Créer un Giveaway"):
    duration = discord.ui.TextInput(label="Durée (ex: 10m, 2h, 1d)", required=True)
    winners = discord.ui.TextInput(label="Nombre de gagnants", required=True)
    prize = discord.ui.TextInput(label="Prix", required=True)
    description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, interactor):
        super().__init__()
        self.interactor = interactor

    def parse_duration(self, s: str) -> int:
        unit = s[-1]
        val = int(s[:-1])
        if unit == "s": return val
        elif unit == "m": return val * 60
        elif unit == "h": return val * 3600
        elif unit == "d": return val * 86400
        else: raise ValueError("Unité invalide (utilise s, m, h ou d)")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            seconds = self.parse_duration(str(self.duration))
        except:
            return await interaction.response.send_message("Durée invalide. Utilise 10m, 2h, 1d...", ephemeral=True)

        end_time = discord.utils.utcnow() + timedelta(seconds=seconds)
        giveaway_id = ''.join(str(random.randint(0, 9)) for _ in range(10))

        giveaways[giveaway_id] = {
            "participants": set(),
            "prize": str(self.prize),
            "host": self.interactor.user.id,
            "winners": int(str(self.winners)),
            "end": end_time,
            "message_id": None
        }

        # Ajout de la description personnalisée si fournie
        extra_description = ""
        if self.description.value and self.description.value.strip():
            giveaways[giveaway_id]["description"] = self.description.value.strip()
            extra_description = f"> {self.description.value.strip()}\n\n"

        embed = discord.Embed(
            title=str(self.prize),
            description=(
                f"{extra_description}"
                f"**Ends:** <t:{int(end_time.timestamp())}:R> (<t:{int(end_time.timestamp())}:F>)\n"
                f"**Hosted by:** {self.interactor.user.mention}\n"
                f"**Entries:** 0\n"
                f"**Winners:** {str(self.winners)}"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"ID: {giveaway_id} — Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        view = JoinGiveawayView(giveaway_id)
        await interaction.response.send_message("Giveaway créé avec succès !", ephemeral=True)
        message = await interaction.channel.send(embed=embed, view=view)
        giveaways[giveaway_id]["message_id"] = message.id

        async def end_giveaway():
            await asyncio.sleep(seconds)
            data = giveaways.get(giveaway_id)
            if not data:
                return

            channel = interaction.channel
            try:
                msg = await channel.fetch_message(data["message_id"])
            except:
                return

            if not data["participants"]:
                await channel.send(f"🎉 Giveaway **{data['prize']}** annulé : aucun participant.")
                await msg.edit(view=None)
                del giveaways[giveaway_id]
                return

            winners = random.sample(list(data["participants"]), min(data["winners"], len(data["participants"])))
            winner_mentions = ', '.join(f"<@{uid}>" for uid in winners)
            await channel.send(f"🎉 Giveaway terminé pour **{data['prize']}** ! Gagnant(s) : {winner_mentions}")

            ended_embed = discord.Embed(
                title=data["prize"],
                description=(
                    f"**Ended:** <t:{int(data['end'].timestamp())}:F>\n"
                    f"**Hosted by:** <@{data['host']}>\n"
                    f"**Entries:** {len(data['participants'])}\n"
                    f"**Winners:** {winner_mentions}"
                ),
                color=discord.Color.blue()
            )
            ended_embed.set_footer(text=f"ID: {giveaway_id} — Terminé")

            await msg.edit(embed=ended_embed, view=None)
            ended_giveaways[giveaway_id] = data
            del giveaways[giveaway_id]

        asyncio.create_task(end_giveaway())

class JoinGiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = giveaways.get(self.giveaway_id)
        if not data:
            return await interaction.response.send_message("Giveaway introuvable.", ephemeral=True)

        if discord.utils.utcnow() > data["end"]:
            return await interaction.response.send_message("⏰ Ce giveaway est terminé !", ephemeral=True)

        if interaction.user.id in data["participants"]:
            return await interaction.response.send_message(
                "You have already entered this giveaway!", ephemeral=True,
                view=LeaveGiveawayView(self.giveaway_id)
            )

        data["participants"].add(interaction.user.id)
        await self.update_embed(interaction.channel, data)
        await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)

    async def update_embed(self, channel, data):
        try:
            msg = await channel.fetch_message(data["message_id"])
            embed = msg.embeds[0]
            lines = embed.description.split('\n')
            for i in range(len(lines)):
                if lines[i].startswith("**Entries:**"):
                    lines[i] = f"**Entries:** {len(data['participants'])}"
            embed.description = '\n'.join(lines)
            await msg.edit(embed=embed)
        except:
            pass

class LeaveGiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=30)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = giveaways.get(self.giveaway_id)
        if data and interaction.user.id in data["participants"]:
            data["participants"].remove(interaction.user.id)
            await interaction.response.send_message("❌ Tu as quitté le giveaway.", ephemeral=True)
        else:
            await interaction.response.send_message("Tu n’étais pas inscrit !", ephemeral=True)

@bot.tree.command(name="g-create", description="Créer un giveaway")
async def g(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)
    await interaction.response.send_modal(GiveawayModal(interaction))

@bot.tree.command(name="g-end", description="Terminer un giveaway prématurément")
@app_commands.describe(giveaway_id="L'ID du giveaway à terminer")
async def g_end(interaction: discord.Interaction, giveaway_id: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)

    data = giveaways.get(giveaway_id)
    if not data:
        return await interaction.response.send_message("Giveaway introuvable ou déjà terminé.", ephemeral=True)

    channel = interaction.channel
    try:
        msg = await channel.fetch_message(data["message_id"])
    except:
        return await interaction.response.send_message("Impossible de retrouver le message du giveaway.", ephemeral=True)

    if not data["participants"]:
        await channel.send(f"🎉 Giveaway **{data['prize']}** annulé : aucun participant.")
        await msg.edit(view=None)
        del giveaways[giveaway_id]
        return await interaction.response.send_message("Giveaway terminé manuellement (aucun participant).", ephemeral=True)

    winners = random.sample(list(data["participants"]), min(data["winners"], len(data["participants"])))
    winner_mentions = ', '.join(f"<@{uid}>" for uid in winners)
    await channel.send(f"🎉 Giveaway terminé pour **{data['prize']}** ! Gagnant(s) : {winner_mentions}")

    ended_embed = discord.Embed(
        title=data["prize"],
        description=(
            f"**Ended (manuellement):** <t:{int(discord.utils.utcnow().timestamp())}:F>\n"
            f"**Hosted by:** <@{data['host']}>\n"
            f"**Entries:** {len(data['participants'])}\n"
            f"**Winners:** {winner_mentions}"
        ),
        color=discord.Color.blue()
    )
    ended_embed.set_footer(text=f"ID: {giveaway_id} — Terminé manuellement")

    await msg.edit(embed=ended_embed, view=None)

    ended_giveaways[giveaway_id] = data
    del giveaways[giveaway_id]

    await interaction.response.send_message("✅ Giveaway terminé manuellement.", ephemeral=True)

@bot.tree.command(name="g-reroll", description="Relancer un giveaway terminé")
@app_commands.describe(giveaway_id="L'ID du giveaway à reroll")
async def g_reroll(interaction: discord.Interaction, giveaway_id: str):
    data = ended_giveaways.get(giveaway_id)
    if not data:
        return await interaction.response.send_message("Giveaway non trouvé ou pas encore terminé.", ephemeral=True)

    if not data["participants"]:
        return await interaction.response.send_message("Aucun participant à ce giveaway.", ephemeral=True)

    winners = random.sample(list(data["participants"]), min(data["winners"], len(data["participants"])))
    winner_mentions = ', '.join(f"<@{uid}>" for uid in winners)
    await interaction.response.send_message(
        f"🎉 Nouveau tirage pour **{data['prize']}** ! Gagnant(s) : {winner_mentions}"
    )

fast_giveaways = {}

@bot.tree.command(name="g-fast", description="Créer un giveaway rapide (g-fast)")
async def g_fast(interaction: discord.Interaction, duration: str, prize: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)

    def parse_duration(s):
        unit = s[-1]
        val = int(s[:-1])
        if unit == "s": return val
        elif unit == "m": return val * 60
        elif unit == "h": return val * 3600
        elif unit == "d": return val * 86400
        else: raise ValueError("Unité invalide")

    try:
        seconds = parse_duration(duration)
    except:
        return await interaction.response.send_message("Durée invalide. Utilise 10m, 2h, 1d...", ephemeral=True)

    end_time = discord.utils.utcnow() + timedelta(seconds=seconds)
    giveaway_id = ''.join(str(random.randint(0, 9)) for _ in range(10))

    data = {
        "participants": set(),
        "prize": prize,
        "host": interaction.user.id,
        "end": end_time,
        "message_id": None,
        "channel_id": interaction.channel.id
    }
    fast_giveaways[giveaway_id] = data

    embed = discord.Embed(
        title=f"🎉 Giveaway Fast - {prize}",
        description=(
            f"**Ends:** <t:{int(end_time.timestamp())}:R>\n"
            f"**Hosted by:** {interaction.user.mention}\n"
            f"**Entries:** 0\n"
            f"**1 Winner**"
        ),
        color=discord.Color.green()
    )

    view = FastGiveawayView(giveaway_id)
    msg = await interaction.channel.send(embed=embed, view=view)
    data["message_id"] = msg.id
    await interaction.response.send_message("Giveaway rapide lancé !", ephemeral=True)

    async def end_fast():
        await asyncio.sleep(seconds)
        data = fast_giveaways.get(giveaway_id)
        if not data or not data["participants"]:
            await interaction.channel.send(f"🎉 Giveaway **{data['prize']}** annulé : aucun participant.")
            return

        winner_id = random.choice(list(data["participants"]))
        winner = await bot.fetch_user(winner_id)

        try:
            dm = await winner.create_dm()
            dm_msg = await dm.send(
                f"🎉 Tu as gagné **{data['prize']}** ! Réagis à ce message avec <a:fete:1375944789035319470> pour valider ta victoire."
            )
            await dm_msg.add_reaction("<a:fete:1375944789035319470>")
        except Exception:
            return await interaction.channel.send(f"❌ Impossible d'envoyer un MP à <@{winner_id}>.")

        start_time = discord.utils.utcnow()

        def check(reaction, user):
            return (
                user.id == winner_id and
                reaction.message.id == dm_msg.id and
                str(reaction.emoji) == "<a:fete:1375944789035319470>"
            )

        try:
            await bot.wait_for('reaction_add', timeout=60, check=check)
            delay = (discord.utils.utcnow() - start_time).total_seconds()
            await interaction.channel.send(
                f"⏱️ <@{winner_id}> a réagi en **{round(delay, 2)} secondes** pour valider sa victoire sur **{data['prize']}** !"
            )
        except asyncio.TimeoutError:
            await interaction.channel.send(
                f"❌ <@{winner_id}> n’a pas réagi dans les 60 secondes en MP. Giveaway perdu."
            )

        del fast_giveaways[giveaway_id]

    asyncio.create_task(end_fast())

class FastGiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="🎉 Participer", style=discord.ButtonStyle.green)
    async def join_fast(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = fast_giveaways.get(self.giveaway_id)
        if not data:
            return await interaction.response.send_message("Giveaway introuvable.", ephemeral=True)
        if discord.utils.utcnow() > data["end"]:
            return await interaction.response.send_message("⏰ Ce giveaway est terminé !", ephemeral=True)
        if interaction.user.id in data["participants"]:
            return await interaction.response.send_message("Tu es déjà inscrit !", ephemeral=True)

        data["participants"].add(interaction.user.id)
        await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)

# Modal de vérification
class EnregistrerServeurModal(ui.Modal, title="🔐 Vérification requise"):

    code = ui.TextInput(label="Code de vérification", placeholder="Entre le code fourni", required=True)

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != VERIFICATION_CODE:
            await interaction.response.send_message("❌ Code incorrect. Action annulée.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        enregistrés = 0
        déjà = 0
        erreurs = 0

        for guild in interaction.client.guilds:
            existing = collection31.find_one({"guild_id": guild.id})
            if existing:
                déjà += 1
                continue

            try:
                await asyncio.sleep(1)  # éviter les rate limits

                # Remplacement de fetch_owner() par fetch_user(owner_id)
                owner = await interaction.client.fetch_user(guild.owner_id)
                owner_id = owner.id

                data = {
                    "guild_id": guild.id,
                    "guild_name": guild.name,
                    "member_count": guild.member_count,
                    "owner_id": owner_id,
                    "timestamp": datetime.utcnow()
                }
                collection31.insert_one(data)
                enregistrés += 1

            except Exception as e:
                erreurs += 1
                print(f"Erreur fetch owner pour {guild.name} ({guild.id}) : {e}")
                traceback.print_exc()
                continue

        await interaction.followup.send(
            f"✅ {enregistrés} serveur(s) enregistré(s).\n"
            f"🗂️ {déjà} déjà présent(s).\n"
            f"⚠️ {erreurs} erreur(s) lors du fetch des owners.",
            ephemeral=True
        )

# Commande slash
@bot.tree.command(name="enregistrer-serveur", description="Enregistre les infos des serveurs (réservé à Isey).")
async def enregistrer_serveur(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Seul Isey peut utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.send_modal(EnregistrerServeurModal(interaction))


class ResetServeurModal(ui.Modal, title="⚠️ Réinitialisation requise"):
    code = ui.TextInput(label="Code de vérification", placeholder="Entre le code fourni", required=True)

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != VERIFICATION_CODE:
            await interaction.response.send_message("❌ Code incorrect. Réinitialisation annulée.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            result = collection31.delete_many({})
            await interaction.followup.send(
                f"✅ Réinitialisation terminée.\n🗑️ {result.deleted_count} document(s) supprimé(s) de la collection.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la suppression : {e}", ephemeral=True)

# Commande slash
@bot.tree.command(name="reset-serveur", description="Réinitialise complètement la collection (réservé à Isey).")
async def reset_serveur(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Seul Isey peut utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.send_modal(ResetServeurModal(interaction))

@bot.command(name="presentation")
async def presentation(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("🚫 Cette commande est réservée à ISEY uniquement.")

    embed = discord.Embed(
        title="**Bienvenue sur le support officiel de Project : Delta !**",
        description=(
            "> <:dev_white:1376909968141451274>  **Un bot complet pour gérer, protéger et animer votre serveur Discord.**\n"
            "> <a:fete:1375944789035319470>  Simple, puissant, gratuit (Premium offert pendant la phase de test) !\n\n"

            "## <:bot:1377223809832058971>・**Project : Delta – Le Bot**\n\n"
            "<:shield:1377224699955773523>  Anti-raid puissant – Ne laissez aucune attaque passer.\n"
            "<:Vocal:1361766779143061767>  Détection automatique de mots sensibles – Modération intelligente.\n"
            "<:tools:1377227900037632060>  Outils de gestion simples et efficaces – Kick, ban, clear, logs, et plus.\n"
            "<:member:1377228477131919370>  Giveaways & commandes fun – Pour animer votre communauté avec style.\n\n"

            "<:files:1377229165572395079>  **Fonctionnalités à venir :**\n"
            "<:uoad:1377229381784698932>  *Sauvegarde de serveur.*\n"
            "<:ticket:1377229577880997918> *Tickets.*\n"
            "<:delertle:1377229695086628884> *Logs.*\n"
            "<a:recaptcha:1377230186545942609> *Captcha*\n\n"

            "<a:fete:1377230403114635415> **Offre actuelle** : Tous les serveurs qui ajoutent le bot ont un **statut Premium GRATUIT** pendant la phase de test !\n\n"
            "<:emoji_36:1361992348363653180>  [Ajouter Project : Delta](https://discord.com/oauth2/authorize?client_id=1356693934012891176&permissions=8&integration_type=0&scope=bot)\n\n"

            "## <:support:1377230564070789201> ・**Serveur Support**\n\n"
            "Besoin d’aide ? Une question ? Une suggestion ?\n"
            "Tu es au bon endroit !\n\n"
            "<:Staff:1377230643678675015> *Staff actif et à l’écoute*\n"
            "<:spare_bulb:1362002224599011429> *Salons dédiés aux bugs et idées*\n"
            "<:pinkgift:1377230919970062366> *Bonus pour les membres actifs et soutiens de Project : Delta*\n"
            "<a:fleche3:1290077283100397672> *Événements réguliers & Giveaways à gogo !*\n\n"
            "<:link:1377231454219534376> [Rejoindre notre support (t’es déjà là)](https://discord.gg/c5VkwStrTr)\n\n"

            "## <:Calendar:1377251449456558080> ・**Lancement Officiel : Vendredi 30 Mai à 18h00**\n\n"
            "<a:fete:1375944789035319470>  Grand événement **“L’Éveil de Project : Delta”** avec **+10 giveaways** et des **services exclusifs à gagner** !\n\n"
            "<a:Gift_Animation:1342041962542272594> **Giveaways Classiques** (5 à 7) :\n"
            "<a:trophee:1289678773700268183> *Jusqu’à des services **à vie** (bots, sites web, serveurs Discord)*\n"
            "<a:star:1377232131516010646> *Objectifs communautaires simples : membres, invites, ajout du bot...*\n\n"
            "<a:cadeau:1377232340702597212>  **Giveaways Fast** (5 à 7) :\n"
            "<a:check:1377232820715524156> *Des récompenses instantanées, sans conditions !*\n\n"
            "<a:notif:1172810989088026675> *Plus tu participes, plus tu gagnes.*\n"
            "<:hey:1376197207832924290> Active-toi et cumule des **points** pour échanger contre **services gratuits** (voir salon dédié).\n\n"

            "## <a:heart:1376670580283146371> ・**Rejoins l’aventure dès maintenant !**\n\n"
            "🔗 [Ajouter le bot à ton serveur](https://discord.com/oauth2/authorize?client_id=1356693934012891176&permissions=8&integration_type=0&scope=bot)\n\n"
            "Merci d’être là avec nous <a:Heart:1353412261888135228>\n"
            "**– L’équipe Project : Delta**"
        ),
        color=discord.Color.purple()
    )

    embed.set_image(url="https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20Delta/uriifs3A2F2FM2F91f68b3b-528b-47fb-a810-fa202d513477.png?raw=true")
    embed.set_footer(
        text="Project : Delta – L’avenir de ton serveur commence ici",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=embed)

@bot.command(name="regle-event")
async def regle_event(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("🚫 Cette commande est réservée à ISEY uniquement.")

    embed = discord.Embed(
        title="Règlement de l’Événement — L’Éveil de Project : Delta",
        description=(
            "Merci de participer à notre événement ! Pour garantir une compétition saine et équitable, nous vous demandons de respecter les règles suivantes :\n\n"

            "**1. Interdiction stricte des doubles comptes**\n"
            "Créer ou utiliser plusieurs comptes pour augmenter ses chances ou ses points est **formellement interdit**.\n"
            "**Sanction : disqualification immédiate.**\n\n"

            "**2. Pas de fraude dans le système de points**\n"
            "Tenter de tricher ou de contourner les règles entraînera une exclusion de l’événement. Exemples interdits :\n"
            "- Ajouter, retirer et ré-ajouter le bot pour farm les points.\n"
            "- Inviter un ami pour qu’il quitte et revienne juste après.\n"
            "- Exploiter des scripts ou bots externes.\n\n"
            "Nous avons un système de logs complet. Si vous trichez, **vous serez simplement sanctionnés – inutile de tenter le diable**.\n\n"

            "**3. Exploitation de bugs ou failles**\n"
            "Si vous découvrez un bug ou une faille dans le système de points ou les commandes du bot :\n"
            "→ **Ne l’utilisez pas.**\n"
            "→ **Signalez-la au staff immédiatement.**\n\n"
            "**Une récompense vous sera attribuée** pour toute faille signalée **avant** d’être utilisée à mauvais escient.\n\n"

            "**4. Respect du staff et des autres participants**\n"
            "Le fair-play est essentiel. Les provocations, insultes ou comportements toxiques sont **interdits**.\n\n"
            "Toute tentative de nuire à l'événement, directement ou indirectement, peut entraîner une **exclusion temporaire ou définitive**.\n\n"

            "**Rappel :** Le but est de s’amuser, d’être actif, de découvrir le bot, et de repartir potentiellement avec des cadeaux ou des services !\n\n"
            "En participant à l’événement, vous acceptez ce règlement dans son intégralité."
        ),
        color=discord.Color.gold()
    )

    embed.set_image(url="https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20Delta/uriifs3A2F2FM2F91f68b3b-528b-47fb-a810-fa202d513477.png?raw=true")
    embed.set_footer(
        text="Project : Delta – L’avenir de ton serveur commence ici",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=embed)

# === CLASSES DES BOUTONS ET VUES ===

class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PointSystemButton())
        self.add_item(PriceServiceButton())

class PointSystemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Système de Gain de points",
            style=discord.ButtonStyle.primary,
            custom_id="pointsystem_btn"
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x1ABC9C)
        embed.set_image(url="https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/1.jpg?raw=true")

        view = discord.ui.View(timeout=None)
        view.add_item(ImageButton("Project : Delta", "https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/2.jpg?raw=true", "project_image_btn"))
        view.add_item(ImageButton("Annonce", "https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/3.jpg?raw=true", "annonce_image_btn"))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PriceServiceButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Prix des Services",
            style=discord.ButtonStyle.secondary,
            custom_id="price_service_btn"
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💰 Prix des Services",
            description="Les prix varient selon le service demandé et sa complexité.",
            color=0x3498DB
        )

        view = discord.ui.View(timeout=None)
        view.add_item(ImageButton("Bot Discord", "https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/4.jpg?raw=true", "img_botdiscord"))
        view.add_item(ImageButton("Site Web", "https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/5.jpg?raw=true", "img_siteweb"))
        view.add_item(ImageButton("Serveur Discord", "https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/6.jpg?raw=true", "img_servdiscord"))
        view.add_item(ImageButton("Prestations Annexes", "https://github.com/Iseyg91/PD-IC/blob/main/IMAGES%20EVENT/7.jpg?raw=true", "img_annexe"))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ImageButton(discord.ui.Button):
    def __init__(self, label, image_url, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.success, custom_id=custom_id)
        self.image_url = image_url

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x2C3E50)
        embed.set_image(url=self.image_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# === COMMANDE POUR ENVOYER L'ÉVENT ===

@bot.command()
async def info(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

    embed = discord.Embed(
        title="**ÉVÉNEMENT SPÉCIAL — LANCEMENT OFFICIEL DE PROJECT : DELTA**",
        description=(
            "C’est officiel : **Project : Delta** est lancé ! <a:happyanime:1172809287089786940>\n"
            "Pour marquer le coup, on vous a préparé un **événement unique** sur le serveur… et vous allez pouvoir **gagner plein de choses** ! <a:cadeau:1377232340702597212>\n\n"
            "<a:fete:1377230403114635415>  **POURQUOI CET ÉVÉNEMENT ?**\n"
            "Parce qu’on voulait faire plus que juste un lancement : on voulait **vous impliquer**, **vous remercier** et **vous faire kiffer** dès le début.\n"
            "C’est l’occasion parfaite pour :\n\n"
            "<a:fleche3:1376557416216268921>  Gagner des **récompenses** (roles exclusifs, services gratuits, pubs, boosts, etc.)\n"
            "<a:fleche3:1376557416216268921> Obtenir des **points** à échanger contre des avantages\n"
            "<a:fleche3:1376557416216268921> Découvrir les services proposés par Delta... **sans rien payer** pendant l’event !\n\n"
            "<:time:1377361886428921866> **DURÉE DE L'ÉVÉNEMENT : FLEXIBLE**\n"
            "Cet événement n’a **pas de fin fixée à l’avance**. Sa durée dépendra entièrement de **vous** <:Symbol_Down_Arrow2:1367233328398205110>\n\n"
            "<a:fleche3:1376557416216268921>  *Si ça flop* → l’event sera écourté.\n"
            "<a:fleche3:1376557416216268921> *Si c’est stable* → l’event continuera quelques jours.\n"
            "<a:fleche3:1376557416216268921> *Si c’est un énorme succès* → on prolonge, ajoute des bonus, et peut-être des **récompenses surprises** <:sourire:1377362110165815296>\n\n"
            "<:bravo:1377362203757383802>  En bref : **plus vous participez, plus ça dure, plus c’est cool.** À vous de jouer !"
        ),
        color=0x9B59B6
    )

    await ctx.send(embed=embed, view=InfoView())

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
