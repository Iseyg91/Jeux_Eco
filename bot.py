import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput
from discord.utils import get
from discord import TextStyle
from functools import wraps
import os
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
from datetime import datetime, timedelta  # Tu as déjà la bonne importation pour datetime et timedelta
from collections import defaultdict, deque
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import psutil
import pytz
import platform
from discord import Interaction
import logging
from typing import Optional

token = os.environ['ETHERYA']
intents = discord.Intents.all()
start_time = time.time()
bot = commands.Bot(command_prefix="!!", intents=intents, help_command=None)

#Configuration du Bot:
# --- ID Owner Bot ---
ISEY_ID = 792755123587645461
# Définir GUILD_ID
GUILD_ID = 1034007767050104892

# --- ID Etherya Partenariats ---
partnership_channel_id = 1355158081855688745
ROLE_ID = 1355157749994098860

# --- ID Etherya ---
BOUNTY_CHANNEL_ID = 1355298449829920950
ETHERYA_SERVER_ID = 1034007767050104892
AUTORIZED_SERVER_ID = 1034007767050104892
WELCOME_CHANNEL_ID = 1355198748296351854

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

# Collections
collection = db['ether_eco']  #Stock les Bal
collection2 = db['ether_daily']  #Stock les cd de daily
collection3 = db['ether_slut']  #Stock les cd de slut
collection4 = db['ether_crime']  #Stock les cd de slut
collection5 = db['ether_collect'] #Stock les cd de collect
collection6 = db['ether_work'] #Stock les cd de Work
collection7 = db['ether_inventory'] #Stock les inventaires
collection8 = db['info_cf'] #Stock les Info du cf
collection9 = db['info_logs'] #Stock le Salon logs
collection10 = db['info_bj'] #Stock les Info du Bj
collection11 = db['info_rr'] #Stock les Info de RR
collection12 = db['info_roulette'] #Stock les Info de SM
collection13 = db['info_sm'] #Stock les Info de SM
collection14 = db['ether_rob'] #Stock les cd de Rob
collection15 = db['anti_rob'] #Stock les rôle anti-rob
collection21 = db['daily_badge'] #Stock les cd des daily badge

# Fonction pour vérifier si l'utilisateur possède un item (fictif, à adapter à ta DB)
async def check_user_has_item(user: discord.Member, item_id: int):
    # Ici tu devras interroger la base de données MongoDB ou autre pour savoir si l'utilisateur possède cet item
    # Par exemple:
    # result = collection.find_one({"user_id": user.id, "item_id": item_id})
    # return result is not None
    return True  # Pour l'exemple, on suppose que l'utilisateur a toujours l'item.

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

async def initialize_bounty_or_honor(user_id, is_pirate, is_marine):
    # Vérifier si le joueur est un pirate et n'a pas encore de prime
    if is_pirate:
        bounty_data = collection37.find_one({"user_id": user_id})
        if not bounty_data:
            # Si le joueur n'a pas de prime, initialiser à 50
            collection37.insert_one({"user_id": user_id, "bounty": 50})

    # Vérifier si le joueur est un marine et n'a pas encore d'honneur
    if is_marine:
        honor_data = collection38.find_one({"user_id": user_id})
        if not honor_data:
            # Si le joueur n'a pas d'honneur, initialiser à 50
            collection38.insert_one({"user_id": user_id, "honor": 50})

async def log_eco_channel(bot, guild_id, user, action, amount, balance_before, balance_after, note=""):
    config = collection9.find_one({"guild_id": guild_id})
    channel_id = config.get("eco_log_channel") if config else None

    if not channel_id:
        return  # Aucun salon configuré

    channel = bot.get_channel(channel_id)
    if not channel:
        return  # Salon introuvable (peut avoir été supprimé)

    embed = discord.Embed(
        title="💸 Log Économique",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
    embed.add_field(name="Action", value=action, inline=True)
    embed.add_field(name="Montant", value=f"{amount} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Solde", value=f"Avant: {balance_before}\nAprès: {balance_after}", inline=False)

    if note:
        embed.add_field(name="Note", value=note, inline=False)

    await channel.send(embed=embed)

def load_guild_settings(guild_id):
    # Charger les données de la collection principale
    ether_eco_data = collection.find_one({"guild_id": guild_id}) or {}
    ether_daily_data = collection2.find_one({"guild_id": guild_id}) or {}
    ether_slut_data = collection3.find_one({"guild_id": guild_id}) or {}
    ether_crime_data = collection4.find_one({"guild_id": guild_id}) or {}
    ether_collect = collection5.find_one({"guild_id": guild_id}) or {}
    ether_work_data = collection6.find_one({"guild_id": guild_id}) or {}
    ether_inventory_data = collection7.find_one({"guild_id": guild_id}) or {}
    info_cf_data = collection8.find_one({"guild_id": guild_id}) or {}
    info_logs_data = collection9.find_one({"guild_id": guild_id}) or {}
    info_bj_data = collection10.find_one({"guild_id": guild_id}) or {}
    info_rr_data = collection11.find_one({"guild_id": guild_id}) or {}
    info_roulette_data = collection12.find_one({"guild_id": guild_id}) or {}
    info_sm_roulette_data = collection13.find_one({"guild_id": guild_id}) or {}
    ether_rob_data = collection14.find_one({"guild_id": guild_id}) or {}
    anti_rob_data = collection15.find_one({"guild_id": guild_id}) or {}
    daily_badge_data = collection21.find_one({"guild_id": guild_id}) or {}
    
    # Débogage : Afficher les données de setup
    print(f"Setup data for guild {guild_id}: {setup_data}")

    combined_data = {
        "ether_eco": ether_eco_data,
        "ether_daily": ether_daily_data,
        "ether_slut": ether_slut_data,
        "ether_crime": ether_crime_data,
        "ether_collect": ether_collect_data,
        "ether_work": ether_work_data,
        "ether_inventory": ether_inventory_data,
        "info_cf": info_cf_data,
        "info_logs": info_logs_data,
        "info_bj": info_bj_data,
        "info_rr": info_rr_data,
        "info_roulette": info_roulette_data,
        "info_sm": info_sm_data,
        "ether_rob": ether_rob_data,
        "anti_rob": anti_rob_data,
        "daily_badge": daily_badge_data
    }

    return combined_data

def get_or_create_user_data(guild_id: int, user_id: int):
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data:
        data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
        collection.insert_one(data)
    return data

def insert_badge_into_db():
    # Insérer les badges définis dans la base de données MongoDB
    for badge in BADGES:
        # Vérifier si le badge est déjà présent
        if not collection19.find_one({"id": badge["id"]}):
            collection19.insert_one(badge)

# === UTILITAIRE POUR RÉCUPÉRER LA DATE DE DÉBUT ===
def get_start_date(guild_id):
    start_date_data = collection22.find_one({"guild_id": guild_id})
    if start_date_data:
        return datetime.fromisoformat(start_date_data["start_date"])
    return None

TOP_ROLES = {
    1: 1363923497885237298,  # ID du rôle Top 1
    2: 1363923494504501510,  # ID du rôle Top 2
    3: 1363923356688056401,  # ID du rôle Top 3
}

# Config des rôles
COLLECT_ROLES_CONFIG = [
    {
        "role_id": 1355157715550470335, #Membres
        "amount": 1000,
        "cooldown": 3600,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365683057591582811, #Roi des Pirates
        "amount": 12500,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365683477868970204, #Amiral en Chef
        "amount": 15000,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365682989996052520, #Yonko
        "amount": 5000,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365683407023243304, #Commandant
        "amount": 7500,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365682918243958826, #Corsaires
        "amount": 3000,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365683324831531049, #Lieutenant
        "amount": 5000,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365682795501977610, #Pirates
        "amount": 1000,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365683175019516054, #Matelot
        "amount": 2000,
        "cooldown": 43200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365698043684327424, #Haki de l'armement Inferieur
        "amount": 5000,
        "cooldown": 7200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1365389381246124084, #Haki de l'Armement Avancé
        "amount": 5000,
        "cooldown": 7200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1363969965572755537, #Nen Maudit
        "percent": -20,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1365313255471579297, #Soumsi a Nika
        "percent": -10,
        "cooldown": 86400,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1365313257279062067, #Gol Gol no Mi
        "percent": 10,
        "cooldown": 604800,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1365313261129568297, #Gear Second
        "percent": 5,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1365312301900501063, #Nika Collect
        "percent": 500,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1365313287964725290, #Soumis Bourrasque Devastatrice
        "percent": -50,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1365312292069048443, #Tonnere Divin
        "percent": -70,
        "cooldown": 86400,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1355903910635770098, #God of Glory
        "amount": 12500,
        "cooldown": 86400,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1034546767104069663, #Booster
        "amount": 5000,
        "cooldown": 7200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1363974710739861676, #Collect Bank
        "percent": 1,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1363948445282341135, #Mode Ermite
        "amount": 5000,
        "cooldown": 7200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157729362313308, #Grade E
        "amount": 1000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157728024072395, #Grade D
        "amount": 2000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157726032035881, #Grade C
        "amount": 3000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157725046243501, #Grade B
        "amount": 4000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157723960049787, #Grade A
        "amount": 5000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157722907279380, #Grade S
        "amount": 6000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157721812435077, #Grade National
        "amount": 7000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157720730439701, #Grade Etheryens
        "amount": 8000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    }
]

# --- Tâche quotidienne à minuit ---
@tasks.loop(hours=24)
async def task_annonce_jour():
    await annoncer_message_du_jour()

# --- Boucle auto-collecte ---
@tasks.loop(seconds=60)
async def auto_collect_loop():
    for guild in bot.guilds:
        for member in guild.members:
            for config in COLLECT_ROLES_CONFIG:
                role = discord.utils.get(guild.roles, id=config["role_id"])
                if role in member.roles and config["auto"]:
                    now = datetime.utcnow()
                    cd_data = collection5.find_one({
                        "guild_id": guild.id,
                        "user_id": member.id,
                        "role_id": role.id
                    })
                    last_collect = cd_data.get("last_collect") if cd_data else None

                    if not last_collect or (now - last_collect).total_seconds() >= config["cooldown"]:
                        eco_data = collection.find_one({
                            "guild_id": guild.id,
                            "user_id": member.id
                        }) or {"guild_id": guild.id, "user_id": member.id, "cash": 1500, "bank": 0}

                        if "cash" not in eco_data:
                            eco_data["cash"] = 0
                        if "bank" not in eco_data:
                            eco_data["bank"] = 0

                        before = eco_data[config["target"]]
                        if "amount" in config:
                            eco_data[config["target"]] += config["amount"]
                        elif "percent" in config:
                            eco_data[config["target"]] += eco_data[config["target"]] * (config["percent"] / 100)

                        collection.update_one(
                            {"guild_id": guild.id, "user_id": member.id},
                            {"$set": {config["target"]: eco_data[config["target"]]}},
                            upsert=True
                        )

                        collection5.update_one(
                            {"guild_id": guild.id, "user_id": member.id, "role_id": role.id},
                            {"$set": {"last_collect": now}},
                            upsert=True
                        )

                        after = eco_data[config["target"]]
                        await log_eco_channel(bot, guild.id, member, f"Auto Collect ({role.name})", config.get("amount", config.get("percent")), before, after, note="Collect automatique")

import asyncio
import discord
from discord.errors import DiscordServerError

TOP_ROLES = {
    1: 1363923497885237298,  # ID du rôle Top 1
    2: 1363923494504501510,  # ID du rôle Top 2
    3: 1363923356688056401,  # ID du rôle Top 3
}

# --- Boucle Top Roles ---
@tasks.loop(seconds=5)
async def update_top_roles():
    for guild in bot.guilds:
        if guild.id != GUILD_ID:  # Vérifier si on est sur le serveur spécifié
            continue

        all_users_data = list(collection.find({"guild_id": guild.id}))
        sorted_users = sorted(all_users_data, key=lambda u: u.get("cash", 0) + u.get("bank", 0), reverse=True)
        top_users = sorted_users[:3]

        for rank, user_data in enumerate(top_users, start=1):
            user_id = user_data["user_id"]
            role_id = TOP_ROLES[rank]
            role = discord.utils.get(guild.roles, id=role_id)
            if not role:
                print(f"Rôle manquant : {role_id} dans {guild.name}")
                continue

            try:
                member = await fetch_member_with_retry(guild, user_id)
                if not member:
                    print(f"Impossible de récupérer le membre {user_id} dans {guild.name}.")
                    continue
            except discord.NotFound:
                print(f"Membre {user_id} non trouvé dans {guild.name}")
                continue

            if role not in member.roles:
                await member.add_roles(role)
                print(f"Ajouté {role.name} à {member.display_name}")

        for rank, role_id in TOP_ROLES.items():
            role = discord.utils.get(guild.roles, id=role_id)
            if not role:
                continue
            for member in role.members:
                if member.id not in [u["user_id"] for u in top_users]:
                    await member.remove_roles(role)
                    print(f"Retiré {role.name} de {member.display_name}")

# Fonction de réessai pour récupérer un membre
async def fetch_member_with_retry(guild, user_id, retries=5, delay=5):
    for attempt in range(retries):
        try:
            member = await guild.fetch_member(user_id)
            return member
        except discord.NotFound:
            # Si le membre n'est pas trouvé, on arrête le réessai
            return None
        except DiscordServerError as e:
            print(f"Erreur lors de la récupération du membre {user_id}: {e}. Tentative de réessai...")
            await asyncio.sleep(delay)  # Attendre avant de réessayer
    print(f"Échec de la récupération du membre {user_id} après {retries} tentatives.")
    return None

# --- Initialisation au démarrage ---
@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté.")
    bot.loop.create_task(start_background_tasks())
    bot.uptime = time.time()
    activity = discord.Activity(
        type=discord.ActivityType.streaming,
        name="Etherya",
        url="https://www.twitch.tv/tonstream"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)

    print(f"🎉 **{bot.user}** est maintenant connecté et affiche son activité de stream avec succès !")
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

# --- Démarrer les tâches en arrière-plan ---
async def start_background_tasks():
    if not task_annonce_jour.is_running():
        task_annonce_jour.start()
    if not auto_collect_loop.is_running():
        auto_collect_loop.start()
    if not update_top_roles.is_running():
        update_top_roles.start()

# --- Gestion globale des erreurs ---
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )
    try:
        await args[0].response.send_message(embed=embed)
    except Exception:
        pass

# Fonction pour enregistrer un message du joueur dans la base de données
async def enregistrer_message_jour(user_id, message):
    date_aujourdhui = datetime.utcnow().strftime('%Y-%m-%d')
    collection.update_one(
        {"user_id": user_id, "date": date_aujourdhui},
        {"$push": {"messages": message}},  # <- On utilise $push pour accumuler les messages
        upsert=True
    )

# Fonction pour envoyer un message à 00h00
async def annoncer_message_du_jour():
    await bot.wait_until_ready()  # On s'assure que le bot est prêt
    while not bot.is_closed():
        now = datetime.utcnow()
        # Calculer combien de secondes jusqu'à minuit
        next_run = (datetime.combine(now + timedelta(days=1), datetime.min.time()) - now).total_seconds()
        await asyncio.sleep(next_run)

        date_aujourdhui = datetime.utcnow().strftime('%Y-%m-%d')
        messages = collection.find({"date": date_aujourdhui})

        channel = bot.get_channel(1365746881048612876)  # ID du salon

        for msg in messages:
            user_id = msg["user_id"]
            user = bot.get_user(user_id)
            if user:
                content = f"Le <@&1355903910635770098> est ||<@{user.id}>||, félicitations à lui."
                message_annonce = await channel.send(content)
                await message_annonce.add_reaction("<:chat:1362467870348410900>")
                await retirer_role(user)

# Fonction pour retirer le rôle à 23h59 (peut être aussi améliorée avec une tâche programmée si besoin)
async def retirer_role(user):
    role = discord.utils.get(user.guild.roles, id=1355903910635770098)  # ID du rôle à retirer
    if role:
        await user.remove_roles(role)
        print(f"Rôle retiré de {user.name} à 23h59.")

# Ton on_message reste pratiquement pareil
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await enregistrer_message_jour(message.author.id, message.content)
    # Gestion des partenariats dans un salon spécifique
    if message.channel.id == partnership_channel_id:
        rank, partnerships = get_user_partner_info(message.author.id)

        await message.channel.send("<@&1355157749994098860>")

        embed = discord.Embed(
            title="Merci du partenariat 🤝",
            description=f"{message.author.mention}\nTu es rank **{rank}**\nTu as effectué **{partnerships}** partenariats.",
            color=discord.Color.green()
        )
        embed.set_footer(
            text="Partenariat réalisé",
            icon_url="https://github.com/Iseyg91/KNSKS-ET/blob/main/Images_GITHUB/Capture_decran_2024-09-28_211041.png?raw=true"
        )
        embed.set_image(
            url="https://github.com/Iseyg91/KNSKS-ET/blob/main/Images_GITHUB/Capture_decran_2025-02-15_231405.png?raw=true"
        )
        await message.channel.send(embed=embed)

    # Générer un montant aléatoire entre 5 et 20 coins pour l'utilisateur
    coins_to_add = random.randint(5, 20)

    # Ajouter les coins au portefeuille de l'utilisateur
    guild_id = message.guild.id
    user_id = message.author.id
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"wallet": coins_to_add}},
        upsert=True
    )

    # Permet à la commande de continuer à fonctionner si d'autres événements sont enregistrés
    await bot.process_commands(message)

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

@bot.hybrid_command(
    name="ping",
    description="Affiche le Ping du bot."
)
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Latence en ms
    embed = discord.Embed(title="Pong!", description=f"Latence: {latency}ms", color=discord.Color.green())

    await ctx.send(embed=embed)

# Vérification si l'utilisateur est l'owner du bot
def is_owner(ctx):
    return ctx.author.id == ISEY_ID

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

@bot.hybrid_command()
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


@bot.hybrid_command( 
    name="balance",
    aliases=["bal", "money"],
    description="Affiche ta balance ou celle d'un autre utilisateur."
)
async def bal(ctx: commands.Context, user: discord.User = None):
    if ctx.guild is None:
        return await ctx.send("Cette commande ne peut être utilisée qu'en serveur.")

    user = user or ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    def get_or_create_user_data(guild_id: int, user_id: int):
        data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
        if not data:
            data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
            collection.insert_one(data)
        return data

    data = get_or_create_user_data(guild_id, user_id)
    cash = data.get("cash", 0)
    bank = data.get("bank", 0)
    total = cash + bank

    # Classement des utilisateurs
    all_users_data = list(collection.find({"guild_id": guild_id}))
    sorted_users = sorted(
        all_users_data,
        key=lambda u: u.get("cash", 0) + u.get("bank", 0),
        reverse=True
    )
    rank = next((i + 1 for i, u in enumerate(sorted_users) if u["user_id"] == user_id), None)

    role_name = f"Tu as le rôle **[𝑺ץ] Top {rank}** ! Félicitations !" if rank in TOP_ROLES else None

    emoji_currency = "<:ecoEther:1341862366249357374>"

    def ordinal(n: int) -> str:
        return f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'}"

    # Création de l'embed
    embed = discord.Embed(color=discord.Color.blue())
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

    # Ajout du champ classement seulement si rank existe
    if rank:
        embed.add_field(
            name="Leaderboard Rank",
            value=f"{ordinal(rank)}",
            inline=False
        )

    # Champ des finances (titre invisible)
    embed.add_field(
        name="Ton Solde:",
        value=(
            f"**Cash :** {int(cash):,} {emoji_currency}\n"
            f"**Banque :** {int(bank):,} {emoji_currency}\n"
            f"**Total :** {int(total):,} {emoji_currency}"
        ),
        inline=False
    )


    await ctx.send(embed=embed)

@bot.hybrid_command(name="deposit", aliases=["dep"], description="Dépose de l'argent de ton portefeuille vers ta banque.")
@app_commands.describe(amount="Montant à déposer (ou 'all')")
async def deposit(ctx: commands.Context, amount: str):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0, "bank": 0}
    cash = data.get("cash", 0)
    bank = data.get("bank", 0)

    # Cas "all"
    if amount.lower() == "all":
        if cash == 0:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, tu n'as rien à déposer.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)
        deposit_amount = int(cash)

    else:
        # Vérification si le montant est valide (positif et numérique)
        if not amount.isdigit() or int(amount) <= 0:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, montant invalide. Utilise un nombre positif ou `all`.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

        deposit_amount = int(amount)

        # Vérifier si l'utilisateur a suffisamment d'argent
        if deposit_amount > cash:
            embed = discord.Embed(
                description=(
                    f"<:classic_x_mark:1362711858829725729> {user.mention}, tu n'as pas assez de cash à déposer. "
                    f"Tu as actuellement <:ecoEther:1341862366249357374> **{int(cash):,}** dans ton portefeuille."
                ),
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

    # Mise à jour des données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"cash": -deposit_amount, "bank": deposit_amount}},
        upsert=True
    )

    # Embed de succès
    embed = discord.Embed(
        description=f"<:Check:1362710665663615147> Tu as déposé <:ecoEther:1341862366249357374> **{int(deposit_amount):,}** dans ta banque !",
        color=discord.Color.green()
    )
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="withdraw", aliases=["with"], description="Retire de l'argent de ta banque vers ton portefeuille.")
async def withdraw(ctx: commands.Context, amount: str):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Chercher les données actuelles
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0, "bank": 0}
    cash = data.get("cash", 0)
    bank = data.get("bank", 0)

    # Gérer le cas "all"
    if amount.lower() == "all":
        if bank == 0:
            embed = discord.Embed(
                description="💸 Tu n'as rien à retirer.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)
        withdrawn_amount = int(bank)
    else:
        # Vérifie que c'est un nombre valide
        if not amount.isdigit() or int(amount) <= 0:
            embed = discord.Embed(
                description="❌ Montant invalide. Utilise un nombre positif ou `all`.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

        withdrawn_amount = int(amount)

        if withdrawn_amount > bank:
            embed = discord.Embed(
                description=(
                    f"<:classic_x_mark:1362711858829725729> Tu n'as pas autant à retirer. "
                    f"Tu as actuellement <:ecoEther:1341862366249357374> **{int(bank):,}** dans ta banque."
                ),
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

    # Mise à jour dans la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"cash": withdrawn_amount, "bank": -withdrawn_amount}},
        upsert=True
    )

    # Création de l'embed de succès
    embed = discord.Embed(
        description=f"<:Check:1362710665663615147> Tu as retiré <:ecoEther:1341862366249357374> **{int(withdrawn_amount):,}** de ta banque !",
        color=discord.Color.green()
    )
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="add-money", description="Ajoute de l'argent à un utilisateur (réservé aux administrateurs).")
@app_commands.describe(
    user="L'utilisateur à créditer",
    amount="Le montant à ajouter",
    location="Choisis entre cash ou bank"
)
@app_commands.choices(location=[
    app_commands.Choice(name="Cash", value="cash"),
    app_commands.Choice(name="Bank", value="bank"),
])
@commands.has_permissions(administrator=True)
async def add_money(ctx: commands.Context, user: discord.User, amount: int, location: app_commands.Choice[str]):
    if amount <= 0:
        return await ctx.send("❌ Le montant doit être supérieur à 0.")

    guild_id = ctx.guild.id
    user_id = user.id
    field = location.value

    # Récupération du solde actuel
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0, "bank": 0}
    balance_before = int(data.get(field, 0))

    # Mise à jour du solde
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {field: amount}},
        upsert=True
    )

    balance_after = balance_before + amount

    # Log dans le salon économique
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Ajout d'argent",
        int(amount),
        balance_before,
        balance_after,
        f"Ajout de {int(amount):,} <:ecoEther:1341862366249357374> dans le compte {field} de {user.mention} par {ctx.author.mention}."
    )

    # Embed de confirmation
    embed = discord.Embed(
        title="✅ Ajout effectué avec succès !",
        description=f"**{int(amount):,} <:ecoEther:1341862366249357374>** ont été ajoutés à la **{field}** de {user.mention}.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs de permissions
@add_money.error
async def add_money_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")
    else:
        await ctx.send("❌ Une erreur est survenue lors de l'exécution de la commande.")

@bot.hybrid_command(name="remove-money", description="Retire de l'argent à un utilisateur.")
@app_commands.describe(user="L'utilisateur ciblé", amount="Le montant à retirer", location="Choisis entre cash ou bank")
@app_commands.choices(location=[
    app_commands.Choice(name="Cash", value="cash"),
    app_commands.Choice(name="Bank", value="bank"),
])
@commands.has_permissions(administrator=True)
async def remove_money(ctx: commands.Context, user: discord.User, amount: int, location: app_commands.Choice[str]):
    if amount <= 0:
        return await ctx.send("❌ Le montant doit être supérieur à 0.")

    guild_id = ctx.guild.id
    user_id = user.id
    field = location.value

    # Récupération du solde actuel
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0, "bank": 0}
    current_balance = int(data.get(field, 0))
    balance_before = current_balance
    balance_after = balance_before - amount

    # Mise à jour du solde (peut devenir négatif)
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {field: -amount}},
        upsert=True
    )

    # Log dans le salon éco
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Retrait d'argent",
        -int(amount),
        balance_before,
        balance_after,
        f"Retrait de {int(amount):,} <:ecoEther:1341862366249357374> dans le compte {field} de {user.mention} par {ctx.author.mention}."
    )

    # Embed confirmation
    embed = discord.Embed(
        title="✅ Retrait effectué avec succès !",
        description=f"**{int(amount):,} <:ecoEther:1341862366249357374>** a été retiré de la **{field}** de {user.mention}.\nNouveau solde : **{balance_after:,}** <:ecoEther:1341862366249357374>",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@remove_money.error
async def remove_money_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu dois être administrateur pour utiliser cette commande.")
    else:
        await ctx.send("❌ Une erreur est survenue.")

@bot.hybrid_command(name="set-money", description="Définit un montant exact dans le cash ou la bank d’un utilisateur.")
@app_commands.describe(user="L'utilisateur ciblé", amount="Le montant à définir", location="Choisis entre cash ou bank")
@app_commands.choices(location=[
    app_commands.Choice(name="Cash", value="cash"),
    app_commands.Choice(name="Bank", value="bank"),
])
@commands.has_permissions(administrator=True)
async def set_money(ctx: commands.Context, user: discord.User, amount: int, location: app_commands.Choice[str]):
    if amount < 0:
        return await ctx.send("❌ Le montant ne peut pas être négatif.")

    guild_id = ctx.guild.id
    user_id = user.id
    field = location.value

    # Récupération du solde actuel
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0, "bank": 0}
    balance_before = int(data.get(field, 0))

    # Mise à jour de la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {field: int(amount)}},
        upsert=True
    )

    # Log dans le salon de logs économiques
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Définition du solde",
        int(amount) - balance_before,
        balance_before,
        int(amount),
        f"Le solde du compte `{field}` de {user.mention} a été défini à {int(amount):,} <:ecoEther:1341862366249357374> par {ctx.author.mention}."
    )

    # Création de l'embed
    embed = discord.Embed(
        title=f"{user.display_name} - {user.name}",
        description=f"Le montant de **{field}** de {user.mention} a été défini à **{int(amount):,} <:ecoEther:1341862366249357374>**.",
        color=discord.Color.green()
    )
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs de permissions
@set_money.error
async def set_money_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu dois être administrateur pour utiliser cette commande.")
    else:
        await ctx.send("❌ Une erreur est survenue.")

@bot.hybrid_command(name="pay", description="Paie un utilisateur avec tes coins.")
@app_commands.describe(user="L'utilisateur à qui envoyer de l'argent", amount="Montant à transférer ou 'all' pour tout envoyer")
async def pay(ctx: commands.Context, user: discord.User, amount: str):
    sender = ctx.author
    guild_id = ctx.guild.id

    if user.id == sender.id:
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> {sender.mention}, tu ne peux pas te payer toi-même.",
            color=discord.Color.red()
        )
        embed.set_author(name=sender.display_name, icon_url=sender.display_avatar.url)
        return await ctx.send(embed=embed)

    sender_data = collection.find_one({"guild_id": guild_id, "user_id": sender.id}) or {"cash": 0}
    sender_cash = int(sender_data.get("cash", 0))

    # Gestion du mot-clé "all"
    if amount.lower() == "all":
        if sender_cash <= 0:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {sender.mention}, tu n'as pas d'argent à envoyer.",
                color=discord.Color.red()
            )
            embed.set_author(name=sender.display_name, icon_url=sender.display_avatar.url)
            return await ctx.send(embed=embed)
        amount = sender_cash
    else:
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {sender.mention}, le montant doit être un nombre positif ou 'all'.",
                color=discord.Color.red()
            )
            embed.set_author(name=sender.display_name, icon_url=sender.display_avatar.url)
            return await ctx.send(embed=embed)

        if sender_cash < amount:
            embed = discord.Embed(
                description=(
                    f"<:classic_x_mark:1362711858829725729> {sender.mention}, tu n'as pas assez de cash. "
                    f"Tu as actuellement <:ecoEther:1341862366249357374> **{sender_cash:,}** dans ton portefeuille."
                ),
                color=discord.Color.red()
            )
            embed.set_author(name=sender.display_name, icon_url=sender.display_avatar.url)
            return await ctx.send(embed=embed)

    # Mise à jour des soldes
    collection.update_one(
        {"guild_id": guild_id, "user_id": sender.id},
        {"$inc": {"cash": -amount}},
        upsert=True
    )

    collection.update_one(
        {"guild_id": guild_id, "user_id": user.id},
        {"$inc": {"cash": amount}},
        upsert=True
    )

    # Log dans le salon économique
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Paiement reçu",
        amount,
        None,
        None,
        f"{user.mention} a reçu **{amount:,} <:ecoEther:1341862366249357374>** de la part de {sender.mention}."
    )

    # Embed de succès
    embed = discord.Embed(
        description=(
            f"<:Check:1362710665663615147> {user.mention} a reçu **{amount:,}** <:ecoEther:1341862366249357374> de ta part."
        ),
        color=discord.Color.green()
    )
    embed.set_author(name=sender.display_name, icon_url=sender.display_avatar.url)
    embed.set_footer(text=f"Paiement effectué à {user.display_name}", icon_url=user.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@pay.error
async def pay_error(ctx, error):
    embed = discord.Embed(
        description="<:classic_x_mark:1362711858829725729> Une erreur est survenue lors du paiement.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name="work", aliases=["wk"], description="Travaille et gagne de l'argent !")
async def work(ctx: commands.Context):
    if ctx.guild is None:
        return await ctx.send("Cette commande ne peut être utilisée qu'en serveur.")
    
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id
    now = datetime.utcnow()

    # Vérification du cooldown
    cooldown_data = collection6.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    last_work_time = cooldown_data.get("last_work_time")

    if last_work_time:
        time_diff = now - last_work_time
        cooldown = timedelta(minutes=30)
        if time_diff < cooldown:
            remaining = cooldown - time_diff
            minutes_left = int(remaining.total_seconds() // 60)

            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, tu dois attendre **{minutes_left} minutes** avant de pouvoir retravailler.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

    # Gain aléatoire
    amount = random.randint(100, 1000)

    # Récupération ou création des données utilisateur
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not user_data:
        user_data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
        collection.insert_one(user_data)

    initial_cash = user_data.get("cash", 1500)

    # Mise à jour du cooldown
    collection6.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_work_time": now}},
        upsert=True
    )

    # Mise à jour du cash
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"cash": amount}},
        upsert=True
    )

    # Log + messages variés
    messages = [
        f"Tu as travaillé dur et gagné **{amount:,} <:ecoEther:1341862366249357374>**. Bien joué !",
        f"Bravo ! Tu as gagné **{amount:,} <:ecoEther:1341862366249357374>** après ton travail.",
        f"Tu as travaillé avec assiduité et récolté **{amount:,} <:ecoEther:1341862366249357374>**.",
        f"Du bon travail ! Voici **{amount:,} <:ecoEther:1341862366249357374>** pour toi.",
        f"Félicitations, tu as gagné **{amount:,} <:ecoEther:1341862366249357374>** pour ton travail.",
        f"Tu as gagné **{amount:,} <:ecoEther:1341862366249357374>** après une journée de travail bien remplie !",
        f"Bien joué ! **{amount:,} <:ecoEther:1341862366249357374>** ont été ajoutés à ta balance.",
        f"Voici ta récompense pour ton travail : **{amount:,} <:ecoEther:1341862366249357374>**.",
        f"Tu es payé pour ton dur labeur : **{amount:,} <:ecoEther:1341862366249357374>**.",
    ]
    message = random.choice(messages)

    # Log de l'action
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Travail effectué",
        amount,
        initial_cash,
        initial_cash + amount,
        f"{user.mention} a gagné **{amount:,} <:ecoEther:1341862366249357374>** pour son travail."
    )

    # Embed de succès
    embed = discord.Embed(
        description=message,
        color=discord.Color.green()
    )
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    embed.set_footer(text="Commande de travail", icon_url=user.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@work.error
async def work_error(ctx, error):
    embed = discord.Embed(
        description="<:classic_x_mark:1362711858829725729> Une erreur est survenue lors de l'utilisation de la commande `work`.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name="slut", description="Tente ta chance dans une aventure sexy pour gagner de l'argent... ou tout perdre.")
async def slut(ctx: commands.Context):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id
    now = datetime.utcnow()

    # Cooldown 30 min
    cooldown_data = collection3.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    last_slut_time = cooldown_data.get("last_slut_time")

    if last_slut_time:
        time_diff = now - last_slut_time
        if time_diff < timedelta(minutes=30):
            remaining = timedelta(minutes=30) - time_diff
            minutes_left = int(remaining.total_seconds() // 60)
            return await ctx.send(f"<:classic_x_mark:1362711858829725729> Tu dois encore patienter **{minutes_left} minutes** avant de retenter une nouvelle aventure sexy.")

    # Déterminer le résultat
    outcome = random.choice(["gain", "loss"])
    amount_gain = random.randint(100, 1000)  # Valeur pour un gain
    amount_loss = random.randint(1, 500)  # Valeur pour une perte (indépendante)

    # Récupérer ou créer données joueur
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not user_data:
        user_data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
        collection.insert_one(user_data)

    balance_before = user_data.get("cash", 1500)

    # Vérifier si l'utilisateur a le rôle spécial
    has_special_role = any(role.id == 1365313292477927464 for role in user.roles)

    if outcome == "gain" or has_special_role:
        messages = [
            f"<:Check:1362710665663615147> Tu as séduit la bonne personne et reçu **{int(amount_gain)} <:ecoEther:1341862366249357374>** en cadeau.",
            f"<:Check:1362710665663615147> Une nuit torride t’a valu **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tu as été payé pour tes charmes : **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Ta prestation a fait des ravages, tu gagnes **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Ce client généreux t’a offert **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tu as chauffé la salle et récolté **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tes talents ont été récompensés avec **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tu as dominé la scène, et gagné **{int(amount_gain)} <:ecoEther:1341862366249357374>**.",
        ]
        message = random.choice(messages)

        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": amount_gain}},
            upsert=True
        )

        balance_after = balance_before + amount_gain
        await log_eco_channel(bot, guild_id, user, "Gain après slut", amount_gain, balance_before, balance_after)

    else:
        messages = [
            f"<:classic_x_mark:1362711858829725729> Ton plan a échoué, tu perds **{int(amount_loss)} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Ton client a disparu sans payer. Tu perds **{int(amount_loss)} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> T’as glissé pendant ton show… Résultat : **{int(amount_loss)} <:ecoEther:1341862366249357374>** de frais médicaux.",
            f"<:classic_x_mark:1362711858829725729> Mauvais choix de client, il t’a volé **{int(amount_loss)} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Une nuit sans succès… Tu perds **{int(amount_loss)} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Ton charme n’a pas opéré… Pertes : **{int(amount_loss)} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Tu as été arnaqué par un faux manager. Tu perds **{int(amount_loss)} <:ecoEther:1341862366249357374>**.",
        ]
        message = random.choice(messages)

        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": -amount_loss}},
            upsert=True
        )

        balance_after = balance_before - amount_loss
        await log_eco_channel(bot, guild_id, user, "Perte après slut", -amount_loss, balance_before, balance_after)

    # Mise à jour du cooldown
    collection3.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_slut_time": now}},
        upsert=True
    )

    # Embed
    embed = discord.Embed(
        title="💋 Résultat de ta prestation",
        description=message,
        color=discord.Color.blue() if outcome == "gain" else discord.Color.dark_red()
    )
    embed.set_footer(text=f"Aventure tentée par {user}", icon_url=user.display_avatar.url)

    await ctx.send(embed=embed)

@slut.error
async def slut_error(ctx, error):
    await ctx.send("<:classic_x_mark:1362711858829725729> Une erreur est survenue pendant la commande.")

@bot.hybrid_command(name="crime", description="Participe à un crime pour essayer de gagner de l'argent, mais attention, tu pourrais perdre !")
async def crime(ctx: commands.Context):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    now = datetime.utcnow()
    cooldown_data = collection4.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    last_crime_time = cooldown_data.get("last_crime_time")

    if last_crime_time:
        time_diff = now - last_crime_time
        if time_diff < timedelta(minutes=30):
            remaining = timedelta(minutes=30) - time_diff
            minutes_left = int(remaining.total_seconds() // 60)
            return await ctx.send(f"<:classic_x_mark:1362711858829725729> Tu dois attendre encore **{minutes_left} minutes** avant de pouvoir recommencer.")

    outcome = random.choice(["gain", "loss"])
    
    # Séparation des valeurs de gain et de perte
    gain_amount = random.randint(100, 1000)  # Valeur de gain
    loss_amount = random.randint(1, 750)  # Valeur de perte

    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    balance_before = user_data.get("cash", 0)

    # Vérifier si l'utilisateur a le rôle spécial
    has_special_role = any(role.id == 1365313292477927464 for role in user.roles)

    if outcome == "gain" or has_special_role:
        messages = [
            f"Tu as braqué une banque sans te faire repérer et gagné **{gain_amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as volé une mallette pleine de billets ! Gain : **{gain_amount} <:ecoEther:1341862366249357374>**.",
            # Autres messages pour les gains
        ]
        message = random.choice(messages)

        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": gain_amount}},
            upsert=True
        )

        balance_after = balance_before + gain_amount
        await log_eco_channel(bot, guild_id, user, "Gain après crime", gain_amount, balance_before, balance_after)

        embed = discord.Embed(
            title="💸 Tu as réussi ton crime !",
            description=message,
            color=discord.Color.green()
        )

    else:
        messages = [
            f"Tu t’es fait attraper par la police et tu perds **{loss_amount} <:ecoEther:1341862366249357374>** en caution.",
            f"Ton complice t’a trahi et s’est enfui avec **{loss_amount} <:ecoEther:1341862366249357374>**.",
            # Autres messages pour les pertes
        ]
        message = random.choice(messages)

        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": -loss_amount}},
            upsert=True
        )

        balance_after = balance_before - loss_amount
        await log_eco_channel(bot, guild_id, user, "Perte après crime", -loss_amount, balance_before, balance_after)

        embed = discord.Embed(
            title="🚨 Échec du crime !",
            description=message,
            color=discord.Color.red()
        )

    collection4.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_crime_time": now}},
        upsert=True
    )

    embed.set_footer(text=f"Action effectuée par {user}", icon_url=user.display_avatar.url)
    await ctx.send(embed=embed)

@crime.error
async def crime_error(ctx, error):
    await ctx.send("<:classic_x_mark:1362711858829725729> Une erreur est survenue lors de la commande.")

@bot.command(name="buy", aliases=["chicken", "c", "h", "i", "k", "e", "n"])
async def buy_item(ctx, item: str = "chicken"):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    item = "chicken"  # Forcer l'achat du chicken

    # Vérifier si l'utilisateur possède déjà un chicken
    data = collection7.find_one({"guild_id": guild_id, "user_id": user_id})
    if data and data.get("chicken", False):
        embed = discord.Embed(
            description="<:classic_x_mark:1362711858829725729> Vous possédez déjà un chicken.\nEnvoyez-le au combat avec la commande `cock-fight <pari>`.",
            color=discord.Color.red()
        )
        embed.set_author(name=f"{user.display_name}", icon_url=user.display_avatar.url)
        await ctx.send(embed=embed)
        return

    # Vérifier le solde (champ cash)
    balance_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance = balance_data.get("cash", 0) if balance_data else 0

    items_for_sale = {
        "chicken": 10,
    }

    if item in items_for_sale:
        price = items_for_sale[item]

        if balance >= price:
            # Retirer du cash
            collection.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$inc": {"cash": -price}},
                upsert=True
            )

            # Ajouter le chicken
            collection7.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": {item: True}},
                upsert=True
            )

            # Logs économiques
            balance_after = balance - price
            await log_eco_channel(
                bot, guild_id, user, "Achat", price, balance, balance_after,
                f"Achat d'un **{item}**"
            )

            # Embed de confirmation
            embed = discord.Embed(
                description="<:Check:1362710665663615147> Vous avez acheté un chicken pour combattre !\nUtilisez la commande `cock-fight <pari>`",
                color=discord.Color.green()
            )
            embed.set_author(name=f"{user.display_name}", icon_url=user.display_avatar.url)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> Vous n'avez pas assez de coins pour acheter un **{item}** !",
                color=discord.Color.red()
            )
            embed.set_author(name=f"{user.display_name}", icon_url=user.display_avatar.url)
            await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> Cet item n'est pas disponible à l'achat.",
            color=discord.Color.red()
        )
        embed.set_author(name=f"{user.display_name}", icon_url=user.display_avatar.url)
        await ctx.send(embed=embed)

@bot.command(name="cock-fight", aliases=["cf"])
async def cock_fight(ctx, amount: str):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    config = get_cf_config(guild_id)
    max_bet = config.get("max_bet", 7500)
    max_chance = config.get("max_chance", 100)
    start_chance = config.get("start_chance", 50)

    # Vérifier si l'utilisateur a un chicken
    data = collection7.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data or not data.get("chicken", False):
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> {user.mention}, tu n'as pas de poulet ! Utilise la commande `!!buy chicken` pour en acheter un.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifier le solde de l'utilisateur
    balance_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance = balance_data.get("cash", 0) if balance_data else 0

    # Gérer les mises "all" ou "half"
    if amount.lower() == "all":
        if balance == 0:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, ton cash est vide.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        if balance > max_bet:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, ta mise dépasse la limite de **{max_bet} <:ecoEther:1341862366249357374>**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        amount = balance

    elif amount.lower() == "half":
        if balance == 0:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, ton cash est vide.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        amount = balance // 2
        if amount > max_bet:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, la moitié de ton cash dépasse la limite de **{max_bet} <:ecoEther:1341862366249357374>**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

    else:
        try:
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, entre un montant valide, ou utilise `all` ou `half`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

    # Vérifier que l'utilisateur a assez d'argent
    if amount > balance:
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> {user.mention}, tu n'as pas assez de cash pour cette mise.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    if amount <= 0:
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> {user.mention}, la mise doit être positive.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    if amount > max_bet:
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> {user.mention}, la mise est limitée à **{max_bet} <:ecoEther:1341862366249357374>**.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Chance de victoire
    win_data = collection6.find_one({"guild_id": guild_id, "user_id": user_id})
    win_chance = win_data.get("win_chance", start_chance)

    did_win = random.randint(1, 100) <= win_chance

    if did_win:
        win_amount = amount
        new_chance = min(win_chance + 1, max_chance)

        # Mise à jour de la base
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": win_amount}},
            upsert=True
        )
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"win_chance": new_chance}},
            upsert=True
        )

        # Embed victoire
        embed = discord.Embed(
            description=f"<:Check:1362710665663615147> {user.mention}, ton poulet a **gagné** le combat et t’a rapporté <:ecoEther:1341862366249357374> **{win_amount}** ! 🐓",
            color=discord.Color.green()
        )
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else user.default_avatar.url)

        embed.set_footer(text=f"Chicken strength (chance of winning): {new_chance}%")

        await ctx.send(embed=embed)

        balance_after = balance + win_amount
        await log_eco_channel(
            bot, guild_id, user, "Victoire au Cock-Fight", win_amount, balance, balance_after,
            f"Victoire au Cock-Fight avec un gain de **{win_amount}**"
        )

    else:
        # Défaite : poulet meurt
        collection7.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"chicken": False}}
        )
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": -amount}},
            upsert=True
        )
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {
                "$set": {"win_chance": start_chance},
            },
            upsert=True
        )

        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> {user.mention}, ton poulet est **mort** au combat... <:imageremovebgpreview53:1362693948702855360>",
            color=discord.Color.red()
        )
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
        await ctx.send(embed=embed)

        balance_after = balance - amount
        await log_eco_channel(
            bot, guild_id, user, "Défaite au Cock-Fight", -amount, balance, balance_after,
            f"Défaite au Cock-Fight avec une perte de **{amount}**"
        )

@bot.command(name="set-cf-depart-chance")
@commands.has_permissions(administrator=True)
async def set_depart_chance(ctx, pourcent: str = None):
    if pourcent is None:
        return await ctx.send("⚠️ Merci de spécifier un pourcentage (entre 1 et 100). Exemple : `!set-cf-depart-chance 50`")

    if not pourcent.isdigit():
        return await ctx.send("⚠️ Le pourcentage doit être un **nombre entier**.")

    pourcent = int(pourcent)
    if not 1 <= pourcent <= 100:
        return await ctx.send("❌ Le pourcentage doit être compris entre **1** et **100**.")

    # Mettre à jour la base de données avec la nouvelle valeur
    collection8.update_one({"guild_id": ctx.guild.id}, {"$set": {"start_chance": pourcent}}, upsert=True)

    # Envoyer un message dans le salon de log spécifique (si configuré)
    config = collection9.find_one({"guild_id": ctx.guild.id})
    channel_id = config.get("eco_log_channel") if config else None

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔧 Log de Configuration",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Action", value="Mise à jour de la chance de départ", inline=True)
            embed.add_field(name="Chance de départ", value=f"{pourcent}%", inline=True)
            await channel.send(embed=embed)

    await ctx.send(f"✅ La chance de départ a été mise à **{pourcent}%**.")


@bot.command(name="set-cf-max-chance")
@commands.has_permissions(administrator=True)
async def set_max_chance(ctx, pourcent: str = None):
    if pourcent is None:
        return await ctx.send("⚠️ Merci de spécifier un pourcentage (entre 1 et 100). Exemple : `!set-cf-max-chance 90`")

    if not pourcent.isdigit():
        return await ctx.send("⚠️ Le pourcentage doit être un **nombre entier**.")

    pourcent = int(pourcent)
    if not 1 <= pourcent <= 100:
        return await ctx.send("❌ Le pourcentage doit être compris entre **1** et **100**.")

    # Mettre à jour la base de données avec la nouvelle valeur
    collection8.update_one({"guild_id": ctx.guild.id}, {"$set": {"max_chance": pourcent}}, upsert=True)

    # Envoyer un message dans le salon de log spécifique (si configuré)
    config = collection9.find_one({"guild_id": ctx.guild.id})
    channel_id = config.get("eco_log_channel") if config else None

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔧 Log de Configuration",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Action", value="Mise à jour de la chance maximale de victoire", inline=True)
            embed.add_field(name="Chance maximale", value=f"{pourcent}%", inline=True)
            await channel.send(embed=embed)

    await ctx.send(f"✅ La chance maximale de victoire est maintenant de **{pourcent}%**.")

@bot.command(name="set-cf-mise-max")
@commands.has_permissions(administrator=True)
async def set_max_mise(ctx, amount: str = None):
    if amount is None:
        return await ctx.send("⚠️ Merci de spécifier une mise maximale (nombre entier positif). Exemple : `!set-cf-mise-max 1000`")

    if not amount.isdigit():
        return await ctx.send("⚠️ La mise maximale doit être un **nombre entier**.")

    amount = int(amount)
    if amount <= 0:
        return await ctx.send("❌ La mise maximale doit être un **nombre supérieur à 0**.")

    # Mettre à jour la base de données avec la nouvelle mise maximale
    collection8.update_one({"guild_id": ctx.guild.id}, {"$set": {"max_bet": amount}}, upsert=True)

    # Envoyer un message dans le salon de log spécifique (si configuré)
    config = collection9.find_one({"guild_id": ctx.guild.id})
    channel_id = config.get("eco_log_channel") if config else None

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔧 Log de Configuration",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Action", value="Mise à jour de la mise maximale", inline=True)
            embed.add_field(name="Mise maximale", value=f"{amount} <:ecoEther:1341862366249357374>", inline=True)
            await channel.send(embed=embed)

    await ctx.send(f"✅ La mise maximale a été mise à **{amount} <:ecoEther:1341862366249357374>**.")

# Gestion des erreurs liées aux permissions
@set_depart_chance.error
@set_max_chance.error
@set_max_mise.error
async def cf_config_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("❌ Une erreur est survenue lors de l’exécution de la commande.")
        print(f"[ERREUR] {error}")
    else:
        await ctx.send("⚠️ Une erreur inconnue est survenue.")
        print(f"[ERREUR INCONNUE] {error}")

class CFConfigView(ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    @ui.button(label="🔄 Reset aux valeurs par défaut", style=discord.ButtonStyle.red)
    async def reset_defaults(self, interaction: Interaction, button: ui.Button):
        # Vérifier si l'utilisateur est admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Tu n'as pas la permission de faire ça.", ephemeral=True)
            return

        # Reset config
        default_config = {
            "start_chance": 50,
            "max_chance": 100,
            "max_bet": 20000
        }
        collection8.update_one(
            {"guild_id": self.guild_id},
            {"$set": default_config},
            upsert=True
        )
        await interaction.response.send_message("✅ Les valeurs par défaut ont été rétablies.", ephemeral=True)

@bot.command(name="cf-config")
@commands.has_permissions(administrator=True)
async def cf_config(ctx):
    guild_id = ctx.guild.id
    config = get_cf_config(guild_id)

    start_chance = config.get("start_chance", 50)
    max_chance = config.get("max_chance", 100)
    max_bet = config.get("max_bet", 20000)

    embed = discord.Embed(
        title="⚙️ Configuration Cock-Fight",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎯 Chance de départ", value=f"**{start_chance}%**", inline=False)
    embed.add_field(name="📈 Chance max", value=f"**{max_chance}%**", inline=False)
    embed.add_field(name="💰 Mise maximale", value=f"**{max_bet} <:ecoEther:1341862366249357374>**", inline=False)
    embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed, view=CFConfigView(guild_id))

@bot.command(name="set-eco-log")
@commands.has_permissions(administrator=True)
async def set_eco_log(ctx, channel: discord.TextChannel):
    guild_id = ctx.guild.id
    collection9.update_one(
        {"guild_id": guild_id},
        {"$set": {"eco_log_channel": channel.id}},
        upsert=True
    )
    await ctx.send(f"✅ Les logs économiques seront envoyés dans {channel.mention}")

# Fonction pour récupérer ou créer les données utilisateur
def get_or_create_user_data(guild_id: int, user_id: int):
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data:
        data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
        collection.insert_one(data)
    return data

# Valeur des cartes
card_values = {
    'A': 11,
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10
}

# ÉMOJIS DE CARTES
card_emojis = {
    'A': ['<:ACarreauRouge:1362752186291060928>', '<:APiqueNoir:1362752281363087380>', '<:ACoeurRouge:1362752392508084264>', '<:ATrefleNoir:1362752416046518302>'],
    '2': ['<:2CarreauRouge:1362752434677743767>', '<:2PiqueNoir:1362752455082901634>', '<:2CoeurRouge:1362752473852547082>', '<:2TrefleNoir:1362752504097406996>'],
    '3': ['<:3CarreauRouge:1362752551065358459>', '<:3PiqueNoir:1362752595269255248>', '<:3CoeurRouge:1362752651565207562>', '<:3TrefleNoir:1362752672922603681>'],
    '4': ['<:4CarreauRouge:1362752709412917460>', '<:4PiqueNoir:1362752726592917555>', '<:4CoeurRouge:1362752744405991555>', '<:4TrefleNoir:1362752764924530848>'],
    '5': ['<:5CarreauRouge:1362752783316549743>', '<:5PiqueNoir:1362752806368313484>', '<:5CoeurRouge:1362752826123485205>', '<:5TrefleNoir:1362752846889615470>'],
    '6': ['<:6CarreauRouge:1362752972831850626>', '<:6PiqueNoir:1362752993203847409>', '<:6CoeurRouge:1362753014921953362>', '<:6TrefleNoir:1362753036404916364>'],
    '7': ['<:7CarreauRouge:1362753062392823809>', '<:7PiqueNoir:1362753089547010219>', '<:7CoeurRouge:1362753147407433789>', '<:7TrefleNoir:1362753178403209286>'],
    '8': ['<:8CarreauRouge:1362753220665151620>', '<:8PiqueNoir:1362753245675524177>', '<:8CoeurRouge:1362753270065528944>', '<:8TrefleNoir:1362753296552689824>'],
    '9': ['<:9CarreauRouge:1362753331507892306>', '<:9PiqueNoir:1362753352903036978>', '<:9CoeurRouge:1362753387514429540>', '<:9TrefleNoir:1362753435153469673>'],
    '10': ['<:10CarreauRouge:1362753459505594390>', '<:10PiqueNoir:1362753483429646529>', '<:10CoeurRouge:1362753511263047731>', '<:10TrefleNoir:1362753534621122744>'],
    'J': ['<:JValetCarreau:1362753572495822938>', '<:JValetPique:1362753599771246624>', '<:JValetCoeur:1362753627340537978>', '<:JValetTrefle:1362753657753309294>'],
    'Q': ['<:QReineCarreau:1362754443543711744>', '<:QReinePique:1362754468390764576>', '<:QReineCoeur:1362754488909299772>', '<:QReineTrefle:1362754507422830714>'],
    'K': ['<:KRoiCarreau:1362753685095976981>', '<:KRoiPique:1362753958350946385>', '<:KRoiCoeur:1362754291223498782>', '<:KRoiTrefle:1362754318276497609>']
}

# Fonction pour tirer une carte
def draw_card():
    value = random.choice(list(card_values.keys()))
    emoji = random.choice(card_emojis.get(value, ['🃏']))
    return value, emoji

# Calcul de la valeur totale d'une main
def calculate_hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        if card == 'A':
            aces += 1
        total += card_values[card]
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

# Fonction pour afficher le nombre de cartes du croupier
def dealer_cards_count(dealer_hand):
    return len(dealer_hand)

class BlackjackView(discord.ui.View):
    def __init__(self, ctx, player_hand, dealer_hand, bet, player_data, max_bet):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.bet = bet
        self.player_data = player_data
        self.guild_id = ctx.guild.id
        self.user_id = ctx.author.id
        self.max_bet = max_bet

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green, emoji="➕")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        value, _ = draw_card()
        self.player_hand.append(value)
        player_total = calculate_hand_value(self.player_hand)

        if player_total > 21:
            await self.end_game(interaction, "lose")
        else:
            # Créer un embed ici avant de l'utiliser
            embed = discord.Embed(title="Blackjack", color=discord.Color.blue())

            embed.add_field(
                name="Ta main",
                value=" ".join([card_emojis[c][0] for c in self.player_hand]) + f"\nValeur: **{calculate_hand_value(self.player_hand)}**",
                inline=False
            )

            embed.add_field(
                name="Main du croupier",
                value=f"{card_emojis[self.dealer_hand[0]][0]} 🂠\nValeur: **?**",
                inline=False
            )

            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.blurple, emoji="🛑")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        while calculate_hand_value(self.dealer_hand) < 17:
            value, _ = draw_card()
            self.dealer_hand.append(value)

        player_total = calculate_hand_value(self.player_hand)
        dealer_total = calculate_hand_value(self.dealer_hand)

        if dealer_total > 21 or player_total > dealer_total:
            await self.end_game(interaction, "win")
        elif player_total == dealer_total:
            await self.end_game(interaction, "draw")
        else:
            await self.end_game(interaction, "lose")

    async def end_game(self, interaction: discord.Interaction, result: str):
        player_total = calculate_hand_value(self.player_hand)
        dealer_total = calculate_hand_value(self.dealer_hand)

        # Détermine la couleur et le texte selon le résultat
        if result == "win":
            color = discord.Color.green()
            result_text = f"Result: Dealer bust <:ecoEther:1341862366249357374> +{self.bet}"
        
            # DONNER LA RÉCOMPENSE
            collection.update_one(
                {"guild_id": self.guild_id, "user_id": self.user_id},
                {"$inc": {"cash": self.bet * 2}}  # x2 car on rembourse la mise + gain équivalent
            )

        elif result == "lose":
            color = discord.Color.red()
            result_text = f"Result: Loss <:ecoEther:1341862366249357374> -{self.bet}"
            # (rien à faire, l'argent est déjà retiré au départ)

        else:  # draw
            color = discord.Color.gold()
            result_text = "Result: Draw"
        
            # RENDRE LA MISE
            collection.update_one(
                {"guild_id": self.guild_id, "user_id": self.user_id},
                {"$inc": {"cash": self.bet}}
            )

        embed = discord.Embed(
            color=color,
            description=result_text
        )

        embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        embed.add_field(
            name="Your Hand",
            value=" ".join([card_emojis[c][0] for c in self.player_hand]) + f"\nValue: **{calculate_hand_value(self.player_hand)}**",
            inline=True
        )

        embed.add_field(
            name="Dealer Hand",
            value=" ".join([card_emojis[c][0] for c in self.dealer_hand]) + f"\nValue: **{calculate_hand_value(self.dealer_hand)}**",
            inline=True
        )

        await interaction.response.edit_message(embed=embed, view=None)

@bot.hybrid_command(name="blackjack", aliases=["bj"], description="Joue au blackjack et tente de gagner !")
@app_commands.describe(mise="La somme à miser")
async def blackjack(ctx: commands.Context, mise: str):
    if ctx.guild is None:
        return await ctx.send(embed=discord.Embed(description="Cette commande ne peut être utilisée qu'en serveur.", color=discord.Color.red()))

    # S'assurer qu'une mise est spécifiée
    if mise is None:
        return await ctx.send(embed=discord.Embed(description="Tu dois spécifier une mise, ou utiliser 'all' ou 'half' pour miser tout ou la moitié de ton solde.", color=discord.Color.red()))

    # Traitement du cas où la mise est 'all'
    if mise == "all":
        user_data = get_or_create_user_data(ctx.guild.id, ctx.author.id)
        max_bet = 5000  # La mise maximale

        if user_data["cash"] <= max_bet:
            mise = user_data["cash"]  # Mise toute la somme disponible
        else:
            return await ctx.send(embed=discord.Embed(description=f"Ton solde est trop élevé pour miser tout, la mise maximale est de {max_bet} <:ecoEther:1341862366249357374>.", color=discord.Color.red()))

    # Traitement du cas où la mise est 'half'
    elif mise == "half":
        user_data = get_or_create_user_data(ctx.guild.id, ctx.author.id)
        max_bet = 15000  # La mise maximale
        half_cash = user_data["cash"] // 2

        if half_cash > max_bet:
            return await ctx.send(embed=discord.Embed(description=f"La moitié de ton solde est trop élevée, la mise maximale est de {max_bet} <:ecoEther:1341862366249357374>.", color=discord.Color.red()))
        else:
            mise = half_cash

    # Traitement du cas où la mise est un nombre
    elif mise:
        try:
            mise = int(mise)
        except ValueError:
            return await ctx.send(embed=discord.Embed(description="La mise doit être un nombre valide.", color=discord.Color.red()))

        user_data = get_or_create_user_data(ctx.guild.id, ctx.author.id)
        max_bet = 15000  # La mise maximale

        if mise <= 0:
            return await ctx.send(embed=discord.Embed(description="Tu dois miser une somme supérieure à 0.", color=discord.Color.red()))
        if mise < 1:
            return await ctx.send(embed=discord.Embed(description="La mise minimale est de 1 <:ecoEther:1341862366249357374>.", color=discord.Color.red()))
        if mise > max_bet:
            return await ctx.send(embed=discord.Embed(description=f"La mise maximale est de {max_bet} <:ecoEther:1341862366249357374>.", color=discord.Color.red()))
        if user_data["cash"] < mise:
            return await ctx.send(embed=discord.Embed(description="Tu n'as pas assez d'argent pour miser cette somme.", color=discord.Color.red()))

    # Mise à jour de la balance après la mise
    user_data["cash"] -= mise
    collection.update_one(
        {"guild_id": ctx.guild.id, "user_id": ctx.author.id},
        {"$set": {"cash": user_data["cash"]}}
    )

    player_hand = [draw_card()[0] for _ in range(2)]
    dealer_hand = [draw_card()[0] for _ in range(2)]

    embed = discord.Embed(
        color=discord.Color.blue(),
        description=(
            "`hit` - prendre une carte\n"
            "`stand` - finir la partie\n\n"
        )
    )

    embed.set_author(
        name=f"{ctx.author.name}",
        icon_url=ctx.author.display_avatar.url
    )

    embed.add_field(
        name="Ta main",
        value=" ".join([card_emojis[c][0] for c in player_hand]) + f"\nValeur: **{calculate_hand_value(player_hand)}**",
        inline=True
    )

    embed.add_field(
        name="Main du croupier",
        value=f"{card_emojis[dealer_hand[0]][0]} 🂠\nValeur: **?**",
        inline=True
    )

    await ctx.send(embed=embed, view=BlackjackView(ctx, player_hand, dealer_hand, mise, user_data, max_bet))

@bot.command(name="bj-max-mise", aliases=["set-max-bj"])
@commands.has_permissions(administrator=True)  # La commande est réservée aux admins
async def set_max_bj_mise(ctx, mise_max: int):
    # Vérification que la mise max est un entier et supérieure à 0
    if not isinstance(mise_max, int) or mise_max <= 0:
        embed = discord.Embed(
            title="❌ Mise maximale invalide",
            description="La mise maximale doit être un nombre entier positif.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    guild_id = ctx.guild.id

    # Charger les paramètres de Blackjack depuis la collection info_bj
    bj_config = collection10.find_one({"guild_id": guild_id})

    # Si la configuration n'existe pas, en créer une avec la mise max par défaut
    old_max_mise = 30000  # Valeur par défaut
    if bj_config:
        old_max_mise = bj_config.get("max_mise", 30000)

    # Mise à jour de la mise maximale
    collection10.update_one(
        {"guild_id": guild_id},
        {"$set": {"max_mise": mise_max}},
        upsert=True
    )

    embed = discord.Embed(
        title="✅ Mise maximale mise à jour",
        description=f"La mise maximale pour le Blackjack a été changée à {mise_max} coins.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

    # Log des changements
    await log_bj_max_mise(ctx.bot, guild_id, ctx.author, mise_max, old_max_mise)

# Gestion de l'erreur si l'utilisateur n'est pas administrateur
@set_max_bj_mise.error
async def set_max_bj_mise_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Accès refusé",
            description="Tu n'as pas les permissions nécessaires pour changer la mise maximale.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.hybrid_command(name="rob", description="Voler entre 30% et 80% du portefeuille d'un autre utilisateur.")
async def rob(ctx, user: discord.User):
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    target_id = user.id

    if user.bot or user_id == target_id:
        reason = "Tu ne peux pas voler un bot." if user.bot else "Tu ne peux pas voler des coins à toi-même."
        embed = discord.Embed(description=reason, color=discord.Color.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        return await ctx.send(embed=embed)

    # Cooldown check
    last_rob = collection14.find_one({"guild_id": guild_id, "user_id": user_id})
    if last_rob and (last_rob_time := last_rob.get("last_rob")):
        time_left = last_rob_time + timedelta(hours=1) - datetime.utcnow()
        if time_left > timedelta(0):
            mins, secs = divmod(int(time_left.total_seconds()), 60)
            hrs, mins = divmod(mins, 60)
            time_str = f"{hrs}h {mins}min" if hrs else f"{mins}min"
            embed = discord.Embed(
                description=f"⏳ Attends encore **{time_str}** avant de pouvoir voler à nouveau.",
                color=discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            return await ctx.send(embed=embed)

    # Récupération du membre cible
    target_member = ctx.guild.get_member(target_id)
    if not target_member:
        return await ctx.send(embed=discord.Embed(
            description=f"Utilisateur introuvable sur ce serveur.",
            color=discord.Color.red()
        ))

    # Anti rob par rôles stockés dans MongoDB
    anti_rob_data = collection15.find_one({"guild_id": guild_id}) or {"roles": []}
    if any(role.name in anti_rob_data["roles"] for role in target_member.roles):
        return await ctx.send(embed=discord.Embed(
            description=f"{user.display_name} est protégé contre le vol.",
            color=discord.Color.red()
        ))

    # Vérifier si la cible a le rôle qui repousse les vols (300% banque)
    has_anti_rob_reflect = discord.utils.get(target_member.roles, id=1365313284584116264)
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 1500, "bank": 0}
    if has_anti_rob_reflect:
        penalty = round(user_data["bank"] * 3.00, 2)
        penalty = min(penalty, user_data["bank"])
        collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"bank": -penalty}})

        await log_eco_channel(bot, guild_id, ctx.author, "Vol repoussé", -penalty, user_data["bank"], user_data["bank"] - penalty, f"Repoussé par {user.display_name}")

        return await ctx.send(embed=discord.Embed(
            description=f"⚠️ {user.display_name} a tenté de voler **{target_member.display_name}**, mais a été **repoussé par une aura protectrice** !\n"
                        f"💸 Il perd **{int(penalty)}** coins de sa banque !",
            color=discord.Color.red()
        ).set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url))

    # Data utilisateur/target
    target_data = collection.find_one({"guild_id": guild_id, "user_id": target_id}) or {"cash": 1500, "bank": 0}
    collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$setOnInsert": user_data}, upsert=True)
    collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$setOnInsert": target_data}, upsert=True)

    if target_data["cash"] <= 0:
        return await ctx.send(embed=discord.Embed(
            description=f"{user.display_name} n’a pas de monnaie à voler.",
            color=discord.Color.red()
        ))

    # Barrière bancaire
    if discord.utils.get(target_member.roles, id=1365311602290851880):
        now = datetime.utcnow()
        today_str = now.strftime("%Y-%m-%d")
        barrier_data = collection.find_one({"guild_id": guild_id, "user_id": target_id, "barriere_date": today_str})
        if not barrier_data:
            collection.update_one(
                {"guild_id": guild_id, "user_id": target_id},
                {"$set": {"barriere_date": today_str}},
                upsert=True
            )
            return await ctx.send(embed=discord.Embed(
                description=f"🛡️ La **barrière bancaire** de {user.display_name} a annulé le vol !",
                color=discord.Color.blue()
            ))

    # Rôles spéciaux
    has_half_rob_protection = discord.utils.get(target_member.roles, id=1365311588139274354)
    has_counter_role = discord.utils.get(target_member.roles, id=1365313254108430396)
    has_30_percent_protection = discord.utils.get(target_member.roles, id=1365312038716444672)

    # Calcul succès du vol
    robber_total = user_data["cash"] + user_data["bank"]
    rob_chance = max(80 - (robber_total // 1000), 10)
    success = random.randint(1, 100) <= rob_chance

    # Enregistrement du cooldown
    collection14.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_rob": datetime.utcnow()}},
        upsert=True
    )

    if success:
        percentage = random.randint(30, 80)
        stolen = (percentage / 100) * target_data["cash"]

        if has_half_rob_protection:
            stolen /= 2

        # Limiter à 30% si protection active
        if has_30_percent_protection:
            max_stealable = target_data["cash"] * 0.30
            stolen = min(stolen, max_stealable)

        stolen = round(stolen, 2)
        stolen = min(stolen, target_data["cash"])
        initial_stolen = stolen

        # Application du vol
        collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"cash": stolen}})
        collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$inc": {"cash": -stolen}})

        # Contre-attaque si rôle
        if has_counter_role:
            counter_amount = round(initial_stolen * 2, 2)
            collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"cash": -counter_amount}})
            collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$inc": {"cash": counter_amount}})

            new_cash = user_data["cash"] - counter_amount
            await log_eco_channel(bot, guild_id, ctx.author, "Contre-vol subi", -counter_amount, user_data["cash"], new_cash, f"Contre-attaque de {user.display_name}")
            await log_eco_channel(bot, guild_id, target_member, "Contre-vol réussi", counter_amount, target_data["cash"], target_data["cash"] + counter_amount, f"Contre-attaque sur {ctx.author.display_name}")

            return await ctx.send(embed=discord.Embed(
                description=f"🔥 Mauvais choix ! {user.display_name} a été **contre-attaqué** et a perdu **{int(counter_amount)}** — il est maintenant **dans le négatif** !",
                color=discord.Color.red()
            ).set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url))

        await log_eco_channel(bot, guild_id, ctx.author, "Vol", stolen, user_data["cash"], user_data["cash"] + stolen, f"Volé à {user.display_name}")

        return await ctx.send(embed=discord.Embed(
            description=f"💰 Tu as volé **{int(stolen)}** à **{user.display_name}** !",
            color=discord.Color.green()
        ).set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url))

    else:
        percentage = random.uniform(1, 5)
        loss = (percentage / 100) * user_data["cash"]
        loss = round(loss, 2)
        loss = min(loss, user_data["cash"])

        collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"cash": -loss}})

        await log_eco_channel(bot, guild_id, ctx.author, "Échec vol", -loss, user_data["cash"], user_data["cash"] - loss, f"Échec de vol sur {user.display_name}")

        return await ctx.send(embed=discord.Embed(
            description=f"🚨 Tu as échoué et perdu **{int(loss)}** !",
            color=discord.Color.red()
        ).set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url))

@bot.command(name="set-anti_rob")
async def set_anti_rob(ctx):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send(embed=discord.Embed(
            description="Tu n'as pas la permission d'exécuter cette commande.",
            color=discord.Color.red()
        ))

    guild_id = ctx.guild.id
    data = collection15.find_one({"guild_id": guild_id}) or {"guild_id": guild_id, "roles": []}
    anti_rob_roles = data["roles"]

    embed = discord.Embed(
        title="🔐 Gestion des rôles anti-rob",
        description="Choisis une action à effectuer ci-dessous.\n\n"
                    "**Rôles actuellement protégés :**\n"
                    f"{', '.join(anti_rob_roles) if anti_rob_roles else 'Aucun rôle protégé.'}",
        color=discord.Color.blurple()
    )

    class ActionSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Ajouter un rôle", value="add", emoji="✅"),
                discord.SelectOption(label="Supprimer un rôle", value="remove", emoji="❌")
            ]
            super().__init__(
                placeholder="Choisis une action",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Cette interaction ne t'est pas destinée.", ephemeral=True)

            await interaction.response.send_message(
                f"Tu as choisi **{self.values[0]}**. Merci de **mentionner un rôle** dans le chat.",
                ephemeral=True
            )

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel and msg.role_mentions

            try:
                msg = await bot.wait_for("message", timeout=30.0, check=check)
                role = msg.role_mentions[0]
                role_name = role.name

                if self.values[0] == "add":
                    if role_name in anti_rob_roles:
                        await ctx.send(f"🔸 Le rôle **{role_name}** est déjà protégé.")
                    else:
                        anti_rob_roles.append(role_name)
                        await ctx.send(f"✅ Le rôle **{role_name}** a été ajouté à la protection anti-rob.")
                elif self.values[0] == "remove":
                    if role_name in anti_rob_roles:
                        anti_rob_roles.remove(role_name)
                        await ctx.send(f"❌ Le rôle **{role_name}** a été retiré de la protection anti-rob.")
                    else:
                        await ctx.send(f"🔸 Le rôle **{role_name}** n’est pas protégé.")

                # Mise à jour BDD
                collection15.update_one({"guild_id": guild_id}, {"$set": {"roles": anti_rob_roles}}, upsert=True)

            except asyncio.TimeoutError:
                await ctx.send("⏱️ Temps écoulé. Merci de réessayer.")

    view = View()
    view.add_item(ActionSelect())
    await ctx.send(embed=embed, view=view)

@bot.hybrid_command(
    name="set-rr-limite",
    description="Fixe une limite de mise pour la roulette russe. (Admin seulement)"
)
@commands.has_permissions(administrator=True)  # Permet uniquement aux admins de modifier la limite
async def set_rr_limite(ctx: commands.Context, limite: int):
    if limite <= 0:
        return await ctx.send("La limite de mise doit être un nombre positif.")
    
    guild_id = ctx.guild.id

    # Mettre à jour la limite dans la collection info_rr
    collection11.update_one(
        {"guild_id": guild_id},
        {"$set": {"rr_limite": limite}},
        upsert=True  # Si la donnée n'existe pas, elle sera créée
    )

    await ctx.send(f"La limite de mise pour la roulette russe a été fixée à {limite:,} coins.")

active_rr_games = {}

@bot.command(aliases=["rr"])
async def russianroulette(ctx, arg: str):
    guild_id = ctx.guild.id
    user = ctx.author

    # Fonction pour récupérer le cash
    def get_user_cash(guild_id: int, user_id: int):
        data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
        if data:
            return data.get("cash", 0)
        return 0

    # Fonction pour créer ou récupérer les données utilisateur
    def get_or_create_user_data(guild_id, user_id):
        data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
        if not data:
            data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
            collection.insert_one(data)
        return data

    # Fonction pour parser le montant avec notation exponentielle (ex: 5e2 -> 500)
    def parse_mise(mise):
        match = re.match(r"(\d+)e(\d+)", mise)
        if match:
            base = int(match.group(1))
            exponent = int(match.group(2))
            return base * (10 ** exponent)
        else:
            return int(mise)

    if arg.isdigit() or arg.lower() == "all" or arg.lower() == "half":
        if arg.lower() == "all":
            bet = get_user_cash(guild_id, user.id)
        elif arg.lower() == "half":
            bet = get_user_cash(guild_id, user.id) // 2
        else:
            try:
                bet = parse_mise(arg)  # Utilisation de la fonction parse_mise
            except ValueError:
                return await ctx.send(embed=discord.Embed(
                    description=f"<:classic_x_mark:1362711858829725729> La mise spécifiée est invalide.",
                    color=discord.Color.from_rgb(255, 92, 92)
                ))

        if bet < 1:
            return await ctx.send(embed=discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> La mise minimale est de 1 coin.",
                color=discord.Color.from_rgb(255, 92, 92)
            ))

        if bet > 10000:
            return await ctx.send(embed=discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> La mise maximale autorisée est de 10,000 coins.",
                color=discord.Color.from_rgb(255, 92, 92)
            ))

        user_cash = get_user_cash(guild_id, user.id)

        if bet > user_cash:
            return await ctx.send(embed=discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> Tu n'as pas assez de cash pour cette mise. Tu as {user_cash} coins.",
                color=discord.Color.from_rgb(255, 92, 92)
            ))

        if guild_id in active_rr_games:
            game = active_rr_games[guild_id]
            if user in game["players"]:
                return await ctx.send(embed=discord.Embed(
                    description=f"<:classic_x_mark:1362711858829725729> Tu as déjà rejoint cette partie.",
                    color=discord.Color.from_rgb(255, 92, 92)
                ))
            if bet != game["bet"]:
                return await ctx.send(embed=discord.Embed(
                    description=f"<:classic_x_mark:1362711858829725729> Tu dois miser exactement {game['bet']} coins pour rejoindre cette partie.",
                    color=discord.Color.from_rgb(255, 92, 92)
                ))
            game["players"].append(user)
            return await ctx.send(embed=discord.Embed(
                description=f"{user.mention} a rejoint cette partie de Roulette Russe avec une mise de <:ecoEther:1341862366249357374> {bet}.",
                color=0x00FF00
            ))

        else:
            embed = discord.Embed(
                title="Nouvelle partie de Roulette Russe",
                description="> Pour démarrer cette partie : `!!rr start`\n"
                            "> Pour rejoindre : `!!rr <montant>`\n\n"
                            "**Temps restant :** 5 minutes ou 5 joueurs maximum",
                color=discord.Color.from_rgb(100, 140, 230)
            )
            msg = await ctx.send(embed=embed)

            active_rr_games[guild_id] = {
                "starter": user,
                "bet": bet,
                "players": [user],
                "message_id": msg.id
            }

            async def cancel_rr():
                await asyncio.sleep(300)
                if guild_id in active_rr_games and len(active_rr_games[guild_id]["players"]) == 1:
                    await ctx.send(embed=discord.Embed(
                        description="<:classic_x_mark:1362711858829725729> Personne n'a rejoint la roulette russe. La partie est annulée.",
                        color=discord.Color.from_rgb(255, 92, 92)
                    ))
                    del active_rr_games[guild_id]

            active_rr_games[guild_id]["task"] = asyncio.create_task(cancel_rr())

    elif arg.lower() == "start":
        game = active_rr_games.get(guild_id)
        if not game:
            return await ctx.send(embed=discord.Embed(
                description="<:classic_x_mark:1362711858829725729> Aucune partie en cours.",
                color=discord.Color.from_rgb(240, 128, 128)
            ))
        if game["starter"] != user:
            return await ctx.send(embed=discord.Embed(
                description="<:classic_x_mark:1362711858829725729> Seul le créateur de la partie peut la démarrer.",
                color=discord.Color.from_rgb(255, 92, 92)
            ))

        if len(game["players"]) < 2:
            await ctx.send(embed=discord.Embed(
                description="<:classic_x_mark:1362711858829725729> Pas assez de joueurs pour démarrer. La partie est annulée.",
                color=discord.Color.from_rgb(255, 92, 92)
            ))
            game["task"].cancel()
            del active_rr_games[guild_id]
            return

        # Début du jeu
        await ctx.send(embed=discord.Embed(
            description="<:Check:1362710665663615147> La roulette russe commence...",
            color=0x00FF00
        ))
        await asyncio.sleep(1)

        eliminated = random.choice(game["players"])
        survivors = [p for p in game["players"] if p != eliminated]

        # Phase 1 : qui meurt
        embed1 = discord.Embed(
            description=f"{eliminated.display_name} tire... et se fait avoir <:imageremovebgpreview53:1362693948702855360>",
            color=discord.Color.from_rgb(255, 92, 92)
        )
        await ctx.send(embed=embed1)
        await asyncio.sleep(1)

        # Phase 2 : les survivants
        result_embed = discord.Embed(
            title="Survivants de la Roulette Russe",
            description="\n".join([f"{p.mention} remporte <:ecoEther:1341862366249357374> {game['bet'] * 2}" for p in survivors]),
            color=0xFF5C5C
        )
        await ctx.send(embed=result_embed)

        # Distribution des gains
        for survivor in survivors:
            data = get_or_create_user_data(guild_id, survivor.id)
            data["cash"] += game["bet"] * 2  # Leur propre mise + celle du perdant
            collection.update_one(
                {"guild_id": guild_id, "user_id": survivor.id},
                {"$set": {"cash": int(data["cash"])}}  # Arrondir le cash des survivants
            )

        # Retirer la mise au perdant
        loser_data = get_or_create_user_data(guild_id, eliminated.id)
        loser_data["cash"] -= game["bet"]
        collection.update_one(
            {"guild_id": guild_id, "user_id": eliminated.id},
            {"$set": {"cash": int(loser_data["cash"])}}  # Arrondir le cash du perdant
        )

        # Suppression de la partie
        game["task"].cancel()
        del active_rr_games[guild_id]

    else:
        await ctx.send(embed=discord.Embed(
            description="Utilise `!!rr <montant>` pour lancer ou rejoindre une roulette russe.",
            color=discord.Color.from_rgb(255, 92, 92)
        ))


# Set pour suivre les joueurs ayant une roulette en cours
active_roulette_players = set()

# Numéros corrigés
RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
EVEN_NUMBERS = [i for i in range(2, 37, 2)]
ODD_NUMBERS = [i for i in range(1, 37, 2)]
COLUMN_1 = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
COLUMN_2 = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
COLUMN_3 = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]

@bot.command(name="roulette", description="Parie sur la roulette avec un montant spécifique")
async def roulette(ctx: commands.Context, bet: int, space: str):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    if user_id in active_roulette_players:
        return await ctx.send("⏳ Tu as déjà une roulette en cours ! Attends qu'elle se termine.")

    active_roulette_players.add(user_id)

    def get_or_create_user_data(guild_id: int, user_id: int):
        data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
        if not data:
            data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
            collection.insert_one(data)
        return data

    data = get_or_create_user_data(guild_id, user_id)
    cash = data.get("cash", 0)

    if bet > cash:
        active_roulette_players.remove(user_id)
        return await ctx.send(f"Tu n'as pas assez d'argent ! Tu as {cash} en cash.")

    if bet < 1:
        active_roulette_players.remove(user_id)
        return await ctx.send("⛔ La mise minimale est de 1 coin !")

    if bet > 5000:
        active_roulette_players.remove(user_id)
        return await ctx.send("⛔ La mise maximale est de 5000 !")

    # Déduction du montant parié
    collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"cash": -bet}})

    embed = discord.Embed(
        title=ctx.author.name,
        description=f"You have placed a bet of <:ecoEther:1341862366249357374>{int(bet)} on **{space}**.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Time remaining: 10 seconds")

    # Bouton Help
    view = View()
    help_button = Button(label="Help", style=discord.ButtonStyle.primary)

    async def help_callback(interaction: discord.Interaction):
        help_embed = discord.Embed(
            title="📘 Comment jouer à la Roulette",
            description=(
                "**🎯 Parier**\n"
                "Choisis l'espace sur lequel tu penses que la balle va atterrir.\n"
                "Tu peux parier sur plusieurs espaces en exécutant la commande à nouveau.\n"
                "Les espaces avec une chance plus faible de gagner ont un multiplicateur de gains plus élevé.\n\n"
                "**⏱️ Temps restant**\n"
                "Chaque fois qu'un pari est placé, le temps restant est réinitialisé à 10 secondes, jusqu'à un maximum de 1 minute.\n\n"
                "**💸 Multiplicateurs de gains**\n"
                "[x36] Numéro seul\n"
                "[x3] Douzaines (1-12, 13-24, 25-36)\n"
                "[x3] Colonnes (1st, 2nd, 3rd)\n"
                "[x2] Moitiés (1-18, 19-36)\n"
                "[x2] Pair/Impair\n"
                "[x2] Couleurs (red, black)"
            ),
            color=discord.Color.gold()
        )
        help_embed.set_image(url="https://github.com/Iseyg91/Isey_aime_Cass/blob/main/unknown.png?raw=true")
        await interaction.response.send_message(embed=help_embed, ephemeral=True)

    help_button.callback = help_callback
    view.add_item(help_button)

    await ctx.send(embed=embed, view=view)
    await asyncio.sleep(10)

    # Résultat de la roulette
    spin_result = random.randint(0, 36)
    win = False
    multiplier = 0

    if space == "red" and spin_result in RED_NUMBERS:
        win, multiplier = True, 2
    elif space == "black" and spin_result in BLACK_NUMBERS:
        win, multiplier = True, 2
    elif space == "even" and spin_result in EVEN_NUMBERS:
        win, multiplier = True, 2
    elif space == "odd" and spin_result in ODD_NUMBERS:
        win, multiplier = True, 2
    elif space == "1-18" and 1 <= spin_result <= 18:
        win, multiplier = True, 2
    elif space == "19-36" and 19 <= spin_result <= 36:
        win, multiplier = True, 2
    elif space == "1st" and spin_result in COLUMN_1:
        win, multiplier = True, 3
    elif space == "2nd" and spin_result in COLUMN_2:
        win, multiplier = True, 3
    elif space == "3rd" and spin_result in COLUMN_3:
        win, multiplier = True, 3
    elif space == str(spin_result):
        win, multiplier = True, 36

    if win:
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": int(bet * multiplier)}}
        )
        result_str = f"The ball landed on: **{spin_result}**!\n\n**Winners:**\n{ctx.author.mention} won <:ecoEther:1341862366249357374> {int(bet * multiplier)}"
    else:
        result_str = f"The ball landed on: {spin_result}!\n\nNo Winners  :("

    await ctx.send(result_str)

    active_roulette_players.remove(user_id)

#-------------------------------------------------------------- Daily

@bot.hybrid_command(name="daily", aliases=["dy"], description="Réclame tes Coins quotidiens.")
async def daily(ctx: commands.Context):
    if ctx.guild is None:
        return await ctx.send("Cette commande ne peut être utilisée qu'en serveur.")
    
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    now = datetime.utcnow()

    cooldown_data = collection2.find_one({"guild_id": guild_id, "user_id": user_id})
    cooldown_duration = timedelta(hours=24)

    if cooldown_data and "last_claim" in cooldown_data:
        last_claim = cooldown_data["last_claim"]
        next_claim = last_claim + cooldown_duration

        if now < next_claim:
            remaining = next_claim - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            cooldown_embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> Vous devez attendre encore "
                            f"**{remaining.days * 24 + hours} heures, {minutes} minutes et {seconds} secondes** "
                            f"avant de pouvoir recevoir vos Coins quotidiens.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=cooldown_embed)

    # Génération du montant (retirer la décimale)
    amount = int(random.randint(600, 4500))

    # Récupération ou création du document utilisateur
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not user_data:
        user_data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
        collection.insert_one(user_data)

    # Mise à jour du solde
    old_cash = user_data["cash"]
    new_cash = old_cash + amount
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"cash": amount}}
    )

    # Mise à jour du cooldown
    collection2.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_claim": now}},
        upsert=True
    )

    # Embed de succès
    success_embed = discord.Embed(
        description=f"<:ecoEther:1341862366249357374> Vous avez reçu vos **{amount}** Coins quotidiens.\n"
                    f"Votre prochaine récompense sera disponible dans **24 heures**.",
        color=discord.Color.green()
    )
    await ctx.send(embed=success_embed)

    # Log
    await log_eco_channel(
        bot=bot,
        guild_id=guild_id,
        user=ctx.author,
        action="Récompense quotidienne",
        amount=amount,
        balance_before=old_cash,
        balance_after=new_cash,
        note="Commande /daily"
    )
    
#----------------------------------------------------- Leaderbaord

@bot.hybrid_command(
    name="leaderboard",
    aliases=["lb"],
    description="Affiche le classement des plus riches"
)
@app_commands.describe(sort="Choisir le critère de classement: 'cash' pour l'argent, 'bank' pour la banque, ou 'total' pour la somme des deux.")
@app_commands.choices(
    sort=[
        app_commands.Choice(name="Cash", value="cash"),
        app_commands.Choice(name="Banque", value="bank"),
        app_commands.Choice(name="Total", value="total")
    ]
)
async def leaderboard(
    ctx: commands.Context,
    sort: Optional[str] = "total"
):
    if ctx.guild is None:
        return await ctx.send("Cette commande ne peut être utilisée qu'en serveur.")

    guild_id = ctx.guild.id
    emoji_currency = "<:ecoEther:1341862366249357374>"
    bank_logo = "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/1344747420159967293.png?raw=true"

    # Détection du tri via arguments dans le message
    if isinstance(ctx, commands.Context) and ctx.message.content:
        content = ctx.message.content.lower()
        if "-cash" in content:
            sort = "cash"
        elif "-bank" in content:
            sort = "bank"
        else:
            sort = "total"

    if sort == "cash":
        sort_key = lambda u: u.get("cash", 0)
        title = f"Leaderboard - Cash"
    elif sort == "bank":
        sort_key = lambda u: u.get("bank", 0)
        title = f"Leaderboard - Banque"
    else:
        sort_key = lambda u: u.get("cash", 0) + u.get("bank", 0)
        title = f"Leaderboard - Total"

    all_users_data = list(collection.find({"guild_id": guild_id}))
    sorted_users = sorted(all_users_data, key=sort_key, reverse=True)

    page_size = 10
    total_pages = (len(sorted_users) + page_size - 1) // page_size

    def get_page(page_num: int):
        start_index = page_num * page_size
        end_index = start_index + page_size
        users_on_page = sorted_users[start_index:end_index]

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name="Leaderboard", icon_url=bank_logo)

        lines = []
        for i, user_data in enumerate(users_on_page, start=start_index + 1):
            user_id = user_data.get("user_id")
            if not user_id:
                continue
            user = ctx.guild.get_member(user_id)
            name = user.display_name if user else f"Utilisateur {user_id}"
            cash = user_data.get("cash", 0)
            bank = user_data.get("bank", 0)
            total = cash + bank

            # Formater les montants pour enlever les décimales
            if sort == "cash":
                amount = int(cash)
            elif sort == "bank":
                amount = int(bank)
            else:
                amount = int(total)

            line = f"{str(i).rjust(2)}. `{name}` • {emoji_currency} {amount:,}"
            lines.append(line)

        embed.add_field(name=title, value="\n".join(lines), inline=False)

        author_data = collection.find_one({"guild_id": guild_id, "user_id": ctx.author.id})
        user_rank = next((i + 1 for i, u in enumerate(sorted_users) if u["user_id"] == ctx.author.id), None)
        embed.set_footer(text=f"Page {page_num + 1}/{total_pages}  •  Ton rang: {user_rank}")
        return embed

    class LeaderboardView(View):
        def __init__(self, page_num):
            super().__init__(timeout=60)
            self.page_num = page_num

        @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.primary)
        async def previous_page(self, interaction: discord.Interaction, button: Button):
            if self.page_num > 0:
                self.page_num -= 1
                embed = get_page(self.page_num)
                await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.primary)
        async def next_page(self, interaction: discord.Interaction, button: Button):
            if self.page_num < total_pages - 1:
                self.page_num += 1
                embed = get_page(self.page_num)
                await interaction.response.edit_message(embed=embed, view=self)

    view = LeaderboardView(0)
    embed = get_page(0)
    await ctx.send(embed=embed, view=view)

#----------------------------------------------- Collect


@bot.hybrid_command(name="collect-income", aliases=["collect"])
async def collect_income(ctx: commands.Context):
    member = ctx.author
    guild = ctx.guild
    now = datetime.utcnow()
    collected = []
    cooldowns = []

    for config in COLLECT_ROLES_CONFIG:
        role = guild.get_role(config["role_id"])
        if role is None or config.get("auto", False):
            continue

        if role not in member.roles:
            continue

        # Check cooldown
        cd_data = collection5.find_one({
            "guild_id": guild.id,
            "user_id": member.id,
            "role_id": role.id
        })
        last_collect = cd_data.get("last_collect") if cd_data else None

        try:
            if last_collect:
                elapsed = (now - last_collect).total_seconds()
                if elapsed < config["cooldown"]:
                    remaining = config["cooldown"] - elapsed
                    cooldowns.append((remaining, role))
                    continue
        except Exception as e:
            print(f"[DEBUG] Erreur sur cooldown pour {role.name}: {e}")

        # Traitement eco
        eco_data = collection.find_one({
            "guild_id": guild.id,
            "user_id": member.id
        }) or {"guild_id": guild.id, "user_id": member.id, "cash": 1500, "bank": 0}

        amount = config.get("amount", 0)
        target = config.get("target", "cash")
        eco_data[target] = eco_data.get(target, 0) + amount

        collection.update_one(
            {"guild_id": guild.id, "user_id": member.id},
            {"$set": {target: eco_data[target]}},
            upsert=True
        )

        collection5.update_one(
            {"guild_id": guild.id, "user_id": member.id, "role_id": role.id},
            {"$set": {"last_collect": now}},
            upsert=True
        )

        collected.append(f"{role.mention} | <:ecoEther:1341862366249357374>**{amount}** ({target})")

        await log_eco_channel(
            bot, guild.id, member,
            f"Collect ({role.name})", amount, eco_data[target] - amount, eco_data[target],
            note=f"Collect manuel → {target}"
        )

    if collected:
        embed = discord.Embed(
            title=f"{member.display_name}",
            description="<:Check:1362710665663615147> Role income successfully collected!\n\n" + "\n".join(collected),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
        return

    if cooldowns:
        shortest = min(cooldowns, key=lambda x: x[0])
        remaining_minutes = int(shortest[0] // 60) or 1
        embed = discord.Embed(
            description=f"<:classic_x_mark:1362711858829725729> Tu as déjà collecté récemment ! Prochain collect dans **{remaining_minutes}min** (`{shortest[1].name}`)",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        description="❌ Tu n'as aucun rôle avec `collect` disponible.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

#------------------------------------------------------------------------- Commandes d'aide : +aide, /help
@bot.hybrid_command(name="help", description="Affiche l'aide économique pour Etherya Economie")
async def help(ctx: commands.Context):
    banner_url = "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/BANNER_ETHERYA-topaz.png?raw=true"  # URL de la bannière
    embed = discord.Embed(
        title="🏡 **Accueil Etherya Economie **",
        description=f"Hey, bienvenue {ctx.author.mention} sur la page d'accueil de Etherya Economie! 🎉\n\n"
                    "Ici, vous trouverez toutes les informations nécessaires pour comprendre l'économie efficacement. 🌟",
        color=discord.Color(0x1abc9c)
    )
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Développé avec ❤️ par Iseyg. Merci pour votre soutien !")
    embed.set_image(url=banner_url)  # Ajout de la bannière en bas de l'embed

    # Informations générales
    embed.add_field(name="📚 **Informations**", value=f"• **Mon préfixe** : !!\n• **Nombre de commandes** : 57", inline=False)

    # Création du menu déroulant
    select = discord.ui.Select(
        placeholder="Choisissez une catégorie 👇", 
        options=[
            discord.SelectOption(label="Jeux", description="🪙 Commandes pour jouer a l'économie", emoji="💸"),
            discord.SelectOption(label="Items & Badges", description="📦Commandes pour accéder aux Items & Badges", emoji="🛒"),
            discord.SelectOption(label="Pouvoir", description="🌊Commandes pour attaquer d'autre joueur ou encore se défendre ", emoji="🪭"),
            discord.SelectOption(label="Guild", description="📍Commande pour gérer votre Guild", emoji="🪄"),
            discord.SelectOption(label="Crédits", description="💖 Remerciements et crédits", emoji="🙏")
        ], 
        custom_id="help_select"
    )

    # Définir la méthode pour gérer l'interaction du menu déroulant
    async def on_select(interaction: discord.Interaction):
        category = interaction.data['values'][0]
        new_embed = discord.Embed(color=discord.Color(0x1abc9c))
        new_embed.set_image(url=banner_url)  # Ajout de la bannière dans chaque catégorie
        if category == "Jeux":
            new_embed.title = "💴 **Commandes pour jouer a l'économie**"
            new_embed.description = "Bienvenue dans la section Economie !"
            new_embed.add_field(name="💰 !!bal", value="Affiche ton solde actuel en **cash**,**bank** et **total**.", inline=False)
            new_embed.add_field(name="🏹 !!dy", value="Récupère une **somme quotidienne**.", inline=False)
            new_embed.add_field(name="🍀 !!collect", value="Récupère des Coins.", inline=False)
            new_embed.add_field(name="💼 !!work", value="Travaille pour gagner de l'argent !", inline=False)
            new_embed.add_field(name="💥 !!slut", value="Comettre un **slut** pour gagner de l'argent ou risquer une amende.", inline=False)
            new_embed.add_field(name="🚨 !!crime", value="Comettre un **crime** pour gagner de l'argent ou risquer une amende.", inline=False)
            new_embed.add_field(name="🏆 !!lb (-cash, -bank)", value="Affiche le **classement** des joueurs avec leur cash, banque ou encore en total.", inline=False)
            new_embed.add_field(name="💥 !!rob <@user>", value="Tente de **voler** un autre utilisateur (risque d'échec).", inline=False)
            new_embed.add_field(name="💸 !!with <amount>", value="Retire une certaine somme d'argent de la **banque**.", inline=False)
            new_embed.add_field(name="💳 !!dep <amount>", value="Dépose une certaine somme d'argent dans ta **banque**.", inline=False)
            new_embed.add_field(name="🛍 !!buy c", value="Achat d'**un chicken** pour jouer au cf.", inline=False)
            new_embed.add_field(name="🎲 !!cf <amount>", value="Joue au **chicken fight*** avec un certain montant.", inline=False)
            new_embed.add_field(name="🍒 !!bj <amount>", value="Joue au **blackjack** avec une certaine somme.", inline=False)
            new_embed.add_field(name="🎰 !!rr <amount>", value="Joue à la **roulette russe** avec une certaine somme.", inline=False)
            new_embed.add_field(name="💸 !!roulette <amount> <space>", value="Mise à la **roulette** avec un certain montant.", inline=False)
            new_embed.add_field(name="💰 !!pay <@user> <amount>", value="Envoie de l'argent à un autre utilisateur.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Items & Badges":
            new_embed.title = "📦 **Commandes pour accéder aux Items & Badges**"
            new_embed.description = "Bienvenue dans la section Items & Badges !"
            new_embed.add_field(name="🛒 /item-store", value="Accède au **magasin d'items** pour acheter des objets.", inline=False)
            new_embed.add_field(name="📜 /item-info", value="Affiche les **détails** d'un item spécifique.", inline=False)
            new_embed.add_field(name="💸 /item-buy", value="Permet d'acheter un item en utilisant ton solde.", inline=False)
            new_embed.add_field(name="💰 /item-sell", value="Permet de **vendre** un item de ton inventaire à un autre joueur.", inline=False)
            new_embed.add_field(name="📦 /item-inventory", value="Affiche les items que tu possèdes dans ton **inventaire**.", inline=False)
            new_embed.add_field(name="⚡️ /item-use", value="Utilise un item de ton inventaire pour activer ses effets.", inline=False)
            new_embed.add_field(name="🏆 /item-leaderboard", value="Affiche le **classement** des joueurs de l'items spécifié.", inline=False)
            new_embed.add_field(name="🎖 /badge-store", value="Accède au **musée de badges** pour voir les badges uniques.", inline=False)
            new_embed.add_field(name="🎖 /badge-inventory", value="Affiche les badges que tu possèdes dans ton inventaire.", inline=False)
            new_embed.add_field(name="🏅 /rewards", value="Récupère une **récompense quotidienne**.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Pouvoir":
            new_embed.title = "🗃️ **Commandes pour attaquer d'autre joueur ou encore se défendre**"
            new_embed.description = "Bienvenue dans la section Pouvoir !"
            new_embed.add_field(name="!!nen", value="Cet objet permet d'utiliser le Nen aléatoirement, avec un serment pour chaque technique. La spécialisation est inaccessible.", inline=False)
            new_embed.add_field(name="!!renforcement", value="Offre à son utilisateur un anti-rob de 24h grâce a un serment de nen mais ne peux pas le refaire pendant 1 semaine.", inline=False)
            new_embed.add_field(name="!!emission <@user>", value="Maudit quelqu'un grâce a son propre nen et lui offre un collect de -20% (cooldown 1 semaine)", inline=False)
            new_embed.add_field(name="!!manipulation", value="Manipule sa propre banque et offre un collect de 1% toutes les 4h pendant 24h (cooldown 1 semaines)", inline=False)
            new_embed.add_field(name="!!matérialisation", value="Matérialise un objet aléatoire de la boutique (sauf exception) (tous les mois)", inline=False)
            new_embed.add_field(name="!!transformation <@user>", value="Permet de transformer son aura en éclair et FOUDROYER la banque de quelqu'un est de lui retirer 25% de celle-ci (cooldown : 2 semaines)", inline=False)
            new_embed.add_field(name="!!heal", value="Permet de retirer le nen que quelqu'un nous a poser grâce à un exorciste !", inline=False)
            new_embed.add_field(name="!!imperial <@user>", value="Permet d'utiliser le démon dans votre arme et vous permet de voler votre adversaire", inline=False)
            new_embed.add_field(name="!!haki <@user>", value="Paralyse ainsi il n’aura pas accès aux salons économiques.", inline=False)
            new_embed.add_field(name="!!ultra", value="Vous activez l'Ultra Instinct ultime, esquivant toutes les attaques pendant (temps d'immunité). Après utilisation, 5 jours de repos sont nécessaires pour le réutiliser.", inline=False)
            new_embed.add_field(name="!!berserk <@user>", value="Berserk te consume, tu détruis sans gain. Roll 100 : cible perd tout, tu obtiens 'L'incarnation de la Rage'. Roll ≤ 10 : perds 15% de ta banque. 7 jours de cooldown.", inline=False)
            new_embed.add_field(name="!!armure", value="Offre une protection anti-rob de 1h. L'armure s'auto-consomme après l'utilisation.", inline=False)
            new_embed.add_field(name="!!infini", value="Vous donne un anti-rob", inline=False)
            new_embed.add_field(name="!!pokeball <@user>", value="Permet de voler un objet aléatoire à une personne ciblé, ou d'obtenir rien.", inline=False)
            new_embed.add_field(name="!!float", value="Accès au salon <#1355158032195256491> pendant 15 minutes, utilisable une fois par jour", inline=False)
            new_embed.add_field(name="!!oeil", value="Voir l'avenir et entrevoir le prochain restock pendant 10 sec, cooldown de 1 semaine.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Guild":
            new_embed.title = "🛡️**Commandes pour gérer votre Guild**"
            new_embed.description = "Bienvenue dans la section Guild !"
            new_embed.add_field(name="!!gcreate", value="Crée une guild. Coût : 5000 coins.", inline=False)
            new_embed.add_field(name="!!g", value="Affiche les informations de votre guild.", inline=False)
            new_embed.add_field(name="!!cdep <amount>", value="Dépose des coins dans le coffre-fort de la guild. Accès restreint.", inline=False)
            new_embed.add_field(name="!!cwith <amount>", value="Retire des coins du coffre-fort de la guild. Accès restreint.", inline=False)
            new_embed.add_field(name="!!gban <@user>", value="Bannit un membre de la guild (empêche de la rejoindre à nouveau).", inline=False)
            new_embed.add_field(name="!!gdelete <guildid>", value="Supprime définitivement une guild (admin only).", inline=False)
            new_embed.add_field(name="!!gdep <amount/all>", value="Dépose des coins dans la banque de la guild.", inline=False)
            new_embed.add_field(name="!!gkick <@user>", value="Expulse un membre de la guild.", inline=False)
            new_embed.add_field(name="!!gleave", value="Quitte la guild actuelle.", inline=False)
            new_embed.add_field(name="!!gowner <@user>", value="Transfère la propriété de la guild à un autre membre.", inline=False)
            new_embed.add_field(name="!!gunban <@user>", value="Débannit un ancien membre, lui permettant de rejoindre à nouveau la guild.", inline=False)
            new_embed.add_field(name="!!gwith <amount>", value="Retire des coins de la banque de la guild.", inline=False)
            new_embed.add_field(name="/dep-guild-inventory", value="Dépose un item de votre inventaire personnel dans celui de votre guild.", inline=False)
            new_embed.add_field(name="/with-guild-inventory", value="Retire un item de l'inventaire de votre guild vers le vôtre.", inline=False)
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

#--------------------------------------------------- COMMANDE ROLL
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
            label="📩 Inviter Project Delta",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1356693934012891176"
        )
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)

        end_time = time.time()
        print(f"Commande `getbotinfo` exécutée en {round((end_time - start_time) * 1000, 2)}ms")

    except Exception as e:
        print(f"Erreur dans la commande `getbotinfo` : {e}")

# Définition des symboles
symbols = {
    'delta': "<:delta_jeton:1365410293206880296>",
    'alpha': "<:alpha_jeton:1365410328363667599>",
    'beta': "<:beta_jeton:1365410310860705863>"
}

# Fonction pour obtenir ou créer les données de l'utilisateur
def get_or_create_user_data(guild_id, user_id):
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data:
        data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
        collection.insert_one(data)
    return data

# Mise à jour de la balance du joueur
async def update_balance(guild_id, user_id, amount):
    data = get_or_create_user_data(guild_id, user_id)
    new_cash = data['cash'] + amount
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"cash": new_cash}}
    )
    return new_cash

# Fonction principale de la machine à sous
async def slot_machine(ctx, bet):
    if bet < 1 or bet > 5000:
        await ctx.send("La mise doit être entre 1 et 5000.")
        return

    data = get_or_create_user_data(ctx.guild.id, ctx.author.id)
    cash = data.get("cash", 0)

    if bet > cash:
        await ctx.send("Vous n'avez pas assez d'argent pour jouer à cette mise.")
        return

    reels = [random.choice(list(symbols.values())) for _ in range(9)]
    lines = [
        "|".join(reels[0:3]),
        "|".join(reels[3:6]),
        "|".join(reels[6:9])
    ]

    if lines[1] == "|".join([symbols['delta']] * 3):
        win_amount = bet * 3
        color = discord.Color.green()
        description = f"**You won** <:ecoEther:1341862366249357374> {win_amount:,}!"
    elif lines[1] == "|".join([symbols['alpha']] * 3):
        win_amount = bet * 2
        color = discord.Color.green()
        description = f"**You won** <:ecoEther:1341862366249357374> {win_amount:,}!"
    elif lines[1] == "|".join([symbols['beta']] * 3):
        win_amount = bet * 1
        color = discord.Color.green()
        description = f"**You won** <:ecoEther:1341862366249357374> {win_amount:,}!"
    else:
        win_amount = -bet
        color = discord.Color.red()
        description = f"**You lost** <:ecoEther:1341862366249357374> {bet:,}!"

    await update_balance(ctx.guild.id, ctx.author.id, win_amount)

    embed = discord.Embed(color=color)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.description = description

    embed.add_field(
        name="\u200b",  # Champ sans titre
        value=f"{lines[0]}\n{lines[1]} <:emoji_14:1365415542466281593>\n{lines[2]}"
    )

    await ctx.send(embed=embed)

# Commande pour jouer à la machine à sous
@bot.hybrid_command(name="slot-machine", aliases=["sm"], description="Jouer à la machine à sous.")
async def slot(ctx, bet: int):
    await slot_machine(ctx, bet)

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
