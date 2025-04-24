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

token = os.environ['ETHERYA']
intents = discord.Intents.all()
start_time = time.time()
bot = commands.Bot(command_prefix="!!", intents=intents, help_command=None)

#Configuration du Bot:
# --- ID Owner Bot ---
ISEY_ID = 792755123587645461
# Définir GUILD_ID
GUILD_ID = 1034007767050104892

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
collection16 = db['ether_boutique'] #Stock les Items dans la boutique
collection17 = db['joueur_ether_inventaire'] #Stock les items de joueurs
collection18 = db['ether_effects'] #Stock les effets
collection19 = db['ether_badge'] #Stock les bagde
collection20 = db['inventaire_badge'] #Stock les bagde des joueurs
collection21 = db['daily_badge'] #Stock les cd des daily badge
collection22 = db['start_date'] #Stock la date de commencemant des rewards
collection23 = db['joueur_rewards'] #Stock ou les joueurs sont
collection24 = db['cd_renforcement'] #Stock les cd
collection25 = db['cd_emission'] #Stock les cd
collection26 = db['cd_manipulation'] #Stock les cd
collection27 = db['cd_materialisation'] #Stock les cd
collection28 = db['cd_transformation'] #Stock les cd
collection29 = db['cd_specialisation'] #Stock les cd
collection30 = db['cd_haki_attaque'] #Stock les cd
collection31 = db['cd_haki_subis'] #Stock les cd
collection32 = db['ether_quetes'] #Stock les quetes
collection33 = db['inventory_collect'] #Stock les items de quetes
collection34 = db['collect_items'] #Stock les items collector
collection35 = db['ether_guild'] #Stock les Guild
collection36 = db['guild_inventaire'] #Stock les inventaire de Guild


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
    ether_boutique_data = collection16.find_one({"guild_id": guild_id}) or {}
    joueur_ether_inventaire_data = collection17.find_one({"guild_id": guild_id}) or {}
    ether_effects_data = collection18.find_one({"guild_id": guild_id}) or {}
    ether_badge_data = collection19.find_one({"guild_id": guild_id}) or {}
    inventaire_badge_data = collection20.find_one({"guild_id": guild_id}) or {}
    daily_badge_data = collection21.find_one({"guild_id": guild_id}) or {}
    start_date_data = collection22.find_one({"guild_id": guild_id}) or {}
    joueur_rewards_data = collection23.find_one({"guild_id": guild_id}) or {}
    cd_renforcement_data = collection24.find_one({"guild_id": guild_id}) or {}
    cd_emission_data = collection25.find_one({"guild_id": guild_id}) or {}
    cd_manipultation_data = collection26.find_one({"guild_id": guild_id}) or {}
    cd_materialisation_data = collection27.find_one({"guidl_id": guild_id}) or {}
    cd_transformation_data = collection28.find_one({"guild_id": guild_id}) or {}
    cd_specialisation_data = collection29.find_one({"guild_id": guild_id}) or {}
    cd_haki_attaque_data = collection30.find_one({"guild_id": guild_id}) or {}
    cd_haki_subis_data = collection31.find_one({"guild_id": guild_id}) or {}
    ether_quetes_data = collection32.find_one({"guild_id": guild_id}) or {}
    inventory_collect_data = collection33.find_one({"guild_id": guild_id}) or {}
    collect_items_data = collection34.find_one({"guild_id": guild_id}) or {}
    ether_guild_data = collection35.find_one({"guild_id": guild_id}) or {}
    guild_inventaire_data = collection36.find_one({"guild_id": guild_id}) or {}

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
        "ether_boutique": ether_boutique_data,
        "joueur_ether_inventaire": joueur_ether_inventaire_data,
        "ether_effects": ether_effects_data,
        "ether_badge": ether_badge_data,
        "inventaire_badge": inventaire_badge_data,
        "daily_badge": daily_badge_data,
        "start_date": start_date_data,
        "joueur_rewards": joueur_rewards_data,
        "cd_renforcement": cd_renforcement_data,
        "cd_emission": cd_emission_data,
        "cd_manipultation": cd_manipultation_data,
        "cd_materialisation": cd_materialisation_data,
        "cd_transformation" : cd_transformation_data,
        "cd_specialisation" : cd_specialisation_data,
        "cd_haki_attaque": cd_haki_attaque_data,
        "cd_haki_subis": cd_haki_subis_data,
        "ether_quetes": ether_quetes_data,
        "inventory_collect": inventory_collect_data,
        "collect_items": collect_items_data,
        "ether_guild": ether_guild_data,
        "guild_inventaire": guild_inventaire

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

# === CONFIGURATION DES RÉCOMPENSES PAR JOUR ===
daily_rewards = {
    1: {"coins": 1000, "badge": None, "item": None, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.1.png?raw=true"},
    2: {"coins": 2000, "badge": None, "item": None, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.2.png?raw=true"},
    3: {"coins": 3000, "badge": 2, "item": None, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.3.png?raw=true"},
    4: {"coins": 4000, "badge": None, "item": None, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.4.png?raw=true"},
    5: {"coins": 5000, "badge": None, "item": 1, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.5.png?raw=true"},
    6: {"coins": 6000, "badge": None, "item": None, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.6.png?raw=true"},
    7: {"coins": 7000, "badge": 1, "item": None, "image_url": "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20SEASON/image.7.png?raw=true"}
}

TOP_ROLES = {
    1: 1363923497885237298,  # ID du rôle Top 1
    2: 1363923494504501510,  # ID du rôle Top 2
    3: 1363923356688056401,  # ID du rôle Top 3
}

# Config des rôles
COLLECT_ROLES_CONFIG = [
    {
        "role_id": 1355157715550470335,
        "amount": 250,
        "cooldown": 3600,
        "auto": False,
        "target": "bank"  # ou "bank"
    },
    {
        "role_id": 1363969965572755537,
        "percent": -20,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1363974710739861676,
        "percent": 1,
        "cooldown": 3600,
        "auto": True,
        "target": "bank"
    },
    {
        "role_id": 1363948445282341135,
        "amount": 5000,
        "cooldown": 7200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157729362313308,
        "amount": 500,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157728024072395,
        "amount": 1000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157726032035881,
        "amount": 1500,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157725046243501,
        "amount": 2000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157723960049787,
        "amount": 2500,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157722907279380,
        "amount": 3000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157721812435077 ,
        "amount": 3500,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    },
    {
        "role_id": 1355157720730439701  ,
        "amount": 4000,
        "cooldown": 14200,
        "auto": False,
        "target": "bank"
    }
]

# --- Boucle Auto Collect ---
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
                        # Assurez-vous que 'cash' et 'bank' existent
                        eco_data = collection.find_one({
                            "guild_id": guild.id,
                            "user_id": member.id
                        }) or {"guild_id": guild.id, "user_id": member.id, "cash": 1500, "bank": 0}

                        # Si 'cash' ou 'bank' n'existe pas, les initialiser à 0
                        if "cash" not in eco_data:
                            eco_data["cash"] = 0
                        if "bank" not in eco_data:
                            eco_data["bank"] = 0

                        before = eco_data[config["target"]]  # "cash" ou "bank"

                        if "amount" in config:
                            eco_data[config["target"]] += config["amount"]
                        elif "percent" in config:
                            eco_data[config["target"]] += eco_data[config["target"]] * (config["percent"] / 100)

                        # Mise à jour de la base de données
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

# --- Boucle Top Roles ---
@tasks.loop(seconds=5)
async def update_top_roles():
    for guild in bot.guilds:
        all_users_data = list(collection.find({"guild_id": guild.id}))
        sorted_users = sorted(
            all_users_data,
            key=lambda u: u.get("cash", 0) + u.get("bank", 0),
            reverse=True
        )
        top_users = sorted_users[:3]

        for rank, user_data in enumerate(top_users, start=1):
            user_id = user_data["user_id"]
            role_id = TOP_ROLES[rank]
            role = discord.utils.get(guild.roles, id=role_id)
            if not role:
                print(f"Rôle manquant : {role_id} dans {guild.name}")
                continue

            try:
                member = await guild.fetch_member(user_id)
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

# --- Événement on_ready ---
@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté.")

    if not update_top_roles.is_running():
        update_top_roles.start()
    if not auto_collect_loop.is_running():
        auto_collect_loop.start()

    print(f"✅ Le bot {bot.user} est maintenant connecté ! (ID: {bot.user.id})")

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

@bot.event
async def on_message(message):
    # Ignorer les messages du bot lui-même
    if message.author.bot:
        return

    # Obtenir les informations de l'utilisateur
    user = message.author
    guild_id = message.guild.id
    user_id = user.id

    # Générer un montant aléatoire entre 5 et 20 coins
    coins_to_add = random.randint(5, 20)

    # Ajouter les coins au portefeuille de l'utilisateur
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"wallet": coins_to_add}},
        upsert=True
    )

    # Appeler le traitement habituel des commandes
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
        if not amount.isdigit():
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, montant invalide. Utilise un nombre ou `all`.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

        deposit_amount = int(amount)

        if deposit_amount <= 0:
            embed = discord.Embed(
                description=f"<:classic_x_mark:1362711858829725729> {user.mention}, tu dois déposer un montant supérieur à zéro.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

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
        if not amount.isdigit():
            embed = discord.Embed(
                description="❌ Montant invalide. Utilise un nombre ou `all`.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

        withdrawn_amount = int(amount)

        if withdrawn_amount <= 0:
            embed = discord.Embed(
                description="❌ Tu dois retirer un montant supérieur à zéro.",
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            return await ctx.send(embed=embed)

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

    # Vérifie le solde actuel
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0, "bank": 0}
    current_balance = int(data.get(field, 0))

    if current_balance < amount:
        return await ctx.send(
            f"❌ {user.display_name} n'a pas assez de fonds dans son `{field}` pour retirer {int(amount):,} <:ecoEther:1341862366249357374>."
        )

    balance_before = current_balance
    balance_after = balance_before - amount

    # Mise à jour dans la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {field: -amount}},
        upsert=True
    )

    # Log dans le salon de logs économique
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

    # Embed de confirmation
    embed = discord.Embed(
        title="✅ Retrait effectué avec succès !",
        description=f"**{int(amount):,} <:ecoEther:1341862366249357374>** a été retiré de la **{field}** de {user.mention}.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs de permissions
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

from datetime import datetime, timedelta
import random
import discord
from discord.ext import commands

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

    if outcome == "gain":
        messages = [
            f"<:Check:1362710665663615147> Tu as séduit la bonne personne et reçu **{amount_gain:.1f} <:ecoEther:1341862366249357374>** en cadeau.",
            f"<:Check:1362710665663615147> Une nuit torride t’a valu **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tu as été payé pour tes charmes : **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Ta prestation a fait des ravages, tu gagnes **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Ce client généreux t’a offert **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tu as chauffé la salle et récolté **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tes talents ont été récompensés avec **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:Check:1362710665663615147> Tu as dominé la scène, et gagné **{amount_gain:.1f} <:ecoEther:1341862366249357374>**.",
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
            f"<:classic_x_mark:1362711858829725729> Ton plan a échoué, tu perds **{amount_loss:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Ton client a disparu sans payer. Tu perds **{amount_loss:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> T’as glissé pendant ton show… Résultat : **{amount_loss:.1f} <:ecoEther:1341862366249357374>** de frais médicaux.",
            f"<:classic_x_mark:1362711858829725729> Mauvais choix de client, il t’a volé **{amount_loss:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Une nuit sans succès… Tu perds **{amount_loss:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Ton charme n’a pas opéré… Pertes : **{amount_loss:.1f} <:ecoEther:1341862366249357374>**.",
            f"<:classic_x_mark:1362711858829725729> Tu as été arnaqué par un faux manager. Tu perds **{amount_loss:.1f} <:ecoEther:1341862366249357374>**.",
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

    if outcome == "gain":
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

    # Calcul de la chance de victoire
    win_data = collection6.find_one({"guild_id": guild_id, "user_id": user_id})
    win_chance = win_data.get("win_chance") if win_data and "win_chance" in win_data else start_chance

    # Résultat du combat
    if random.randint(1, 100) <= win_chance:
        win_amount = amount
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": win_amount}},
            upsert=True
        )
        new_chance = min(win_chance + 1, max_chance)
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"win_chance": new_chance}},
            upsert=True
        )

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
            {"$set": {"win_chance": start_chance}},
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
            embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
            embed.add_field(name="🧑 Ta main", value=" ".join([card_emojis[c][0] for c in self.player_hand]) + f"\n**Total : {calculate_hand_value(self.player_hand)}**", inline=False)
            embed.add_field(name="🤖 Main du croupier", value=f"{card_emojis[self.dealer_hand[0]][0]} 🂠", inline=False)
            embed.add_field(name="💰 Mise", value=f"{int(self.bet)} <:ecoEther:1341862366249357374>", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)

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

        if result == "win":
            self.player_data["cash"] += int(self.bet * 2)  # Mise doublée sans décimale
            message = f"<:Check:1362710665663615147> Tu as **gagné** !"
            color = discord.Color.green()
        elif result == "draw":
            self.player_data["cash"] += int(self.bet)  # Mise sans décimale
            message = f"<:Check:1362710665663615147> Égalité !"
            color = discord.Color.gold()
        else:
            message = f"<:classic_x_mark:1362711858829725729> Tu as **perdu**..."
            color = discord.Color.red()

        # Mise à jour dans la DB
        collection.update_one(
            {"guild_id": self.guild_id, "user_id": self.user_id},
            {"$set": {"cash": self.player_data["cash"]}}
        )

        embed = discord.Embed(title="🃏 Résultat du Blackjack", color=color)
        embed.add_field(name="🧑 Ta main", value=" ".join([card_emojis[c][0] for c in self.player_hand]) + f"\n**Total : {player_total}**", inline=False)
        embed.add_field(name="🤖 Main du croupier", value=" ".join([card_emojis[c][0] for c in self.dealer_hand]) + f"\n**Total : {dealer_total}**", inline=False)
        embed.add_field(name="💰 Mise", value=f"{int(self.bet)} <:ecoEther:1341862366249357374>", inline=False)
        embed.add_field(name="Résultat", value=message, inline=False)

        await interaction.response.edit_message(embed=embed, view=None)

# Lorsqu'un joueur joue au blackjack
@bot.hybrid_command(name="blackjack", aliases=["bj"], description="Joue au blackjack et tente de gagner !")
async def blackjack(ctx: commands.Context, mise: str = None):
    if ctx.guild is None:
        return await ctx.send(embed=discord.Embed(description="Cette commande ne peut être utilisée qu'en serveur.", color=discord.Color.red()))

    if mise == "all":
        user_data = get_or_create_user_data(ctx.guild.id, ctx.author.id)
        max_bet = 5000  # La mise maximale

        if user_data["cash"] <= max_bet:
            mise = user_data["cash"]  # Mise toute la somme disponible
        else:
            return await ctx.send(embed=discord.Embed(description=f"Ton solde est trop élevé pour miser tout, la mise maximale est de {max_bet} <:ecoEther:1341862366249357374>.", color=discord.Color.red()))

    elif mise == "half":
        user_data = get_or_create_user_data(ctx.guild.id, ctx.author.id)
        max_bet = 15000  # La mise maximale
        half_cash = user_data["cash"] // 2

        if half_cash > max_bet:
            return await ctx.send(embed=discord.Embed(description=f"La moitié de ton solde est trop élevée, la mise maximale est de {max_bet} <:ecoEther:1341862366249357374>.", color=discord.Color.red()))
        else:
            mise = half_cash

    elif mise:
        mise = int(mise)
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
    
    if mise is None:
        return await ctx.send(embed=discord.Embed(description="Tu dois spécifier une mise, ou utiliser `all` ou `half` pour miser tout ou la moitié de ton solde.", color=discord.Color.red()))

    user_data["cash"] -= mise
    collection.update_one(
        {"guild_id": ctx.guild.id, "user_id": ctx.author.id},
        {"$set": {"cash": user_data["cash"]}}
    )

    player_hand = [draw_card()[0] for _ in range(2)]
    dealer_hand = [draw_card()[0] for _ in range(2)]

    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
    embed.add_field(name="🧑 Ta main", value=" ".join([card_emojis[c][0] for c in player_hand]) + f"\n**Total : {calculate_hand_value(player_hand)}**", inline=False)
    embed.add_field(name="🤖 Main du croupier", value=f"{card_emojis[dealer_hand[0]][0]} 🂠 **Cartes visibles : {dealer_cards_count(dealer_hand)}**", inline=False)
    embed.add_field(name="💰 Mise", value=f"{int(mise)} <:ecoEther:1341862366249357374>", inline=False)
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

from datetime import datetime, timedelta

@bot.hybrid_command(name="rob", description="Voler entre 1% et 50% du portefeuille d'un autre utilisateur.")
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

    # Role protection
    target_member = ctx.guild.get_member(target_id)
    if not target_member:
        return await ctx.send(embed=discord.Embed(
            description=f"Utilisateur introuvable sur ce serveur.",
            color=discord.Color.red()
        ))

    anti_rob_data = collection15.find_one({"guild_id": guild_id}) or {"roles": []}
    if any(role.name in anti_rob_data["roles"] for role in target_member.roles):
        return await ctx.send(embed=discord.Embed(
            description=f"{user.display_name} est protégé contre le vol.",
            color=discord.Color.red()
        ))

    # Get data
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 1500, "bank": 0}
    target_data = collection.find_one({"guild_id": guild_id, "user_id": target_id}) or {"cash": 1500, "bank": 0}
    collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$setOnInsert": user_data}, upsert=True)
    collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$setOnInsert": target_data}, upsert=True)

    if target_data["cash"] <= 0:
        return await ctx.send(embed=discord.Embed(
            description=f"{user.display_name} n’a pas de monnaie à voler.",
            color=discord.Color.red()
        ))

    # Success calculation
    robber_total = user_data["cash"] + user_data["bank"]
    rob_chance = max(80 - (robber_total // 1000), 10)
    success = random.randint(1, 100) <= rob_chance

    collection14.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_rob": datetime.utcnow()}},
        upsert=True
    )

    if success:
        percentage = random.randint(1, 50)
        stolen = (percentage / 100) * target_data["cash"]
        stolen = round(stolen, 2)
        stolen = min(stolen, target_data["cash"])

        collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"cash": stolen}})
        collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$inc": {"cash": -stolen}})

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

    if arg.isdigit() or arg.lower() == "all" or arg.lower() == "half":
        if arg.lower() == "all":
            bet = get_user_cash(guild_id, user.id)
        elif arg.lower() == "half":
            bet = get_user_cash(guild_id, user.id) // 2
        else:
            bet = int(arg)

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
        title=ctx.author.name,  # ou interaction.user.name selon ton contexte
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

    spin_result = random.randint(0, 36)
    win = False
    multiplier = 0

    # Vérification du pari
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

    # Message de gain ou de perte
    if win:
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"cash": int(bet * multiplier)}},
        )
        result_str = f"The ball landed on: **{spin_result}**!\n\n**Winners:**\n{ctx.author.mention} won <:ecoEther:1341862366249357374> {int(bet * multiplier)}"
    else:
        result_str = f"The ball landed on: {spin_result}!\n\nNo Winners  :("

    await ctx.send(result_str)

    # Libération du joueur
    active_roulette_players.remove(user_id)

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

from discord import app_commands
from typing import Optional
import discord
from discord.ext import commands
from discord.ui import Button, View

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

import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
import asyncio
from datetime import datetime, timedelta

ITEMS = [
    {
        "id": 8,
        "emoji": "<:infini:1363615903404785734>",
        "title": "Infini | ℕ𝕀𝕍𝔼𝔸𝕌 𝟙",
        "description": "L'infini protège des robs pendant 1h (utilisable 1 fois par items)",
        "price": 25000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 3,
        "tradeable": True,
        "usable": True,
        "use_effect": "L'infini protège des robs pendant 1h ",
        "requirements": {},
        "role_id": 1363939565336920084,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 66,
        "emoji": "<:exorciste:1363602480792994003>",
        "title": "Appel à un exorciste | 𝕊𝕆𝕀ℕ",
        "description": "Permet de retirer le nen que quelqu'un nous a posé grâce à un exorciste !",
        "price": 50000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 5,
        "tradeable": True,
        "usable": True,
        "use_effect": "Retire le rôle, faite !!heal",
        "requirements": {},
        "role_id": 1363873859912335400,
        "role_duration": 3600,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True,
        "remove_role_after_use": True
    },
    {
        "id": 88,
        "emoji": "<:infini:1363615925776941107>",
        "title": "Infini | ℕ𝕀𝕍𝔼𝔸𝕌 𝟚",
        "description": "L'infini protège des robs pendant 3h (utilisable 1 fois par items)",
        "price": 50000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "L'infini protège des robs pendant 3h ",
        "requirements": {},
        "role_id": 1363939567627145660,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 81,
        "emoji": "<:armure:1363599057863311412>",
        "title": "Armure du Berserker",
        "description": "Offre à son utilisateur un anti-rob de 1h... (voir description complète)",
        "price": 100000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 3,
        "tradeable": True,
        "usable": True,
        "use_effect": "L'infini protège des robs pendant 1h",
        "requirements": {},
        "role_id": 1363821649002238142,
        "role_duration": 3600,
        "remove_after_purchase": {
            "roles": True,
            "items": False
        }
    },
    {
        "id": 31,
        "emoji": "<:demoncontrole:1363600359611695344>",
        "title": "Contrôle de démon",
        "description": "Donne accès a tous les équipements de contrôle des démons",
        "price": 100000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 3,
        "tradeable": True,
        "usable": True,
        "use_effect": "Donne accès a tous les équipements de contrôle des démons",
        "requirements": {},
        "role_id": 1363817629781069907,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 888,
        "emoji": "<:infini:1363615948090638490>",
        "title": "Infini | ℕ𝕀𝕍𝔼𝔸𝕌 𝟛",
        "description": "L'infini protège des robs pendant 6h (utilisable 1 fois par items)",
        "price": 100000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 1,
        "tradeable": True,
        "usable": True,
        "use_effect": "L'infini protège des robs pendant 3h",
        "requirements": {},
        "role_id": 1363939486844850388,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 91,
        "emoji": "<:oeildemoniaque:1363947226501484746>",
        "title": "Œil démoniaque",
        "description": "Permet de voir l'avenir grâce au pouvoir de Kishirika...",
        "price": 100000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "Permet de visioner le prochain restock pendant 10 seconde",
        "requirements": {},
        "role_id": 1363949082653098094,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 7,
        "emoji": "<:licence:1363609202211422268>",
        "title": "Licence Hunter ",
        "description": "Donne accès a toutes les techniques De Hunter x Hunter, plus donne accès a un salon avec des quêtes",
        "price": 250000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 1,
        "tradeable": True,
        "usable": True,
        "use_effect": "Donne le rôle licence hunter et donne accès au nen et au quêtes destiné au hunter",
        "requirements": {},
        "role_id": 1363817603713339512,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 4,
        "emoji": "<:naturoermite:1363945371448905810>",
        "title": "Mode Ermite",
        "description": "Ce mode autrefois maîtrisé par Naruto lui même, il vous confère l’énergie de la nature. Grâce à cela, vous pourrez avoir plus d’ezryn !!!",
        "price": 250000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "Vous donne un collect qui vous donne 5,000 <:ecoEther:1341862366249357374> toute les 2 heures",
        "requirements": {},
        "role_id": 1363948445282341135,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 15,
        "emoji": "<:nen:1363607663010775300>",
        "title": "Nen | ℝ𝕆𝕃𝕃",
        "description": "Cet objet vous permet d'utiliser le Nen (le nen vous est donné aléatoirement) comme vous le souhaitez. Chaque technique utilise un serment de nen. *(La spécialisation n’y figure pas car vous n’êtes pas assez fort lol)*\n\n__**Renforcement :**__\n**+renforcement** : Offre à son utilisateur un anti-rob de 24h, mais ne peut pas le refaire pendant 1 semaine.\n\n__**Émission :**__\n**+emission @user** : Maudit quelqu’un grâce à son propre nen et lui inflige un collect de -20% *(cooldown : 1 semaine)*.\n\n__**Manipulation :**__\n**+manipulation** : Manipule sa propre banque et offre un collect de 1% toutes les 4h pendant 24h *(cooldown : 1 semaine)*.\n\n__**Matérialisation :**__\n**+materialisation** : Matérialise un objet aléatoire de la boutique *(cooldown : 2 sem)*.\n\n__**Transformation :**__\n**+transformation** : Permet de transformer son aura et **FOUDROYER** la banque de quelqu’un, retirant 25% de celle-ci *(cooldown : 2 semaines)*.\n\n__**Spécialisation :**__\nDonne accès à tout .",
        "price": 500000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "Une fois le nen utilisé celui-ci vous attribue un nen aléatoirement avec la commande !!rollnen (avec 19.9% de chance pour chaque sauf la spécialisation qui est à 0.5%)",
        "requirements": {
            "items": [7]
        },
        "role_id": 1363928528587984998,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 22,
        "emoji": "<:imperiale:1363601099990241601>",
        "title": " Arme démoniaque impériale",
        "description": "Cette objet vous permet d'utiliser le démon dans votre arme et vous permet de voler votre adversaire",
        "price": 500000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 3,
        "tradeable": True,
        "usable": True,
        "use_effect": "Un /roll 50 devra être fait et vous permettra de voler le pourcentage de ce roll à l’utilisateur de votre choix à condition que celui-ci soit plus riche que vous ",
        "requirements": {
            "items": [31]
        },
        "role_id": 1363817586466361514,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 45,
        "emoji": "<:hakidesrois:1363623066667843616>",
        "title": "Haki des Rois",
        "description": "Apprenez le haki des rois comme les Empereurs des mers. Faites +haki <@user> pour le paralyser ainsi il n’aura pas accès aux salons économiques",
        "price": 500000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "Donne accès a l'Haki des Rois",
        "requirements": {},
        "role_id": 1363817645249527879,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 28,
        "emoji": "<:rage:1363599799043227940>",
        "title": " Rage du Berserker",
        "description": "Tu perds tout contrôle. L’armure du Berserker te consume, et avec elle, ta dernière part d’humanité. Tu ne voles pas. Tu ne gagnes rien. Tu détruis, par pure haine. Ton seul objectif : voir l’ennemi ruiné.",
        "price": 500000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "Utilisable une seule fois avec !!berserk <@user> → roll 100, % retiré à la banque de la cible (ex : roll 67 = -67%). Nécessite l’armure du Berserker. Cooldown de 7j après achat. Objet détruit après usage.",
        "requirements": {
            "items": [81]
        },
        "role_id": 1363821333624127618,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 23,
        "emoji": "<:pokeball:1363942456676061346>",
        "title": "Pokeball",
        "description": "Cet objet vous permet de voler un objet d’une personne au hasard",
        "price": 500000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 1,
        "tradeable": True,
        "usable": True,
        "use_effect": "Vous donne l'accès de voler un objet au hasard de l'inventaire d'un joueur",
        "requirements": {},
        "role_id": 1363942048075481379,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 34,
        "emoji": "<:nanashimura:1363942592156405830>",
        "title": "Float",
        "description": "Vous utilisez l’un des alters provenant du One for all, et plus précisément de Nana Shimura. En l’utilisant, vous pouvez voler aussi haut que personne ne peut y accéder.",
        "price": 500000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 2,
        "tradeable": True,
        "usable": True,
        "use_effect": "La commande +float vous donne accès au salon (nom du salon) durant 15min mais seulement possible 1/jour.",
        "requirements": {},
        "role_id": 1363946902730575953,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
    {
        "id": 99,
        "emoji": "<:ultrainstinct:1363601650123801027>",
        "title": "Ultra Instinct ",
        "description": "Vous utilisez la forme ultime du Ultra Instinct. Vous pouvez seulement l’utiliser pendant (mettre le temps d’immunité). Lorsque vous utilisez cette forme ultime, vous anticipez toutes attaques et vous l’esquivez (donc immunisé). Malheureusement cette forme utilise énormément de votre ki, il vous faudra donc 5 jours de repos pour réutiliser cette forme",
        "price": 750000,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 1,
        "tradeable": True,
        "usable": True,
        "use_effect": "Donne accès a l'Ultra Instinct",
        "requirements": {},
        "role_id": 1363821033060307106,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": True
    },
{
    "id": 202,
    "emoji": "<:bc1s1:1364217784439144488>",
    "title": "Boule de Cristal n°1",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
{
    "id": 197,
    "emoji": "<:bc2s1:1364224502996930642>",
    "title": "Boule de Cristal n°2",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
{
    "id": 425,
    "emoji": "<:bc3s1:1364224526476640306>",
    "title": "Boule de Cristal n°3",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
{
    "id": 736,
    "emoji": "<:bc4s1:1364224543937396746>",
    "title": "Boule de Cristal n°4",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
{
    "id": 872,
    "emoji": "<:bc5s1:1364224573306048522>",
    "title": "Boule de Cristal n°5",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
{
    "id": 964,
    "emoji": "<:bc6s1:1364224591488221276>",
    "title": "Boule de Cristal n°6",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
{
    "id": 987,
    "emoji": "<:bc7s1:1364224611536994315>",
    "title": "Boule de Cristal n°7",
    "description": "Une sphère mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
    "price": 0,
    "emoji_price": "<:ecoEther:1341862366249357374>",
    "quantity": 0,
    "tradeable": True,
    "usable": False,
    "use_effect": "???",
    "requirements": {},  # Aucun requirement
    "role_id": None,  # Aucun rôle à donner
    "remove_after_purchase": {
        "roles": False,
        "items": False
    },
    "used": False
},
]


# Fonction pour insérer les items dans MongoDB
def insert_items_into_db():
    for item in ITEMS:
        if not collection16.find_one({"id": item["id"]}):
            collection16.insert_one(item)

def get_page_embed(page: int, items_per_page=10):
    start = page * items_per_page
    end = start + items_per_page
    items = ITEMS[start:end]

    embed = discord.Embed(title="🛒 Boutique", color=discord.Color.blue())

    for item in items:
        formatted_price = f"{item['price']:,}".replace(",", " ")
        name_line = f"ID: {item['id']} | {formatted_price} {item['emoji_price']} - {item['title']} {item['emoji']}"

        # Seulement la description, sans les "requirements" et "bonus"
        value = item["description"]

        embed.add_field(name=name_line, value=value, inline=False)

    total_pages = (len(ITEMS) - 1) // items_per_page + 1
    embed.set_footer(text=f"Page {page + 1}/{total_pages}")
    return embed

# Vue pour les boutons de navigation
class Paginator(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        self.page = 0
        self.user = user

    async def update(self, interaction: discord.Interaction):
        embed = get_page_embed(self.page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Tu n'as pas la permission de naviguer dans ce menu.",
                color=discord.Color.red()
            )
            return await interaction.response.edit_message(embed=embed, view=self)
        if self.page > 0:
            self.page -= 1
            await self.update(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Tu n'as pas la permission de naviguer dans ce menu.",
                color=discord.Color.red()
            )
            return await interaction.response.edit_message(embed=embed, view=self)
        if (self.page + 1) * 10 < len(ITEMS):
            self.page += 1
            await self.update(interaction)

# Fonction de vérification des requirements (rôles et items)
async def check_requirements(user: discord.Member, requirements: dict):
    # Vérifier les rôles requis
    if "roles" in requirements:
        user_roles = [role.id for role in user.roles]
        for role_id in requirements["roles"]:
            if role_id not in user_roles:
                return False, f"Tu n'as pas le rôle requis <@&{role_id}>."

    # Vérifier les items requis (dans un système de base de données par exemple)
    if "items" in requirements:
        for item_id in requirements["items"]:
            item_in_inventory = await check_user_has_item(user, item_id)  # Fonction fictive à implémenter
            if not item_in_inventory:
                return False, f"Tu n'as pas l'item requis ID:{item_id}."

    return True, "Requirements vérifiés avec succès."

# Fonction d'achat d'un item
async def buy_item(user: discord.Member, item_id: int):
    # Chercher l'item dans la boutique
    item = next((i for i in ITEMS if i["id"] == item_id), None)
    if not item:
        return f"L'item avec l'ID {item_id} n'existe pas."

    # Vérifier les requirements
    success, message = await check_requirements(user, item["requirements"])
    if not success:
        return message

    # Vérifier si le rôle doit être ajouté ou supprimé après l'achat
    if item["remove_after_purchase"]["roles"]:
        role = discord.utils.get(user.guild.roles, id=item["role_id"])
        if role:
            await user.remove_roles(role)
            return f"Le rôle {role.name} a été supprimé après l'achat de {item['title']}."

    if item["remove_after_purchase"]["items"]:
        # Logique pour supprimer l'item (par exemple, de l'inventaire du joueur)
        pass

    return f"L'achat de {item['title']} a été effectué avec succès."

# Slash command /item-store
@bot.tree.command(name="item-store", description="Affiche la boutique d'items")
async def item_store(interaction: discord.Interaction):
    embed = get_page_embed(0)
    view = Paginator(user=interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

# Appel de la fonction pour insérer les items dans la base de données lors du démarrage du bot
insert_items_into_db()

@bot.tree.command(name="item-buy", description="Achète un item de la boutique via son ID.")
@app_commands.describe(item_id="ID de l'item à acheter", quantity="Quantité à acheter (défaut: 1)")
async def item_buy(interaction: discord.Interaction, item_id: int, quantity: int = 1):
    user_id = interaction.user.id
    guild_id = interaction.guild.id

    item = collection16.find_one({"id": item_id})
    if not item:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item introuvable",
            description="Aucun item avec cet ID n'a été trouvé dans la boutique.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if quantity <= 0:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Quantité invalide",
            description="La quantité doit être supérieure à zéro.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if item["quantity"] < quantity:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Stock insuffisant",
            description=f"Il ne reste que **{item['quantity']}x** de cet item en stock.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Vérifier les requirements avant de permettre l'achat
    valid, message = await check_requirements(interaction.user, item.get("requirements", {}))
    if not valid:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Prérequis non remplis",
            description=message,
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_data = collection.find_one({"user_id": user_id, "guild_id": guild_id}) or {"cash": 0}
    total_price = int(item["price"] * quantity)  # Forcer le total_price en entier

    if user_data["cash"] < total_price:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Fonds insuffisants",
            description=f"Tu n'as pas assez de <:ecoEther:1341862366249357374> pour cet achat.\nPrix total : **{total_price:,}**",  # Format avec des séparateurs de milliers
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Retirer l'argent
    collection.update_one(
        {"user_id": user_id, "guild_id": guild_id},
        {"$inc": {"cash": -total_price}},
        upsert=True
    )

    # Mise à jour de l'inventaire simple (collection7)
    existing = collection7.find_one({"user_id": user_id, "guild_id": guild_id})
    if existing:
        inventory = existing.get("items", {})
        inventory[str(item_id)] = inventory.get(str(item_id), 0) + quantity
        collection7.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": {"items": inventory}}
        )
    else:
        collection7.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "items": {str(item_id): quantity}
        })

    # Mise à jour de l'inventaire structuré (collection17)
    for _ in range(quantity):
        collection17.insert_one({
            "guild_id": guild_id,
            "user_id": user_id,
            "item_id": item_id,
            "item_name": item["title"],
            "emoji": item.get("emoji"),
            "price": item["price"],
            "acquired_at": datetime.utcnow()
        })

    # Mise à jour du stock boutique
    collection16.update_one(
        {"id": item_id},
        {"$inc": {"quantity": -quantity}}
    )

    # Gestion de la suppression des rôles et items si nécessaire
    if item.get("remove_after_purchase"):
        # Suppression des rôles si la configuration l'exige
        if item["remove_after_purchase"].get("roles", False):
            role = discord.utils.get(interaction.guild.roles, id=item["role_id"])
            if role:
                await interaction.user.remove_roles(role)
                print(f"Rôle {role.name} supprimé pour {interaction.user.name} après l'achat.")

        # Suppression des items si la configuration l'exige
        if item["remove_after_purchase"].get("items", False):
            # Logique pour supprimer un item de l'inventaire, si nécessaire
            inventory = collection7.find_one({"user_id": user_id, "guild_id": guild_id})
            if inventory:
                user_items = inventory.get("items", {})
                if str(item_id) in user_items:
                    user_items[str(item_id)] -= quantity
                    if user_items[str(item_id)] <= 0:
                        del user_items[str(item_id)]  # Supprimer l'item si sa quantité atteint zéro
                    collection7.update_one(
                        {"user_id": user_id, "guild_id": guild_id},
                        {"$set": {"items": user_items}}
                    )
                    print(f"{quantity} de l'item {item['title']} supprimé de l'inventaire de {interaction.user.name}.")

    embed = discord.Embed(
        title="<:Check:1362710665663615147> Achat effectué",
        description=(
            f"Tu as acheté **{quantity}x {item['title']}** {item['emoji']} "
            f"pour **{total_price:,}** {item['emoji_price']} !"  # Format avec des séparateurs de milliers
        ),
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="item-inventory", description="Affiche l'inventaire d'un utilisateur")
async def item_inventory(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user
    guild_id = interaction.guild.id

    # Curseur synchrone avec pymongo
    items_cursor = collection17.find({"guild_id": guild_id, "user_id": user.id})

    item_counts = {}
    item_details = {}

    for item in items_cursor:
        item_id = item["item_id"]
        item_counts[item_id] = item_counts.get(item_id, 0) + 1
        if item_id not in item_details:
            item_details[item_id] = {
                "title": item.get("item_name", "Nom inconnu"),
                "emoji": item.get("emoji", ""),
            }

    # Bleu doux (ex : #89CFF0)
    soft_blue = discord.Color.from_rgb(137, 207, 240)

    embed = discord.Embed(
        title="Use an item with the /item-use command.",
        color=soft_blue
    )

    embed.set_author(name=user.name, icon_url=user.avatar.url if user.avatar else user.default_avatar.url)

    if not item_counts:
        embed.title = "<:classic_x_mark:1362711858829725729> Inventaire vide"
        embed.description = "Use an item with the `/item-use` command."
        embed.color = discord.Color.red()
    else:
        lines = []
        for item_id, quantity in item_counts.items():
            details = item_details[item_id]
            lines.append(f"**{quantity}x** {details['title']} {details['emoji']} (ID: `{item_id}`)")
        embed.description = "\n".join(lines)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="item-info", description="Affiche toutes les informations d'un item de la boutique")
@app_commands.describe(id="ID de l'item à consulter")
async def item_info(interaction: discord.Interaction, id: int):
    item = collection16.find_one({"id": id})
    
    if not item:
        return await interaction.response.send_message("❌ Aucun item trouvé avec cet ID.", ephemeral=True)

    formatted_price = f"{item['price']:,}".replace(",", " ")  # Espace fine insécable

    embed = discord.Embed(
        color=discord.Color.blue()
    )

    # Garder uniquement cette ligne pour afficher le nom + pp
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

    embed.add_field(name="**Nom de l'item**", value=item['title'], inline=False)
    embed.add_field(name="**Description**", value=item['description'], inline=False)

    embed.add_field(name="ID", value=str(item["id"]), inline=True)
    embed.add_field(name="Prix", value=f"{formatted_price} {item['emoji_price']}", inline=True)
    embed.add_field(name="Quantité", value=str(item.get("quantity", "Indisponible")), inline=True)

    tradeable = "✅ Oui" if item.get("tradeable", False) else "❌ Non"
    usable = "✅ Oui" if item.get("usable", False) else "❌ Non"

    embed.add_field(name="Échangeable", value=tradeable, inline=True)
    embed.add_field(name="Utilisable", value=usable, inline=True)

    if item.get("use_effect"):
        embed.add_field(name="Effet à l'utilisation", value=item["use_effect"], inline=False)

    # Vérifier et afficher les prérequis
    if item.get("requirements"):
        requirements = item["requirements"]
        req_message = []

        # Vérifier les rôles requis
        if "roles" in requirements:
            for role_id in requirements["roles"]:
                role = discord.utils.get(interaction.guild.roles, id=role_id)
                if role:
                    req_message.append(f"• Rôle requis: <@&{role_id}> ({role.name})")
                else:
                    req_message.append(f"• Rôle requis: <@&{role_id}> (Introuvable)")

        # Vérifier les items requis
        if "items" in requirements:
            for required_item_id in requirements["items"]:
                item_in_inventory = await check_user_has_item(interaction.user, required_item_id)
                if item_in_inventory:
                    req_message.append(f"• Item requis: ID {required_item_id} (Possédé)")
                else:
                    req_message.append(f"• Item requis: ID {required_item_id} (Non possédé)")

        if req_message:
            embed.add_field(name="Prérequis", value="\n".join(req_message), inline=False)
        else:
            embed.add_field(name="Prérequis", value="Aucun prérequis", inline=False)

    emoji = item["emoji"]
    if emoji:
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji.split(':')[2].split('>')[0]}.png")

    embed.set_footer(text="🛒 Etherya • Détails de l'item")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="item-use", description="Utilise un item de ton inventaire.")
@app_commands.describe(item_id="ID de l'item à utiliser")
async def item_use(interaction: discord.Interaction, item_id: int):
    user = interaction.user
    user_id = user.id
    guild = interaction.guild
    guild_id = guild.id

    # Vérifie si l'item est dans l'inventaire
    owned_item = collection17.find_one({"user_id": user_id, "guild_id": guild_id, "item_id": item_id})
    if not owned_item:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item non possédé",
            description="Tu ne possèdes pas cet item dans ton inventaire.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Récupère les infos de l'item
    item_data = collection16.find_one({"id": item_id})
    if not item_data or not item_data.get("usable", False):
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Utilisation impossible",
            description="Cet item n'existe pas ou ne peut pas être utilisé.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Vérifier les prérequis
    if item_data.get("requirements"):
        requirements = item_data["requirements"]
        req_message = []

        # Vérifier les rôles requis
        if "roles" in requirements:
            for role_id in requirements["roles"]:
                role = discord.utils.get(interaction.guild.roles, id=role_id)
                if role and role not in user.roles:
                    req_message.append(f"• Rôle requis: <@&{role_id}> ({role.name})")
        
        # Vérifier les items requis
        if "items" in requirements:
            for required_item_id in requirements["items"]:
                item_in_inventory = await check_user_has_item(interaction.user, required_item_id)
                if not item_in_inventory:
                    req_message.append(f"• Item requis: ID {required_item_id} (Non possédé)")

        # Si des prérequis ne sont pas remplis, empêcher l'utilisation de l'item
        if req_message:
            embed = discord.Embed(
                title="<:classic_x_mark:1362711858829725729> Prérequis non remplis",
                description="Tu ne remplis pas les prérequis suivants pour utiliser cet item :\n" + "\n".join(req_message),
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

    # Supprime un exemplaire dans l'inventaire
    collection17.delete_one({
        "user_id": user_id,
        "guild_id": guild_id,
        "item_id": item_id
    })

    embed = discord.Embed(
        title=f"<:Check:1362710665663615147> Utilisation de l'item",
        description=f"Tu as utilisé **{item_data['title']}** {item_data.get('emoji', '')}.",
        color=discord.Color.green()
    )

    # Ajout du rôle si défini
    role_id = item_data.get("role_id")
    if role_id:
        role = guild.get_role(int(role_id))
        if role:
            # Vérification de la hiérarchie des rôles
            if interaction.guild.me.top_role.position > role.position:
                try:
                    await user.add_roles(role)
                    embed.add_field(name="🎭 Rôle attribué", value=f"Tu as reçu le rôle **{role.name}**.", inline=False)
                except discord.Forbidden:
                    embed.add_field(
                        name="⚠️ Rôle non attribué",
                        value="Je n’ai pas la permission d’attribuer ce rôle. Vérifie mes permissions ou la hiérarchie des rôles.",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="⚠️ Rôle non attribué",
                    value="Le rôle est trop élevé dans la hiérarchie pour que je puisse l’attribuer.",
                    inline=False
                )

    # Ajout d'un item bonus s'il y en a
    reward_item_id = item_data.get("gives_item_id")
    if reward_item_id:
        collection17.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "item_id": reward_item_id
        })
        reward_data = collection16.find_one({"id": reward_item_id})
        if reward_data:
            reward_title = reward_data["title"]
            reward_emoji = reward_data.get("emoji", "")
            embed.add_field(name="🎁 Récompense reçue", value=f"Tu as reçu **{reward_title}** {reward_emoji}.", inline=False)

    # Gestion de la suppression après utilisation
    if item_data.get("remove_after_use"):
        # Suppression des rôles après utilisation
        if item_data["remove_after_use"].get("roles", False):
            # Vérifie si le rôle a été attribué avant de le retirer
            role = discord.utils.get(interaction.guild.roles, id=item_data["role_id"])
            if role and role in user.roles:
                await user.remove_roles(role)
                embed.add_field(name="⚠️ Rôle supprimé", value=f"Le rôle **{role.name}** a été supprimé après l'utilisation de l'item.", inline=False)
                print(f"Rôle {role.name} supprimé pour {interaction.user.name} après l'utilisation de l'item.")

        # Suppression des items après utilisation
        if item_data["remove_after_use"].get("items", False):
            # Suppression de l'item de l'inventaire
            collection17.delete_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "item_id": item_id
            })
            print(f"Item ID {item_id} supprimé de l'inventaire de {interaction.user.name}.")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="item-give", description="(Admin) Donne un item à un utilisateur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    member="Utilisateur à qui donner l'item",
    item_id="ID de l'item à donner",
    quantity="Quantité d'items à donner"
)
async def item_give(interaction: discord.Interaction, member: discord.Member, item_id: int, quantity: int = 1):
    guild_id = interaction.guild.id
    user_id = member.id

    # Vérifie si l'item existe dans la boutique
    item_data = collection16.find_one({"id": item_id})
    if not item_data:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item introuvable",
            description="Cet item n'existe pas dans la boutique.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if quantity < 1:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Quantité invalide",
            description="La quantité doit être d'au moins **1**.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Ajoute l'item dans la collection17 (inventaire structuré)
    for _ in range(quantity):
        collection17.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "item_id": item_id,
            "item_name": item_data["title"],
            "emoji": item_data.get("emoji", ""),
            "price": item_data.get("price"),
            "acquired_at": datetime.utcnow()
        })

    item_name = item_data["title"]
    emoji = item_data.get("emoji", "")

    embed = discord.Embed(
        title=f"<:Check:1362710665663615147> Item donné",
        description=f"**{quantity}x {item_name}** {emoji} ont été donnés à {member.mention}.",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="item-take", description="(Admin) Retire un item d'un utilisateur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    member="Utilisateur à qui retirer l'item",
    item_id="ID de l'item à retirer",
    quantity="Quantité d'items à retirer"
)
async def item_take(interaction: discord.Interaction, member: discord.Member, item_id: int, quantity: int = 1):
    guild_id = interaction.guild.id
    user_id = member.id

    # Vérifie si l'item existe
    item_data = collection16.find_one({"id": item_id})
    if not item_data:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item introuvable",
            description="Cet item n'existe pas dans la boutique.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    item_name = item_data["title"]
    emoji = item_data.get("emoji", "")

    # Vérifie combien l'utilisateur en possède
    owned_count = collection17.count_documents({
        "user_id": user_id,
        "guild_id": guild_id,
        "item_id": item_id
    })

    if owned_count < quantity:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Quantité insuffisante",
            description=f"{member.mention} ne possède que **{owned_count}x {item_name}** {emoji}. Impossible de retirer {quantity}.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Supprime les exemplaires un par un
    for _ in range(quantity):
        collection17.delete_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "item_id": item_id
        })

    embed = discord.Embed(
        title="<:Check:1362710665663615147> Item retiré",
        description=f"**{quantity}x {item_name}** {emoji} ont été retirés de l'inventaire de {member.mention}.",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="item-sell", description="Vends un item à un autre utilisateur pour un prix donné.")
@app_commands.describe(
    member="L'utilisateur à qui vendre l'item",
    item_id="ID de l'item à vendre",
    price="Prix de vente de l'item",
    quantity="Quantité d'items à vendre (par défaut 1)"
)
async def item_sell(interaction: discord.Interaction, member: discord.User, item_id: int, price: int, quantity: int = 1):
    guild_id = interaction.guild.id
    seller_id = interaction.user.id
    buyer_id = member.id

    item_data = collection16.find_one({"id": item_id})
    if not item_data:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item introuvable",
            description="Cet item n'existe pas dans la boutique.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    item_name = item_data["title"]
    emoji = item_data.get("emoji", "")

    owned_count = collection17.count_documents({
        "user_id": seller_id,
        "guild_id": guild_id,
        "item_id": item_id
    })

    if owned_count < quantity:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Vente impossible",
            description=f"Tu ne possèdes que **{owned_count}x {item_name}** {emoji}.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    buyer_data = collection.find_one({"guild_id": guild_id, "user_id": buyer_id}) or {"cash": 1500}
    total_price = price * quantity

    # Vérification du cash uniquement
    if buyer_data.get("cash", 0) < total_price:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Fonds insuffisants",
            description=f"{member.mention} n'a pas assez d'argent en **cash** pour acheter **{quantity}x {item_name}** {emoji}.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Boutons
    class SellView(View):
        def __init__(self):
            super().__init__(timeout=60)

        @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green)
        async def accept_sell(self, interaction_btn: discord.Interaction, button: Button):
            if interaction_btn.user.id != buyer_id:
                return await interaction_btn.response.send_message("❌ Ce n'est pas ton offre.", ephemeral=True)

            # Transfert de l'item
            for _ in range(quantity):
                collection17.insert_one({
                    "user_id": buyer_id,
                    "guild_id": guild_id,
                    "item_id": item_id,
                    "item_name": item_name,
                    "emoji": emoji,
                    "price": price,
                    "acquired_at": datetime.utcnow()
                })
                collection17.delete_one({
                    "user_id": seller_id,
                    "guild_id": guild_id,
                    "item_id": item_id
                })

            # Paiement
            collection.update_one(
                {"guild_id": guild_id, "user_id": buyer_id},
                {"$inc": {"cash": -total_price}},  # Décrémentation du cash de l'acheteur
                upsert=True
            )
            collection.update_one(
                {"guild_id": guild_id, "user_id": seller_id},
                {"$inc": {"cash": total_price}},  # Ajout du cash au vendeur
                upsert=True
            )

            confirm_embed = discord.Embed(
                title="<:Check:1362710665663615147> Vente conclue",
                description=f"{member.mention} a acheté **{quantity}x {item_name}** {emoji} pour **{total_price:,}** <:ecoEther:1341862366249357374>.",
                color=discord.Color.green()
            )
            await interaction_btn.response.edit_message(embed=confirm_embed, view=None)

        @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
        async def decline_sell(self, interaction_btn: discord.Interaction, button: Button):
            if interaction_btn.user.id != buyer_id:
                return await interaction_btn.response.send_message("❌ Ce n'est pas ton offre.", ephemeral=True)

            cancel_embed = discord.Embed(
                title="<:classic_x_mark:1362711858829725729> Offre refusée",
                description=f"{member.mention} a refusé l'offre.",
                color=discord.Color.red()
            )
            await interaction_btn.response.edit_message(embed=cancel_embed, view=None)

    view = SellView()

    offer_embed = discord.Embed(
        title=f"💸 Offre de {interaction.user.display_name}",
        description=f"{interaction.user.mention} te propose **{quantity}x {item_name}** {emoji} pour **{total_price:,}** <:ecoEther:1341862366249357374>.",
        color=discord.Color.gold()
    )
    offer_embed.set_footer(text="Tu as 60 secondes pour accepter ou refuser.")

    await interaction.response.send_message(embed=offer_embed, content=member.mention, view=view)

@bot.tree.command(name="item-leaderboard", description="Affiche le leaderboard des utilisateurs possédant un item spécifique.")
@app_commands.describe(
    item_id="ID de l'item dont vous voulez voir le leaderboard"
)
async def item_leaderboard(interaction: discord.Interaction, item_id: int):
    guild = interaction.guild
    guild_id = guild.id

    item_data = collection16.find_one({"id": item_id})
    if not item_data:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item introuvable",
            description="Aucun item n'existe avec cet ID.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    item_name = item_data["title"]
    item_emoji = item_data.get("emoji", "")

    # Agrégation des quantités par utilisateur
    pipeline = [
        {"$match": {"guild_id": guild_id, "item_id": item_id}},
        {"$group": {"_id": "$user_id", "quantity": {"$sum": 1}}},
        {"$sort": {"quantity": -1}},
        {"$limit": 10}
    ]
    leaderboard = list(collection17.aggregate(pipeline))

    if not leaderboard:
        embed = discord.Embed(
            title="📉 Aucun résultat",
            description=f"Aucun utilisateur ne possède **{item_name}** {item_emoji} dans ce serveur.",
            color=discord.Color.dark_grey()
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title=f"🏆 Leaderboard : {item_name} {item_emoji}",
        description="Classement des membres qui possèdent le plus cet item :",
        color=discord.Color.blurple()
    )

    for i, entry in enumerate(leaderboard, start=1):
        user = guild.get_member(entry["_id"])
        name = user.display_name if user else f"<Utilisateur inconnu `{entry['_id']}`>"
        embed.add_field(
            name=f"{i}. {name}",
            value=f"{entry['quantity']}x {item_name} {item_emoji}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


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


@bot.tree.command(name="restock", description="Restock un item dans la boutique")
@app_commands.describe(item_id="ID de l'item à restock", quantity="Nouvelle quantité à définir")
async def restock(interaction: discord.Interaction, item_id: int, quantity: int):
    if interaction.user.id != ISEY_ID:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    item = collection16.find_one({"id": item_id})
    if not item:
        return await interaction.response.send_message(f"❌ Aucun item trouvé avec l'ID {item_id}.", ephemeral=True)

    collection16.update_one({"id": item_id}, {"$set": {"quantity": quantity}})
    return await interaction.response.send_message(
        f"✅ L'item **{item['title']}** a bien été restocké à **{quantity}** unités.", ephemeral=True
    )

@bot.tree.command(name="reset-item", description="Réinitialise ou supprime les items dans la boutique")
@app_commands.describe(item_id="ID de l'item à réinitialiser ou supprimer")
async def reset_item(interaction: discord.Interaction, item_id: int):
    if interaction.user.id != ISEY_ID:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    item = collection16.find_one({"id": item_id})
    if not item:
        return await interaction.response.send_message(f"❌ Aucun item trouvé avec l'ID {item_id}.", ephemeral=True)

    # Suppression de l'item dans la base de données
    collection16.delete_one({"id": item_id})

    return await interaction.response.send_message(
        f"✅ L'item **{item['title']}** a bien été supprimé de la boutique.", ephemeral=True
    )

BADGES = [
    {
        "id": 1,
        "emoji": "<:gon:1363923253134889082>",
        "title": "Badge Hunter X Hunter",
        "description": "Badge Collector.",
        "price": 100,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 10,
        "tradeable": True,
        "usable": False,
        "use_effect": "???",
        "requirements": {},
        "role_id": None,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": False
    },
    {
        "id": 2,
        "emoji": "<:hxh:1363923320256463088>",
        "title": "Badge Gon",
        "description": "Badge Collector",
        "price": 150,
        "emoji_price": "<:ecoEther:1341862366249357374>",
        "quantity": 5,
        "tradeable": True,
        "usable": False,
        "use_effect": "???",
        "requirements": {},
        "role_id": None,
        "remove_after_purchase": {
            "roles": False,
            "items": False
        },
        "used": False
    },
]

# Fonction pour obtenir les badges dans un format de page avec pagination
def get_badge_embed(page: int = 0, items_per_page=10):
    start = page * items_per_page
    end = start + items_per_page
    badges_page = BADGES[start:end]

    embed = discord.Embed(title="🛒 Boutique de Badges", color=discord.Color.purple())

    for badge in badges_page:
        formatted_price = f"{badge['price']:,}".replace(",", " ")
        name_line = f"ID: {badge['id']} | {formatted_price} {badge['emoji_price']} - {badge['title']} {badge['emoji']}"

        # Seulement la description, sans les "requirements" et "bonus"
        value = badge["description"]

        embed.add_field(name=name_line, value=value, inline=False)

    total_pages = (len(BADGES) - 1) // items_per_page + 1
    embed.set_footer(text=f"Page {page + 1}/{total_pages}")
    return embed

# Vue pour les boutons de navigation
class BadgePaginator(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.page = 0
        self.user = user

    async def update(self, interaction):
        embed = get_badge_embed(self.page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction, button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Tu ne peux pas utiliser ces boutons.", ephemeral=True)
        if self.page > 0:
            self.page -= 1
            await self.update(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction, button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Tu ne peux pas utiliser ces boutons.", ephemeral=True)
        if (self.page + 1) * 10 < len(BADGES):
            self.page += 1
            await self.update(interaction)

# Commande pour afficher la boutique de badges
@bot.tree.command(name="badge-store", description="Affiche la boutique de badges")
async def badge_store(interaction: discord.Interaction):
    view = BadgePaginator(interaction.user)
    embed = get_badge_embed(0)  # Initial page (0)
    await interaction.channel.send(embed=embed, view=view)  # Envoi à tout le monde dans le canal

# Fonction pour insérer les badges dans la base de données lors du démarrage du bot
def insert_badge_into_db():
    for badge in BADGES:
        if not collection19.find_one({"id": badge["id"]}):
            collection19.insert_one(badge)

# Appel de la fonction pour insérer les badges dans la base de données lors du démarrage du bot
insert_badge_into_db()

@bot.tree.command(name="badge-inventory", description="Affiche ton inventaire de badges")
async def badge_inventory(interaction: discord.Interaction):
    data = collection20.find_one({"user_id": interaction.user.id})
    if not data or not data.get("badges"):
        return await interaction.response.send_message("Tu ne possèdes aucun badge pour l’instant.", ephemeral=True)

    user_badges = data["badges"]
    badge_list = list(collection19.find({"id": {"$in": user_badges}}))

    def get_inventory_embed(page=0, per_page=10):
        embed = discord.Embed(title=f"🎖️ Badges de {interaction.user.display_name}", color=discord.Color.orange())
        start = page * per_page
        end = start + per_page
        for badge in badge_list[start:end]:
            embed.add_field(
                name=f"ID: {badge['id']} | {badge['name']} {badge['emoji']}",
                value=badge["description"],
                inline=False
            )
        total_pages = (len(badge_list) - 1) // per_page + 1
        embed.set_footer(text=f"Page {page + 1}/{total_pages}")
        return embed

    class InventoryPaginator(discord.ui.View):
        def __init__(self, user):
            super().__init__(timeout=60)
            self.page = 0
            self.user = user

        async def update(self, interaction):
            await interaction.response.edit_message(embed=get_inventory_embed(self.page), view=self)

        @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
        async def prev(self, interaction, button):
            if interaction.user.id != self.user.id:
                return await interaction.response.send_message("❌ Tu ne peux pas utiliser ces boutons.", ephemeral=True)
            if self.page > 0:
                self.page -= 1
                await self.update(interaction)

        @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction, button):
            if interaction.user.id != self.user.id:
                return await interaction.response.send_message("❌ Tu ne peux pas utiliser ces boutons.", ephemeral=True)
            if (self.page + 1) * 10 < len(badge_list):
                self.page += 1
                await self.update(interaction)

    view = InventoryPaginator(interaction.user)
    await interaction.response.send_message(embed=get_inventory_embed(), view=view, ephemeral=True)

@bot.tree.command(name="badge-give", description="(Admin) Donne un badge à un utilisateur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    member="Utilisateur à qui donner le badge",
    badge_id="ID du badge à donner"
)
async def badge_give(interaction: discord.Interaction, member: discord.Member, badge_id: int):
    badge = collection19.find_one({"id": badge_id})
    if not badge:
        embed = discord.Embed(
            title="❌ Badge introuvable",
            description="Ce badge n'existe pas.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_data = collection20.find_one({"user_id": member.id})
    if user_data and badge_id in user_data.get("badges", []):
        embed = discord.Embed(
            title="❌ Badge déjà possédé",
            description=f"{member.mention} possède déjà ce badge.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    collection20.update_one(
        {"user_id": member.id},
        {"$addToSet": {"badges": badge_id}},
        upsert=True
    )

    embed = discord.Embed(
        title="🎖️ Badge donné",
        description=f"Le badge **{badge['title']}** {badge['emoji']} a été donné à {member.mention}.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="badge-take", description="(Admin) Retire un badge d'un utilisateur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    member="Utilisateur à qui retirer le badge",
    badge_id="ID du badge à retirer"
)
async def badge_take(interaction: discord.Interaction, member: discord.Member, badge_id: int):
    badge = collection19.find_one({"id": badge_id})
    if not badge:
        embed = discord.Embed(
            title="❌ Badge introuvable",
            description="Ce badge n'existe pas.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_data = collection20.find_one({"user_id": member.id})
    if not user_data or badge_id not in user_data.get("badges", []):
        embed = discord.Embed(
            title="❌ Badge non possédé",
            description=f"{member.mention} ne possède pas ce badge.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    collection20.update_one(
        {"user_id": member.id},
        {"$pull": {"badges": badge_id}}
    )

    embed = discord.Embed(
        title="🧼 Badge retiré",
        description=f"Le badge **{badge['title']}** {badge['emoji']} a été retiré à {member.mention}.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reset-badge", description="Réinitialise ou supprime un badge de la boutique")
@app_commands.describe(badge_id="ID du badge à réinitialiser ou supprimer")
async def reset_badge(interaction: discord.Interaction, badge_id: int):
    if interaction.user.id != ISEY_ID:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    badge = collection19.find_one({"id": badge_id})
    if not badge:
        return await interaction.response.send_message(f"❌ Aucun badge trouvé avec l'ID {badge_id}.", ephemeral=True)

    # Supprime le badge de la boutique
    collection19.delete_one({"id": badge_id})

    return await interaction.response.send_message(
        f"✅ Le badge **{badge['title']}** {badge.get('emoji', '')} a été supprimé de la boutique.", ephemeral=True
    )

@bot.tree.command(name="start-rewards", description="Définit la date de début des rewards (réservé à ISEY)")
async def start_rewards(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
        return

    guild_id = interaction.guild.id

    # Vérifie si une date est déjà enregistrée
    existing = collection22.find_one({"guild_id": guild_id})
    if existing:
        await interaction.response.send_message(
            f"⚠️ Les rewards ont déjà été démarrés le <t:{int(existing['start_timestamp'])}:F>.",
            ephemeral=True
        )
        return

    now = datetime.utcnow()
    timestamp = int(now.timestamp())

    collection22.insert_one({
        "guild_id": guild_id,
        "start_date": now.isoformat(),
        "start_timestamp": timestamp
    })

    await interaction.response.send_message(
        f"✅ Le système de rewards a bien été lancé ! Début : <t:{timestamp}:F>",
        ephemeral=True
    )

async def give_reward(interaction: discord.Interaction, day: int):
    reward = daily_rewards.get(day)
    if not reward:
        await interaction.response.send_message("Aucune récompense disponible pour ce jour.", ephemeral=True)
        return

    coins = reward.get("coins", 0)
    badge = reward.get("badge")
    item = reward.get("item")

    # === Récompense enregistrée (collection23) ===
    user_data = collection23.find_one({"guild_id": interaction.guild.id, "user_id": interaction.user.id})
    if not user_data:
        user_data = {"guild_id": interaction.guild.id, "user_id": interaction.user.id, "rewards_received": {}}

    user_data["rewards_received"][str(day)] = reward
    collection23.update_one(
        {"guild_id": interaction.guild.id, "user_id": interaction.user.id},
        {"$set": user_data},
        upsert=True
    )

    # === Coins (collection économie) ===
    eco_data = collection.find_one({"guild_id": interaction.guild.id, "user_id": interaction.user.id})
    if not eco_data:
        collection.insert_one({
            "guild_id": interaction.guild.id,
            "user_id": interaction.user.id,
            "cash": coins,
            "bank": 0
        })
    else:
        collection.update_one(
            {"guild_id": interaction.guild.id, "user_id": interaction.user.id},
            {"$inc": {"cash": coins}}
        )

    # === Badge (collection20) ===
    if badge:
        badge_data = collection20.find_one({"user_id": interaction.user.id})
        if not badge_data:
            collection20.insert_one({"user_id": interaction.user.id, "badges": [badge]})
        elif badge not in badge_data.get("badges", []):
            collection20.update_one(
                {"user_id": interaction.user.id},
                {"$push": {"badges": badge}}
            )

    # === Item (collection17) ===
    if item:
        item_config = collection18.find_one({"id": item})  # Tu peux adapter si l'item vient d'ailleurs
        if item_config:
            collection17.insert_one({
                "guild_id": interaction.guild.id,
                "user_id": interaction.user.id,
                "item_id": item,
                "item_name": item_config.get("title", "Nom inconnu"),
                "emoji": item_config.get("emoji", "")
            })

    # === Embed de récompense ===
    days_received = len(user_data["rewards_received"])
    total_days = 7
    embed = discord.Embed(
        title="🎁 Récompense de la journée",
        description=f"Voici ta récompense pour le jour {day} !",
        color=discord.Color.green()
    )
    embed.add_field(name="Coins", value=f"{coins} <:ecoEther:1341862366249357374>", inline=False)
    if badge:
        embed.add_field(name="Badge", value=f"Badge ID {badge}", inline=False)
    if item:
        embed.add_field(name="Item", value=f"{item_config.get('title', 'Nom inconnu')} {item_config.get('emoji', '')} (ID: {item})", inline=False)
    embed.set_image(url=reward["image_url"])

    progress = "█" * days_received + "░" * (total_days - days_received)
    embed.add_field(name="Progression", value=f"{progress} ({days_received}/{total_days})", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# === COMMANDE SLASH /rewards ===
@bot.tree.command(name="rewards", description="Récupère ta récompense quotidienne")
async def rewards(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    user_id = interaction.user.id

    # Vérifier la date de début des récompenses
    start_date = get_start_date(guild_id)
    if not start_date:
        await interaction.response.send_message("Le système de récompenses n'est pas encore configuré.", ephemeral=True)
        return

    # Calculer le nombre de jours écoulés depuis le début
    days_elapsed = (datetime.utcnow() - start_date).days + 1
    if days_elapsed > 7:
        await interaction.response.send_message("La période de récompenses est terminée.", ephemeral=True)
        return

    # Récupérer les données de l'utilisateur
    user_data = collection23.find_one({"guild_id": guild_id, "user_id": user_id})
    received = user_data.get("rewards_received", {}) if user_data else {}

    # Vérifier si une récompense a été manquée
    for i in range(1, days_elapsed):
        if str(i) not in received:
            await interaction.response.send_message("Tu as manqué un jour. Tu ne peux plus récupérer les récompenses.", ephemeral=True)
            return

    # Vérifier si la récompense d’aujourd’hui a déjà été récupérée
    if str(days_elapsed) in received:
        await interaction.response.send_message("Tu as déjà récupéré ta récompense aujourd'hui.", ephemeral=True)
        return

    # Donner la récompense pour le jour actuel
    await give_reward(interaction, days_elapsed)


# Rôle autorisé à utiliser le Nen
PERMISSION_ROLE_ID = 1363928528587984998

# ID de l'item requis
LICENSE_ITEM_ID = 7

# Roles par type de Nen
nen_roles = {
    "renforcement": 1363306813688381681,
    "emission": 1363817609916584057,
    "manipulation": 1363817536348749875,
    "materialisation": 1363817636793810966,
    "transformation": 1363817619529924740,
    "specialisation": 1363817593252876368,
}

# Chances de drop en %
nen_drop_rates = [
    ("renforcement", 24.5),
    ("emission", 24.5),
    ("manipulation", 16.5),
    ("materialisation", 16.5),
    ("transformation", 17.5),
    ("specialisation", 0.5),
]

# === Vérifie si le joueur a une licence Hunter (item 7)
def has_license(user_id, guild_id):
    items_cursor = collection17.find({"guild_id": guild_id, "user_id": user_id})
    for item in items_cursor:
        if item["item_id"] == LICENSE_ITEM_ID:
            return True
    return False

# === Sélection aléatoire du Nen selon les chances
def get_random_nen():
    roll = random.uniform(0, 100)
    total = 0
    for nen_type, chance in nen_drop_rates:
        total += chance
        if roll <= total:
            return nen_type
    return "renforcement"  # fallback (improbable)

# === Commande Nen (ROLL)
@bot.command()
async def nen(ctx):
    user = ctx.author
    guild = ctx.guild

    # Vérif rôle autorisé
    permission_role = discord.utils.get(guild.roles, id=PERMISSION_ROLE_ID)
    if permission_role not in user.roles:
        return await ctx.send("❌ Tu n'es pas digne d'utiliser le Nen.")

    # Vérif licence Hunter
    if not has_license(user.id, guild.id):
        return await ctx.send("❌ Tu n'as pas de Licence Hunter (item ID 7) dans ton inventaire.")

    # Sélection Nen
    nen_type = get_random_nen()
    role_id = nen_roles.get(nen_type)
    nen_role = discord.utils.get(guild.roles, id=role_id)

    # Attribution du rôle Nen
    if nen_role:
        try:
            await user.add_roles(nen_role)
        except discord.Forbidden:
            return await ctx.send("⚠️ Je n’ai pas la permission d’attribuer des rôles.")

    # Embed de résultat
    color = discord.Color.blue()
    if nen_type == "specialisation":
        color = discord.Color.purple()

    embed = discord.Embed(
        title="🎴 Résultat du Nen Roll",
        description=f"Tu as éveillé le Nen de type **{nen_type.capitalize()}** !",
        color=color
    )
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    embed.set_footer(text="Utilise tes pouvoirs avec sagesse... ou pas.")

    await ctx.send(embed=embed)

# Liste des rôles autorisés à activer le renforcement
RENFORCEMENT_IDS = [1363306813688381681, 1363817593252876368]

COOLDOWN_DAYS = 7
DURATION_HOURS = 24
RENFORCEMENT_ROLE_ID = 1363306813688381681  # Le rôle qu'on donne pour 24h

@bot.command(name="renforcement")
async def renforcement(ctx):
    user = ctx.author
    guild = ctx.guild
    now = datetime.utcnow()

    # Vérifie que l'utilisateur a un des rôles autorisés
    if not any(role.id in RENFORCEMENT_IDS for role in user.roles):
        return await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")

    # Vérifie le cooldown dans MongoDB
    cd_data = collection24.find_one({"user_id": user.id})
    if cd_data and "last_used" in cd_data:
        last_used = cd_data["last_used"]
        if now - last_used < timedelta(days=COOLDOWN_DAYS):
            remaining = (last_used + timedelta(days=COOLDOWN_DAYS)) - now
            hours, minutes = divmod(remaining.total_seconds() // 60, 60)
            return await ctx.send(f"⏳ Tu dois encore attendre {int(hours)}h{int(minutes)} avant de pouvoir réutiliser cette commande.")

    # Donne le rôle temporairement
    role = guild.get_role(RENFORCEMENT_ROLE_ID)
    if not role:
        return await ctx.send("❌ Le rôle de renforcement n'existe pas.")

    await user.add_roles(role, reason="Renforcement activé")

    # Embed joli avec image
    embed = discord.Embed(
        title="💪 Renforcement Activé",
        description=f"Tu as reçu le rôle **{role.name}** pour 24h.",
        color=discord.Color.green(),
        timestamp=now
    )
    embed.set_footer(text="Cooldown de 7 jours")
    embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
    embed.set_image(url="https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20EMBED%20NEN/renfo.jpg?raw=true")  # Ajoute l'image

    await ctx.send(embed=embed)

    # Met à jour le cooldown dans Mongo
    collection24.update_one(
        {"user_id": user.id},
        {"$set": {"last_used": now}},
        upsert=True
    )

    # Attendre 24h puis retirer le rôle
    await asyncio.sleep(DURATION_HOURS * 3600)
    if role in user.roles:
        try:
            await user.remove_roles(role, reason="Renforcement expiré")
            try:
                await user.send("⏳ Ton rôle **Renforcement** a expiré après 24h.")
            except discord.Forbidden:
                pass
        except discord.HTTPException:
            pass

EMISSION_IDS = [1363817593252876368, 1363817609916584057]
TARGET_ROLE_ID = 1363969965572755537 
COOLDOWN_DAYS = 1 

@bot.command(name="emission")
async def emission(ctx, member: discord.Member):
    # Vérification du rôle
    if not any(role.id in EMISSION_IDS for role in ctx.author.roles):
        return await ctx.send("❌ Tu n'as pas le Nen nécessaire pour utiliser cette technique.")

    # Cooldown MongoDB
    cooldown = collection25.find_one({"user_id": ctx.author.id})
    now = datetime.utcnow()
    if cooldown and now < cooldown["next_use"]:
        remaining = cooldown["next_use"] - now
        return await ctx.send(f"⏳ Tu dois attendre encore {remaining.days}j {remaining.seconds // 3600}h.")

    # Appliquer le rôle malus
    role = ctx.guild.get_role(TARGET_ROLE_ID)
    await member.add_roles(role)

    # Enregistrer cooldown
    collection25.update_one(
        {"user_id": ctx.author.id},
        {"$set": {"next_use": now + timedelta(days=COOLDOWN_DAYS)}},
        upsert=True
    )

    # Embed stylé avec image
    embed = discord.Embed(
        title="🌑 Emission : Technique Maudite",
        description=f"{member.mention} a été maudit pendant 24h.\nIl subira un malus de **-20%** sur ses collect !",
        color=discord.Color.dark_purple(),
        timestamp=now
    )
    embed.set_footer(text="Utilisation du Nen : Emission")
    embed.set_image(url="https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20EMBED%20NEN/emission.jpg?raw=true")  # Ajout de l'image

    await ctx.send(embed=embed)

    # Attendre 24h et retirer le rôle
    await asyncio.sleep(86400)  # 24h en secondes
    await member.remove_roles(role)

MANIPULATION_ROLE_ID = 1363974710739861676
AUTHORIZED_MANI_IDS = [1363817593252876368, 1363817536348749875]
COOLDOWN_DAYS = 7

@bot.command(name='manipulation')
@commands.guild_only()
async def manipulation(ctx):
    user = ctx.author
    guild = ctx.guild

    # Vérifie si l'utilisateur a l'un des rôles autorisés
    if not any(role.id in AUTHORIZED_MANI_IDS for role in user.roles):
        return await ctx.send("⛔ Tu n'as pas accès à cette commande.")

    # Vérifie le cooldown en DB
    cooldown_data = collection26.find_one({"user_id": user.id})
    now = datetime.utcnow()

    if cooldown_data and now < cooldown_data["next_available"]:
        remaining = cooldown_data["next_available"] - now
        hours, remainder = divmod(remaining.total_seconds(), 3600)
        minutes = remainder // 60
        return await ctx.send(f"⏳ Tu dois attendre encore {int(hours)}h{int(minutes)}m avant de réutiliser cette commande.")

    # Donne le rôle de manipulation
    role = guild.get_role(MANIPULATION_ROLE_ID)
    if not role:
        return await ctx.send("❌ Le rôle de manipulation est introuvable.")

    await user.add_roles(role)

    # Embed avec image
    embed = discord.Embed(
        title="🧠 Manipulation Activée",
        description="Tu gagnes un **collect de 1%** toutes les 4h pendant 24h.",
        color=discord.Color.blue(),
        timestamp=now
    )
    embed.set_footer(text="Cooldown de 7 jours")
    embed.set_image(url="https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20EMBED%20NEN/image0.jpg?raw=true")  # Ajout de l'image

    await ctx.send(embed=embed)

    # Mets à jour le cooldown
    next_available = now + timedelta(days=COOLDOWN_DAYS)
    collection26.update_one(
        {"user_id": user.id},
        {"$set": {"next_available": next_available}},
        upsert=True
    )

    # Supprime le rôle après 24h
    await asyncio.sleep(86400)
    await user.remove_roles(role)
    try:
        await user.send("💤 Ton effet **Manipulation** est terminé.")
    except discord.Forbidden:
        pass

import random
from datetime import datetime, timedelta
import discord

# ID d'objets matérialisables
MATERIALISATION_IDS = [1363817636793810966, 1363817593252876368]

# IDs d'items interdits à la matérialisation
ITEMS_INTERDITS = [202, 197, 425, 736, 872, 964, 987]

# Cooldown en heures
MATERIALISATION_COOLDOWN_HOURS = 6

@bot.command(name="materialisation")
async def materialisation(ctx):
    user_id = ctx.author.id
    guild_id = ctx.guild.id
    now = datetime.utcnow()

    # Vérifie le cooldown
    cd_doc = collection27.find_one({"user_id": user_id, "guild_id": guild_id})
    if cd_doc:
        last_use = cd_doc.get("last_use")
        if last_use and now < last_use + timedelta(hours=MATERIALISATION_COOLDOWN_HOURS):
            remaining = (last_use + timedelta(hours=MATERIALISATION_COOLDOWN_HOURS)) - now
            hours, remainder = divmod(remaining.total_seconds(), 3600)
            minutes = remainder // 60
            embed = discord.Embed(
                title="⏳ Cooldown actif",
                description=f"Tu dois encore attendre **{int(hours)}h {int(minutes)}m** avant de matérialiser un item.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

    # Récupère un item aléatoire de la boutique (en stock uniquement, et pas interdit)
    items = list(collection16.find({
        "quantity": {"$gt": 0},
        "id": {"$in": MATERIALISATION_IDS, "$nin": ITEMS_INTERDITS}
    }))
    
    if not items:
        embed = discord.Embed(
            title="❌ Aucun item disponible",
            description="Il n'y a pas d'items à matérialiser actuellement.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    selected_item = random.choice(items)

    # Met à jour l'inventaire simple
    existing = collection7.find_one({"user_id": user_id, "guild_id": guild_id})
    if existing:
        inventory = existing.get("items", {})
        inventory[str(selected_item["id"])] = inventory.get(str(selected_item["id"]), 0) + 1
        collection7.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": {"items": inventory}}
        )
    else:
        collection7.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "items": {str(selected_item["id"]): 1}
        })

    # Ajoute à l'inventaire structuré
    collection17.insert_one({
        "guild_id": guild_id,
        "user_id": user_id,
        "item_id": selected_item["id"],
        "item_name": selected_item["title"],
        "emoji": selected_item.get("emoji"),
        "price": selected_item["price"],
        "obtained_at": now
    })

    # Met à jour le cooldown
    collection27.update_one(
        {"user_id": user_id, "guild_id": guild_id},
        {"$set": {"last_use": now}},
        upsert=True
    )

    # Message de confirmation avec image
    embed = discord.Embed(
        title="✨ Matérialisation réussie",
        description=f"Tu as matérialisé **{selected_item['emoji']} {selected_item['title']}** !",
        color=discord.Color.green()
    )
    embed.set_image(url="https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20EMBED%20NEN/Materi.png?raw=true")
    await ctx.send(embed=embed)

@bot.command(
    name="transformation",
    description="Transforme ton aura en éclair et foudroie la banque d'un autre joueur pour lui retirer 25% de son solde bancaire.",
)
async def transformation(ctx: commands.Context, target: discord.User):
    # Vérifier si l'utilisateur a un des rôles autorisés
    if not any(role.id in [1363817593252876368, 1363817619529924740] for role in ctx.author.roles):
        return await ctx.send("Désolé, tu n'as pas le rôle nécessaire pour utiliser cette commande.")

    # Vérifier si l'utilisateur cible est valide
    if target == ctx.author:
        return await ctx.send("Tu ne peux pas utiliser cette commande sur toi-même.")

    guild_id = ctx.guild.id
    user_id = ctx.author.id
    target_id = target.id

    # Vérifier le cooldown
    cooldown_data = collection28.find_one({"guild_id": guild_id, "user_id": user_id})
    if cooldown_data:
        last_used = cooldown_data.get("last_used")
        if last_used and (datetime.utcnow() - last_used).days < 14:
            remaining_days = 14 - (datetime.utcnow() - last_used).days
            return await ctx.send(f"Tu as déjà utilisé cette commande récemment. Essaie dans {remaining_days} jours.")

    # Récupérer les données de la banque de la cible
    target_data = collection.find_one({"guild_id": guild_id, "user_id": target_id})
    if not target_data:
        target_data = {"guild_id": guild_id, "user_id": target_id, "cash": 0, "bank": 0}
        collection.insert_one(target_data)

    # Calculer la perte de la banque de la cible (25%)
    bank_loss = target_data.get("bank", 0) * 0.25
    new_bank_balance = target_data["bank"] - bank_loss

    # Mettre à jour la banque de la cible
    collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$set": {"bank": new_bank_balance}})

    # Enregistrer le temps de la dernière utilisation pour le cooldown
    collection28.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_used": datetime.utcnow()}},
        upsert=True,
    )

    # Log de l'action
    await log_eco_channel(
        bot=ctx.bot,
        guild_id=guild_id,
        user=ctx.author,
        action="Foudroie la banque de",
        amount=bank_loss,
        balance_before=target_data["bank"],
        balance_after=new_bank_balance,
        note=f"Transformation de l'aura en éclair. Perte de 25% de la banque de {target.display_name}."
    )

    # Embed stylé avec image
    embed = discord.Embed(
        title="⚡ Transformation : Aura en Éclair",
        description=f"Tu as transformé ton aura en éclair et foudroyé la banque de {target.display_name}, lui retirant {bank_loss:.2f} d'Ether.",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Utilisation du Nen : Transformation")
    embed.set_image(url="https://github.com/Iseyg91/Isey_aime_Cass/blob/main/IMAGE%20EMBED%20NEN/Transfo.jpg?raw=true")  # Ajout de l'image

    await ctx.send(embed=embed)

# ID du rôle autorisé à utiliser la commande
HEAL_ID = 1363873859912335400
MALUS_ROLE_ID = 1363969965572755537

# Commande .heal
@bot.command()
async def heal(ctx):
    # Vérifier si l'utilisateur a le rôle requis
    if HEAL_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("Désolé, vous n'avez pas l'autorisation de retirer ce Nen.")
        return

    # Retirer le rôle malus à la personne
    malus_role = discord.utils.get(ctx.guild.roles, id=MALUS_ROLE_ID)
    if malus_role in ctx.author.roles:
        await ctx.author.remove_roles(malus_role)
        await ctx.send(f"Le rôle malus a été retiré à {ctx.author.mention}.")

    # Retirer le rôle de soin (HEAL_ID)
    heal_role = discord.utils.get(ctx.guild.roles, id=HEAL_ID)
    if heal_role in ctx.author.roles:
        await ctx.author.remove_roles(heal_role)
        await ctx.send(f"Le rôle de soin a été retiré à {ctx.author.mention}.")

    # Créer l'embed avec l'image spécifiée
    embed = discord.Embed(title="Soin Exorciste", description="Le Nen a été retiré grâce à l'exorciste.", color=discord.Color.green())
    embed.set_image(url="https://preview.redd.it/q1xtzkr219371.jpg?width=1080&crop=smart&auto=webp&s=ce05b77fe67949cc8f6c39c01a9dd93c77af1fe8")

    # Envoyer l'embed
    await ctx.send(embed=embed)

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARME_DEMONIAQUE_ID = 1363817586466361514

@bot.command(name="imperial")
async def imperial(ctx, cible: discord.Member = None):
    auteur = ctx.author

    # Vérification si la cible est précisée
    if not cible:
        logger.warning(f"{auteur} a tenté d'utiliser la commande 'imperial' sans spécifier de cible.")
        return await ctx.send("❌ Tu dois spécifier une cible pour utiliser cette commande.")

    # Vérifie que l'utilisateur a le rôle spécial
    if ARME_DEMONIAQUE_ID not in [r.id for r in auteur.roles]:
        return await ctx.send("❌ Tu n'as pas le pouvoir démoniaque pour utiliser cette commande.")

    # Vérifie que la cible n'est pas un bot
    if cible.bot:
        return await ctx.send("❌ Tu ne peux pas cibler un bot.")

    # Vérifie que l'utilisateur ne cible pas lui-même
    if auteur.id == cible.id:
        return await ctx.send("❌ Tu ne peux pas te voler toi-même.")

    guild_id = ctx.guild.id

    def get_or_create_user_data(user_id):
        data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
        if not data:
            logger.info(f"Création de données pour l'utilisateur {user_id}")
            data = {"guild_id": guild_id, "user_id": user_id, "cash": 1500, "bank": 0}
            collection.insert_one(data)
        return data

    data_auteur = get_or_create_user_data(auteur.id)
    data_cible = get_or_create_user_data(cible.id)

    if "cash" not in data_cible or "bank" not in data_cible:
        logger.warning(f"Les données de {cible.id} sont corrompues. Création de nouvelles données.")
        data_cible["cash"] = 1500
        data_cible["bank"] = 0
        collection.update_one(
            {"guild_id": guild_id, "user_id": cible.id},
            {"$set": {"cash": 1500, "bank": 0}}
        )

    try:
        total_auteur = data_auteur["cash"] + data_auteur["bank"]
        total_cible = data_cible["cash"] + data_cible["bank"]
    except KeyError as e:
        logger.error(f"Erreur d'accès aux données : {e}")
        return await ctx.send(f"❌ Une erreur est survenue lors de l'accès aux données de {cible.display_name}.")

    if total_cible <= total_auteur:
        return await ctx.send("❌ Tu ne peux voler que quelqu'un de plus riche que toi.")

    roll = random.randint(1, 50)
    pourcentage = roll / 100
    vol_total = int(total_cible * pourcentage)

    vol_cash = min(vol_total, data_cible["cash"])
    vol_bank = vol_total - vol_cash

    if vol_total > total_cible:
        return await ctx.send("❌ Il n'y a pas assez de fonds disponibles à voler.")

    collection.update_one(
        {"guild_id": guild_id, "user_id": cible.id},
        {"$inc": {"cash": -vol_cash, "bank": -vol_bank}}
    )
    collection.update_one(
        {"guild_id": guild_id, "user_id": auteur.id},
        {"$inc": {"cash": vol_total}}
    )

    role = ctx.guild.get_role(ARME_DEMONIAQUE_ID)
    if role is None:
        logger.error(f"Le rôle ARME_DEMONIAQUE_ID ({ARME_DEMONIAQUE_ID}) n'a pas été trouvé.")
        return await ctx.send("❌ Le rôle d'arme démoniaque n'existe pas.")
    
    await auteur.remove_roles(role)

    emoji_currency = "<:ecoEther:1341862366249357374>"
    embed = discord.Embed(
        title="Pouvoir Impérial Démoniaque Utilisé !",
        description=(
            f"**{auteur.mention}** a utilisé son arme démoniaque sur **{cible.mention}** !\n"
            f"🎲 Le démon a jugé ton vol à **{roll}%** !\n"
            f"💸 Tu lui as volé **{vol_total:,} {emoji_currency}** !"
        ),
        color=discord.Color.dark_red()
    )
    embed.set_image(url="https://pm1.aminoapps.com/6591/d1e3c1527dc792f004068d914ca00c411031ccd2_hq.jpg")
    
    await ctx.send(embed=embed)

# ID des rôles
HAKI_ROI_ID = 1363817645249527879
HAKI_SUBIS_ID = 1364109450197078026  # Rôle attribué pendant 7 jours

async def is_on_cooldown(user_id):
    print(f"[LOG] Recherche du cooldown MongoDB pour {user_id}")
    cooldown = collection30.find_one({"user_id": user_id})
    if cooldown:
        last_used = cooldown["last_used"]
        print(f"[LOG] Dernière utilisation trouvée : {last_used} ({type(last_used)})")
        cooldown_time = timedelta(weeks=2)
        if datetime.utcnow() - last_used < cooldown_time:
            print("[LOG] Cooldown actif")
            return True
        else:
            print("[LOG] Cooldown expiré")
    else:
        print("[LOG] Aucun cooldown trouvé pour cet utilisateur")
    return False

async def apply_haki_role(ctx, user):
    try:
        print("[LOG] Début de apply_haki_role")

        print(f"[LOG] Vérification du cooldown pour l'utilisateur : {user.id}")
        if await is_on_cooldown(user.id):
            print("[LOG] Utilisateur encore en cooldown")
            await ctx.send(f"{user.mention} doit attendre 2 semaines avant d'être ciblé à nouveau.")
            return
        print("[LOG] Utilisateur pas en cooldown")

        role = discord.utils.get(ctx.guild.roles, id=HAKI_SUBIS_ID)
        if not role:
            print("[ERREUR] Rôle Haki non trouvé dans le serveur")
            await ctx.send("Erreur : le rôle Haki à attribuer n'a pas été trouvé.")
            return
        print(f"[LOG] Rôle trouvé : {role.name}")

        await user.add_roles(role)
        print(f"[LOG] Rôle ajouté à {user.name}")
        await ctx.send(f"{user.mention} a été paralysé avec le Haki des Rois pour 7 jours.")

        now = datetime.utcnow()
        print(f"[LOG] Mise à jour du cooldown à {now}")
        collection30.update_one(
            {"user_id": user.id},
            {"$set": {"last_used": now}},
            upsert=True
        )
        print("[LOG] Cooldown enregistré en base de données")

        print("[LOG] Attente 7 jours (asyncio.sleep)")
        await asyncio.sleep(7 * 24 * 60 * 60)

        await user.remove_roles(role)
        print(f"[LOG] Rôle retiré de {user.name}")
        await ctx.send(f"{user.mention} est maintenant libéré du Haki des Rois.")

    except Exception as e:
        print(f"[ERREUR] Exception dans apply_haki_role : {type(e).__name__} - {e}")
        await ctx.send(f"Une erreur est survenue pendant l'application du Haki : `{type(e).__name__} - {e}`")


# Commande .haki
@bot.command()
@commands.has_role(HAKI_ROI_ID)
async def haki(ctx, user: discord.Member):
    """Applique le Haki des Rois à un utilisateur."""

    # Embed d'annonce
    embed = discord.Embed(
        title="⚡ Haki des Rois ⚡",
        description=f"{user.mention} a été frappé par le Haki des Rois !",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )
    embed.set_image(url="https://static.wikia.nocookie.net/onepiece/images/4/42/Haoshoku_Haki_Choc.png/revision/latest?cb=20160221111336&path-prefix=fr")
    await ctx.send(embed=embed)

    # Application du Haki
    await apply_haki_role(ctx, user)

@haki.error
async def haki_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        print("[ERREUR] Permission manquante pour utiliser .haki")
        await ctx.send("Vous n'avez pas le rôle requis pour utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        print("[ERREUR] Argument manquant : utilisateur")
        await ctx.send("Vous devez mentionner un utilisateur : `.haki @utilisateur`")
    else:
        print(f"[ERREUR] Erreur dans haki : {type(error).__name__} - {error}")
        await ctx.send("Une erreur est survenue lors de l'exécution de la commande.")

ULTRA_ID = 1363821033060307106

class MissingUltraRole(commands.CheckFailure):
    pass

@bot.command(name="ultra")
@commands.cooldown(1, 432000, commands.BucketType.user)  # 432000 sec = 5 jours
async def ultra(ctx):
    # Vérifie si l'utilisateur a le rôle ULTRA
    if not any(role.id == ULTRA_ID for role in ctx.author.roles):
        raise MissingUltraRole()

    embed = discord.Embed(
        title="☁️ Ultra Instinct ☁️",
        description=(
            "Vous utilisez la **forme ultime du Ultra Instinct**.\n"
            "Pendant un certain temps, vous **esquivez toutes les attaques** et devenez **totalement immunisé**.\n\n"
            "⚠️ Cette forme utilise énormément de votre ki...\n"
            "⏳ Il vous faudra **5 jours** de repos avant de pouvoir l'utiliser à nouveau."
        ),
        color=discord.Color.purple()
    )
    embed.set_image(url="https://dragonballsuper-france.fr/wp-content/uploads/2022/05/Dragon-Ball-Legends-Goku-Ultra-Instinct.jpg")
    embed.set_footer(text=f"Activé par {ctx.author.display_name}")

    await ctx.send(embed=embed)

@ultra.error
async def ultra_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = str(timedelta(seconds=int(error.retry_after)))
        await ctx.send(f"🕒 Vous devez attendre encore **{remaining}** avant de réutiliser cette forme ultime.")
    elif isinstance(error, MissingUltraRole):
        await ctx.send("❌ Vous n'avez pas la puissance nécessaire pour utiliser cette commande.")
    else:
        await ctx.send("⚠️ Une erreur inconnue s'est produite.")

import discord
from discord.ext import commands
from datetime import datetime
import random
import traceback  # pour logs d'erreurs détaillés

# Paramètres
RAGE_ID = 1363821333624127618
ECLIPSE_ROLE_ID = 1364115033197510656
BerserkCooldown = {}

@bot.command(name="berserk")
@commands.cooldown(1, 604800, commands.BucketType.user)  # 7 jours cooldown
async def berserk(ctx, target: discord.Member = None):
    if ctx.guild is None:
        return await ctx.send("Cette commande ne peut être utilisée qu'en serveur.")

    # Check rôle
    if RAGE_ID not in [role.id for role in ctx.author.roles]:
        return await ctx.send("Tu n'as pas le rôle nécessaire pour utiliser cette commande.")

    if target is None or target.bot or target == ctx.author:
        return await ctx.send("Tu dois cibler un autre utilisateur valide.")

    guild_id = ctx.guild.id
    author_id = ctx.author.id
    target_id = target.id

    roll = random.randint(1, 100)

    # Récupération des données
    author_data = get_or_create_user_data(guild_id, author_id)
    target_data = get_or_create_user_data(guild_id, target_id)

    result = ""
    image_url = "https://github.com/Iseyg91/Isey_aime_Cass/blob/main/unnamed.jpg?raw=true"

    # Logique du roll
    if roll <= 10:
        perte = int(author_data["bank"] * 0.15)
        collection.update_one({"guild_id": guild_id, "user_id": author_id}, {"$inc": {"bank": -perte}})
        result = f"🎲 Roll: {roll}\n⚠️ L’armure se retourne contre toi ! Tu perds **15%** de ta propre banque soit **{perte:,}**."

    elif roll == 100:
        perte = target_data["bank"]
        collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$inc": {"bank": -perte}})

        eclipse_role = ctx.guild.get_role(ECLIPSE_ROLE_ID)
        if eclipse_role:
            try:
                await ctx.author.add_roles(eclipse_role)
            except discord.Forbidden:
                await ctx.send("❌ Je n’ai pas les permissions pour te donner le rôle Éclipse.")
            except Exception as e:
                await ctx.send(f"❌ Une erreur est survenue lors de l’ajout du rôle : {e}")
        else:
            await ctx.send("⚠️ Le rôle Éclipse n’a pas été trouvé sur le serveur.")

        result = (
            f"🎲 Roll: {roll}\n💥 **Effet Éclipse !**\n"
            f"→ {target.mention} perd **100%** de sa banque soit **{perte:,}**.\n"
            f"→ Tu deviens **L’incarnation de la Rage**."
        )

    else:
        perte = int(target_data["bank"] * (roll / 100))
        collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$inc": {"bank": -perte}})
        result = (
            f"🎲 Roll: {roll}\n🎯 {target.mention} perd **{roll}%** de sa banque soit **{perte:,}**.\n"
            f"Tu ne gagnes rien. Juste le chaos."
        )

    # Embed du résultat
    embed = discord.Embed(title="🔥 Berserk Activé ! 🔥", description=result, color=discord.Color.red())
    embed.set_image(url=image_url)
    embed.set_footer(text=f"Par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

@berserk.error
async def berserk_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown = datetime.timedelta(seconds=error.retry_after)
        await ctx.send(f"⏳ Cette commande est en cooldown. Réessaie dans {cooldown}.")
    else:
        raise error

ARMURE_ID = 1363821649002238142
ANTI_ROB_ID = 1363964754678513664

@bot.command()
async def armure(ctx):
    # Vérifie si l'utilisateur a le rôle d'armure
    if ARMURE_ID in [role.id for role in ctx.author.roles]:
        # Retirer immédiatement le rôle d'armure
        armure_role = discord.utils.get(ctx.guild.roles, id=ARMURE_ID)
        await ctx.author.remove_roles(armure_role)
        
        # Ajouter le rôle anti-rob
        anti_rob_role = discord.utils.get(ctx.guild.roles, id=ANTI_ROB_ID)
        await ctx.author.add_roles(anti_rob_role)
        
        # Créer l'embed
        embed = Embed(
            title="Anti-Rob Activé",
            description="Vous avez reçu un anti-rob pour 1 heure !",
            color=discord.Color.green()
        )
        embed.set_image(url="https://miro.medium.com/v2/resize:fit:1024/0*wATbQ49jziZTyhZH.jpg")
        
        # Envoyer l'embed
        await ctx.send(embed=embed)

        # Attendre 1 heure (3600 secondes)
        await asyncio.sleep(3600)

        # Retirer le rôle anti-rob après 1 heure
        await ctx.author.remove_roles(anti_rob_role)
        await ctx.send(f"L'anti-rob de {ctx.author.mention} a expiré.")
    else:
        await ctx.send("Vous n'avez pas le rôle nécessaire pour utiliser cette commande.")

# Les IDs des rôles
INFINI_ID = [1363939565336920084, 1363939567627145660, 1363939486844850388]
ANTI_ROB_ROLE = 1363964754678513664

# Lien des images selon le niveau
images = {
    1: "https://preview.redd.it/zovgpfd6g6od1.jpeg?auto=webp&s=59768167ffc7b8d39072709119686464e7cbddff",
    2: "https://i0.wp.com/www.lerenardmasque.com/wp-content/uploads/2023/08/Capture-decran-2023-08-16-a-13.29.09.png?resize=960%2C419&ssl=1",
    3: "https://i0.wp.com/www.lerenardmasque.com/wp-content/uploads/2023/08/Capture-decran-2023-08-16-a-13.34.03-1.png?resize=960%2C498&ssl=1"
}

# Dictionnaire pour stocker le temps d'expiration de chaque utilisateur
user_anti_rob_expiry = {}

# Commande .infini
@bot.command()
async def infini(ctx):
    member = ctx.author
    current_time = datetime.utcnow()

    # Vérifier si l'utilisateur a déjà un anti-rob actif
    if member.id in user_anti_rob_expiry:
        expiry_time = user_anti_rob_expiry[member.id]
        if current_time < expiry_time:
            remaining_time = expiry_time - current_time
            await ctx.send(f"Vous avez déjà un anti-rob actif. Il expire dans {str(remaining_time).split('.')[0]}.")
            return

    roles = member.roles

    # Vérification des rôles et assignation de l'anti-rob
    for role_id in INFINI_ID:
        role = discord.utils.get(roles, id=role_id)
        if role:
            if role.id == INFINI_ID[0]:
                anti_rob_duration = 1  # 1h pour Niv 1
                image_url = images[1]
            elif role.id == INFINI_ID[1]:
                anti_rob_duration = 3  # 3h pour Niv 2
                image_url = images[2]
            elif role.id == INFINI_ID[2]:
                anti_rob_duration = 6  # 6h pour Niv 3
                image_url = images[3]
            
            # Retirer immédiatement le rôle INFINI_ID
            await member.remove_roles(role)
            print(f"Rôle {role.name} retiré de {member.name}")

            # Ajouter le rôle anti-rob
            anti_rob_role = discord.utils.get(member.guild.roles, id=ANTI_ROB_ROLE)
            await member.add_roles(anti_rob_role)
            print(f"Rôle anti-rob ajouté à {member.name}")

            # Enregistrer l'heure d'expiration de l'anti-rob
            expiry_time = current_time + timedelta(hours=anti_rob_duration)
            user_anti_rob_expiry[member.id] = expiry_time

            # Créer un embed pour afficher le message
            embed = discord.Embed(title="Anti-Rob Activé", description=f"Vous avez reçu un anti-rob de {anti_rob_duration} heure(s).", color=0x00ff00)
            embed.set_image(url=image_url)
            embed.timestamp = current_time

            # Envoyer le message avec l'embed
            await ctx.send(embed=embed)
            break
    else:
        await ctx.send("Vous n'avez pas le rôle nécessaire pour utiliser cette commande.")

# ID du Pokeball (rôle autorisé à utiliser la commande)
POKEBALL_ID = 1363942048075481379  # Remplacez par l'ID réel du rôle autorisé

# Limite d'utilisation par semaine
last_used = {}

# Fonction pour vérifier l'accès basé sur le rôle
async def has_authorized_role(user):
    return any(role.id == POKEBALL_ID for role in user.roles)

# Commande pokeball
@bot.command(name="pokeball", description="Permet de voler un objet à une personne spécifique.")
async def pokeball(ctx, target: discord.Member = None):
    user = ctx.author
    
    # Vérifier si l'utilisateur a le bon rôle
    if not await has_authorized_role(user):
        await ctx.send("Vous n'avez pas l'autorisation d'utiliser cette commande.")
        return
    
    # Vérifier la limite d'utilisation hebdomadaire
    current_time = datetime.now()
    if user.id in last_used:
        time_diff = current_time - last_used[user.id]
        if time_diff < timedelta(weeks=1):
            await ctx.send("Vous avez déjà utilisé cette commande cette semaine. Réessayez plus tard.")
            return
    
    # Si aucune cible n'est spécifiée, l'utilisateur doit mentionner un membre
    if target is None:
        await ctx.send("Veuillez mentionner un membre à qui voler un objet.")
        return
    
    # Vérifier que la cible n'est pas un bot
    if target.bot:
        await ctx.send("Vous ne pouvez pas voler des objets à un bot.")
        return
    
    # Récupérer l'inventaire de l'utilisateur choisi
    guild = ctx.guild
    items_cursor = collection17.find({"guild_id": guild.id, "user_id": target.id})
    items = list(items_cursor)

    if not items:
        await ctx.send(f"{target.name} n'a pas d'objets dans son inventaire.")
        return

    # Voler un objet au hasard
    stolen_item = random.choice(items)
    item_name = stolen_item.get("item_name", "Nom inconnu")
    item_emoji = stolen_item.get("emoji", "")
    
    # Supprimer l'objet volé de l'inventaire de la victime
    collection17.delete_one({"_id": stolen_item["_id"]})
    
    # Ajouter l'objet volé à l'inventaire de l'utilisateur
    collection17.insert_one({
        "guild_id": guild.id,
        "user_id": user.id,
        "item_id": stolen_item["item_id"],
        "item_name": item_name,
        "emoji": item_emoji
    })

    # Mettre à jour la dernière utilisation
    last_used[user.id] = current_time
    
    # Embed de la réponse
    embed = discord.Embed(
        title="Pokeball utilisée avec succès !",
        description=f"Vous avez volé **1x {item_name} {item_emoji}** à {target.name}.",
        color=discord.Color.green()
    )
    embed.set_image(url="https://fr.web.img2.acsta.net/newsv7/20/03/19/15/11/26541590.jpg")
    embed.set_footer(text="Utilisation 1x par semaine.")
    
    await ctx.send(embed=embed)

# Identifiants
FLOAT_ID = 1363946902730575953
ROLE_ID = 1364121382908067890

# Maintenant, vous pouvez utiliser timedelta directement
COOLDOWN_TIME = timedelta(days=1)

# Dictionnaire pour stocker le dernier usage de la commande .float par utilisateur
float_last_used = {}

# URL de l'image
image_url = "https://preview.redd.it/vczetgcwdrge1.jpeg?auto=webp&s=7c04e8249d0ee9f8e231c5940aafecb7a2c5a2ca"

@bot.command()
async def float(ctx):
    # Vérifie si l'utilisateur a le bon rôle
    if FLOAT_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("Tu n'as pas le rôle nécessaire pour utiliser cette commande.")
        return
    
    current_time = datetime.datetime.now()
    last_used_time = float_last_used.get(ctx.author.id)

    # Vérifie si l'utilisateur a déjà utilisé la commande dans les dernières 24 heures
    if last_used_time and current_time - last_used_time < COOLDOWN_TIME:
        await ctx.send("Tu as déjà utilisé cette commande aujourd'hui. Patiente avant de réessayer.")
        return

    # Ajoute le rôle nécessaire à l'utilisateur
    role = ctx.guild.get_role(ROLE_ID)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention}, tu as maintenant accès au salon pendant 15 minutes.")
        
        # Envoie l'embed avec l'image
        embed = discord.Embed(
            title="Utilisation du pouvoir de Nana Shimura",
            description="Tu as utilisé un des alters de One for All et tu accèdes au salon pendant 15 minutes.",
            color=discord.Color.blue()
        )
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

        # Met à jour le dernier usage de la commande
        float_last_used[ctx.author.id] = current_time

        # Programme la suppression du rôle après 15 minutes
        await asyncio.sleep(15 * 60)
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention}, ton accès au salon est maintenant terminé.")
    else:
        await ctx.send("Le rôle nécessaire n'a pas pu être trouvé.")

# Identifiants
OEIL_ID = 1363949082653098094
ROLE_ID = 1364123507532890182
from datetime import timedelta

COOLDOWN_TIME = timedelta(weeks=1)

# Dictionnaire pour stocker le dernier usage de la commande .oeil par utilisateur
oeil_last_used = {}

# URL de l'image
image_url = "https://static0.gamerantimages.com/wordpress/wp-content/uploads/2023/09/rudeus-demon-eye-mushoku-tensei.jpg"

@bot.command()
async def oeil(ctx):
    # Vérifie si l'utilisateur a le bon rôle
    if OEIL_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("Tu n'as pas le rôle nécessaire pour utiliser cette commande.")
        return
    
    current_time = datetime.datetime.now()
    last_used_time = oeil_last_used.get(ctx.author.id)

    # Vérifie si l'utilisateur a déjà utilisé la commande dans les dernières 1 semaine
    if last_used_time and current_time - last_used_time < COOLDOWN_TIME:
        await ctx.send("Tu as déjà utilisé cette commande cette semaine. Patiente avant de réessayer.")
        return

    # Ajoute le rôle nécessaire à l'utilisateur
    role = ctx.guild.get_role(ROLE_ID)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention}, tu as utilisé le pouvoir de Kishirika pour voir l'avenir pendant 10 secondes.")
        
        # Envoie l'embed avec l'image
        embed = discord.Embed(
            title="Le pouvoir de Kishirika",
            description="Tu entrevois le prochain restock pendant 10 secondes grâce au pouvoir de Kishirika.",
            color=discord.Color.purple()
        )
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

        # Met à jour le dernier usage de la commande
        oeil_last_used[ctx.author.id] = current_time

        # Programme la suppression du rôle après 10 secondes
        await asyncio.sleep(10)
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention}, ton accès au pouvoir de voir l'avenir est maintenant terminé.")

    else:
        await ctx.send("Le rôle nécessaire n'a pas pu être trouvé.")

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

# Fonction pour insérer des quêtes de départ dans la base de données
def insert_quetes_into_db():
    # Quêtes à insérer au démarrage
    quetes_debut = [
        {"id": 1, "nom": "Quête de début", "description": "Commencez votre aventure !", "emoji": "🌟", "recompense": "100"},
        {"id": 2, "nom": "Quête de récolte", "description": "Récoltez des ressources.", "emoji": "🌾", "recompense": "200"}
    ]
    
    for quete in quetes_debut:
        # Vérifier si la quête existe déjà dans la base de données
        if not collection32.find_one({"id": quete["id"]}):
            collection32.insert_one(quete)

@bot.tree.command(name="add-quete", description="Ajoute une nouvelle quête.")
@app_commands.describe(
    quest_id="L'ID unique de la quête",
    nom="Nom de la quête",
    description="Description de la quête",
    reward_item_id="ID de l'item en récompense (doit exister dans la boutique)",
    reward_coins="Montant de pièces en récompense"
)
async def add_quete(interaction: discord.Interaction, quest_id: int, nom: str, description: str, reward_item_id: int, reward_coins: int):
    if interaction.user.id != 792755123587645461:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    # Vérifie que l'item existe
    item = collection16.find_one({"id": reward_item_id})
    if not item:
        return await interaction.response.send_message("❌ L'item spécifié n'existe pas dans la boutique.", ephemeral=True)

    existing = collection32.find_one({"id": quest_id})
    if existing:
        return await interaction.response.send_message("❌ Une quête avec cet ID existe déjà.", ephemeral=True)

    quest = {
        "id": quest_id,
        "nom": nom,
        "description": description,
        "reward_item_id": reward_item_id,
        "reward_coins": reward_coins
    }

    collection32.insert_one(quest)
    await interaction.response.send_message(f"✅ Quête **{nom}** ajoutée avec succès !", ephemeral=True)

@bot.tree.command(name="quetes", description="Affiche la liste des quêtes disponibles")
async def quetes(interaction: discord.Interaction):
    quests = list(collection32.find({}))

    if not quests:
        return await interaction.response.send_message("❌ Aucune quête enregistrée.", ephemeral=True)

    # Créez l'embed avec l'utilisateur comme auteur
    embed = discord.Embed(title=f"Quêtes disponibles", color=discord.Color.blue())
    
    # Ajout de la photo de profil de l'utilisateur
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)

    # Ajout de l'emoji personnalisé en haut à droite
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1364316821196640306.png")  # Utilisation du lien direct pour l'emoji personnalisé

    for quest in quests:
        item = collection16.find_one({"id": quest["reward_item_id"]})
        item_name = item["title"] if item else "Inconnu"
        item_emoji = item["emoji"] if item else ""

        embed.add_field(
            name=f"🔹 {quest['nom']} (ID: {quest['id']})",
            value=f"{quest['description']}\n**Récompense**: {item_name} {item_emoji} + {quest['reward_coins']} <:ecoEther:1341862366249357374>",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="quete-faite", description="Valide une quête et donne les récompenses à un utilisateur.")
@app_commands.describe(quest_id="ID de la quête", user="Utilisateur à récompenser")
async def quete_faite(interaction: discord.Interaction, quest_id: int, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    quest = collection32.find_one({"id": quest_id})
    if not quest:
        return await interaction.response.send_message("❌ Quête introuvable.", ephemeral=True)

    # Ajouter item dans l'inventaire
    collection17.insert_one({
        "guild_id": interaction.guild.id,
        "user_id": user.id,
        "item_id": quest["reward_item_id"],
        "item_name": collection16.find_one({"id": quest["reward_item_id"]})["title"],
        "emoji": collection16.find_one({"id": quest["reward_item_id"]})["emoji"]
    })

    # Ajouter des coins
    user_data = collection.find_one({"guild_id": interaction.guild.id, "user_id": user.id})
    if not user_data:
        user_data = {"guild_id": interaction.guild.id, "user_id": user.id, "cash": 0, "bank": 0}
        collection.insert_one(user_data)

    new_cash = user_data["cash"] + quest["reward_coins"]
    collection.update_one(
        {"guild_id": interaction.guild.id, "user_id": user.id},
        {"$set": {"cash": new_cash}}
    )

    await interaction.response.send_message(
        f"✅ Récompenses de la quête **{quest['nom']}** données à {user.mention} !",
        ephemeral=True
    )

@bot.tree.command(name="reset-quetes", description="Supprime toutes les quêtes (ADMIN)")
async def reset_quetes(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("Tu n'as pas l'autorisation d'utiliser cette commande.", ephemeral=True)
        return

    result = collection32.delete_many({})
    await interaction.response.send_message(f"🧹 Collection `ether_quetes` reset avec succès. {result.deleted_count} quêtes supprimées.")


BENEDICTION_ROLE_ID = 1364294230343684137  # Rôle autorisé à utiliser la commande

@bot.command(name="benediction")
async def benediction(ctx):
    user_id = ctx.author.id
    guild_id = ctx.guild.id
    now = datetime.utcnow()

    # Vérifie si l'utilisateur a le rôle requis
    if BENEDICTION_ROLE_ID not in [role.id for role in ctx.author.roles]:
        embed = discord.Embed(
            title="❌ Accès refusé",
            description="Tu n'as pas le rôle nécessaire pour recevoir la bénédiction d'Etherya.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    # Récupère un item aléatoire de la boutique (en stock uniquement, et pas interdit)
    items = list(collection16.find({
        "quantity": {"$gt": 0},
        "id": {"$nin": ITEMS_INTERDITS}
    }))
    
    if not items:
        embed = discord.Embed(
            title="❌ Aucun item disponible",
            description="Il n'y a pas d'items à matérialiser actuellement.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    selected_item = random.choice(items)

    # Met à jour l'inventaire simple
    existing = collection7.find_one({"user_id": user_id, "guild_id": guild_id})
    if existing:
        inventory = existing.get("items", {})
        inventory[str(selected_item["id"])] = inventory.get(str(selected_item["id"]), 0) + 1
        collection7.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": {"items": inventory}}
        )
    else:
        collection7.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "items": {str(selected_item["id"]): 1}
        })

    # Ajoute à l'inventaire structuré
    collection17.insert_one({
        "guild_id": guild_id,
        "user_id": user_id,
        "item_id": selected_item["id"],
        "item_name": selected_item["title"],
        "emoji": selected_item.get("emoji"),
        "price": selected_item["price"],
        "obtained_at": now
    })

    # Retire le rôle après utilisation
    role = discord.utils.get(ctx.guild.roles, id=BENEDICTION_ROLE_ID)
    if role:
        await ctx.author.remove_roles(role)

    # Message de confirmation avec image et texte modifié
    embed = discord.Embed(
        title="🌟 Bénédiction d'Etherya",
        description=(
            "La bénédiction d'Etherya t'a été accordée ! **La Divinité t'a offert un cadeau précieux pour "
            "ta quête. Que ce pouvoir guide tes pas vers la victoire !**\n\n"
            f"Tu as reçu **{selected_item['emoji']} {selected_item['title']}** pour ta bravoure et ta foi."
        ),
        color=discord.Color.green()
    )
    embed.set_image(url="https://imgsrv.crunchyroll.com/cdn-cgi/image/fit=contain,format=auto,quality=70,width=1200,height=675/catalog/crunchyroll/59554268b0e9e3e565547ab4e25453f4.jpg")
    await ctx.send(embed=embed)

@bot.command(name="gcreate")
async def creer_guilde(ctx):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    # Vérifier s'il est déjà dans une guilde
    guilde_existante = collection35.find_one({"guild_id": guild_id, "membres.user_id": user_id})
    if guilde_existante:
        return await ctx.send("Tu es déjà dans une guilde.")

    # Vérifier les coins
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not user_data or user_data.get("cash", 0) < 5000:
        return await ctx.send("Tu n'as pas assez de coins pour créer une guilde (5000 requis).")

    def check_msg(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Demander le nom de la guilde
    await ctx.send("📝 Quel est le nom de ta guilde ? (Ce sera l'ID interne)")
    try:
        msg_nom = await bot.wait_for("message", check=check_msg, timeout=60)
        nom_guilde = msg_nom.content.strip()
    except asyncio.TimeoutError:
        return await ctx.send("⏳ Temps écoulé. Recommence la commande.")

    # Vérifier si une guilde avec ce nom existe déjà
    if collection35.find_one({"guild_id": guild_id, "guild_name": nom_guilde}):
        return await ctx.send("❌ Une guilde avec ce nom existe déjà.")

    # Demander la description
    await ctx.send("📄 Donne une petite description pour ta guilde :")
    try:
        msg_desc = await bot.wait_for("message", check=check_msg, timeout=60)
        description = msg_desc.content.strip()
    except asyncio.TimeoutError:
        return await ctx.send("⏳ Temps écoulé. Recommence la commande.")

    # Demander une PFP pour la guilde
    await ctx.send("🎨 Envoie une image pour la photo de profil de ta guilde (PFP) :")
    try:
        msg_pfp = await bot.wait_for("message", check=check_msg, timeout=60)
        pfp_url = msg_pfp.attachments[0].url if msg_pfp.attachments else None
        if not pfp_url:
            return await ctx.send("❌ Tu n'as pas envoyé d'image pour la PFP.")
    except asyncio.TimeoutError:
        return await ctx.send("⏳ Temps écoulé. Recommence la commande.")

    # Demander une bannière pour la guilde
    await ctx.send("🎨 Envoie une image pour la bannière de ta guilde :")
    try:
        msg_banniere = await bot.wait_for("message", check=check_msg, timeout=60)
        banniere_url = msg_banniere.attachments[0].url if msg_banniere.attachments else None
        if not banniere_url:
            return await ctx.send("❌ Tu n'as pas envoyé d'image pour la bannière.")
    except asyncio.TimeoutError:
        return await ctx.send("⏳ Temps écoulé. Recommence la commande.")

    # Déduire les coins
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"cash": -5000}}
    )

    # Log éco si tu veux
    await log_eco_channel(
        bot, guild_id, ctx.author, "Création Guilde", 5000,
        user_data["cash"], user_data["cash"] - 5000,
        note=f"Guilde: {nom_guilde}"
    )

    # Enregistrement dans la DB
    nouvelle_guilde = {
        "guild_id": guild_id,
        "guild_name": nom_guilde,
        "description": description,
        "pfp_url": pfp_url,
        "banniere_url": banniere_url,
        "bank": 0,
        "vault": 0,
        "membres": [
            {
                "user_id": user_id,
                "role": "Créateur",
                "joined_at": datetime.utcnow()
            }
        ]
    }

    collection35.insert_one(nouvelle_guilde)

    await ctx.send(f"✅ Guilde **{nom_guilde}** créée avec succès !")


@bot.command(name="g")
async def afficher_guilde(ctx):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    # Récupérer la guilde du joueur
    guilde = collection35.find_one({"guild_id": guild_id, "membres.user_id": user_id})
    if not guilde:
        return await ctx.send("Tu n'es dans aucune guilde.")

    guild_name = guilde.get("guild_name", "Inconnue")
    description = guilde.get("description", "Aucune description.")
    banque = guilde.get("bank", 0)
    coffre_fort = guilde.get("vault", 0)
    membres = guilde.get("membres", [])
    pfp_url = guilde.get("pfp_url")
    banniere_url = guilde.get("banniere_url")

    embed = discord.Embed(
        title=f"Informations sur la guilde : {guild_name}",
        color=discord.Color.blue()
    )

    # Ajouter la PFP si elle existe
    if pfp_url:
        embed.set_thumbnail(url=pfp_url)

    # Ajouter la bannière si elle existe
    if banniere_url:
        embed.set_image(url=banniere_url)

    embed.add_field(name="Description", value=description, inline=False)
    embed.add_field(name="Banque", value=f"{int(banque):,} <:ecoEther:1341862366249357374>", inline=True)  # Retirer les décimales
    embed.add_field(name="Coffre fort", value=f"{int(coffre_fort):,} / 750,000 <:ecoEther:1341862366249357374>", inline=True)  # Retirer les décimales
    embed.add_field(name="ID", value=guilde.get("guild_name"), inline=False)

    # Affichage des membres
    membre_text = ""
    for membre in membres:
        mention = f"<@{membre['user_id']}>"
        role = membre.get("role", "Membre")
        if role == "Créateur":
            membre_text += f"**Créateur** | {mention}\n"
        else:
            membre_text += f"**Membre** | {mention}\n"

    embed.add_field(name=f"Membres ({len(membres)}/5)", value=membre_text or "Aucun membre", inline=False)

    await ctx.send(embed=embed)

@bot.command(name="reset-teams")
async def reset_teams(ctx):
    # Vérifier si l'utilisateur a l'ID correct
    if ctx.author.id != 792755123587645461:
        return await ctx.send("Tu n'as pas la permission d'utiliser cette commande.")

    # Effacer toutes les guildes de la base de données
    result = collection35.delete_many({})
    
    if result.deleted_count > 0:
        await ctx.send(f"✅ Toutes les guildes ont été supprimées avec succès. {result.deleted_count} guildes supprimées.")
    else:
        await ctx.send("❌ Aucune guilde trouvée à supprimer.")

@bot.command(name="ginvite")
async def ginvite(ctx, member: discord.Member):
    # Récupérer les informations de la guilde du joueur qui invite
    guild_id = ctx.guild.id
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde:
        return await ctx.send("Aucune guilde trouvée.")

    guild_name = guilde.get("guild_name", "Inconnue")
    description = guilde.get("description", "Aucune description.")
    pfp_url = guilde.get("pfp_url")
    
    # Créer l'embed d'invitation
    embed = discord.Embed(
        title=f"Invitation à la guilde {guild_name}",
        description=f"Tu as été invité à rejoindre la guilde **{guild_name}** !\n\n{description}",
        color=discord.Color.blue()
    )
    
    if pfp_url:
        embed.set_thumbnail(url=pfp_url)

    # Créer les boutons "Accepter" et "Refuser"
    class InviteButtons(View):
        def __init__(self, inviter, invited_member):
            super().__init__()
            self.inviter = inviter
            self.invited_member = invited_member

        @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green)
        async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Action quand le membre accepte l'invitation
            if interaction.user == self.invited_member:
                # Ajouter le membre à la guilde
                collection35.update_one(
                    {"guild_id": guild_id},
                    {"$push": {"membres": {"user_id": self.invited_member.id, "role": "Membre"}}}
                )
                await interaction.response.send_message(f"{self.invited_member.mention} a accepté l'invitation à la guilde {guild_name} !", ephemeral=True)
                # Envoie un message dans la guilde (optionnel)
                await ctx.send(f"{self.invited_member.mention} a rejoint la guilde {guild_name}.")

        @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red)
        async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Action quand le membre refuse l'invitation
            if interaction.user == self.invited_member:
                await interaction.response.send_message(f"{self.invited_member.mention} a refusé l'invitation.", ephemeral=True)

    # Créer la vue pour les boutons
    view = InviteButtons(ctx.author, member)

    # Envoyer l'embed et ajouter la vue avec les boutons dans le salon d'origine
    await ctx.send(embed=embed, view=view)

    await ctx.send(f"Une invitation a été envoyée à {member.mention}.")

# Commande .cdep : Déposer des coins dans le coffre-fort de la guild
@bot.command(name="cdep")
async def cdep(ctx, amount: int):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    # Vérifier les coins de l'utilisateur
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not user_data or user_data.get("cash", 0) < amount:
        return await ctx.send("Tu n'as pas assez de coins pour faire ce dépôt.")

    # Déposer les coins dans le coffre-fort
    collection35.update_one(
        {"guild_id": guild_id},
        {"$inc": {"vault": amount}},
    )
    # Déduire les coins du joueur
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"cash": -amount}},
    )

    await ctx.send(f"{int(amount):,} coins ont été déposés dans le coffre-fort de la guilde.")

# Commande .cwith : Retirer des coins du coffre-fort de la guilde
@bot.command(name="cwith")
async def cwith(ctx, amount: int):
    guild_id = ctx.guild.id

    # Récupérer les informations de la guilde
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or guilde.get("vault", 0) < amount:
        return await ctx.send("Le coffre-fort de la guilde n'a pas assez de coins.")

    # Retirer les coins du coffre-fort
    collection35.update_one(
        {"guild_id": guild_id},
        {"$inc": {"vault": -amount}},
    )
    
    # Ajouter les coins à la banque
    collection35.update_one(
        {"guild_id": guild_id},
        {"$inc": {"bank": amount}},
    )

    await ctx.send(f"{int(amount):,} coins ont été retirés du coffre-fort de la guilde.")

# Commande .gban : Bannir un membre de la guilde
@bot.command(name="gban")
async def gban(ctx, member: discord.Member):
    guild_id = ctx.guild.id

    # Vérifier si l'utilisateur est dans la guilde
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or not any(membre['user_id'] == member.id for membre in guilde['membres']):
        return await ctx.send(f"{member.mention} n'est pas dans la guilde.")

    # Bannir le membre de la guilde
    collection35.update_one(
        {"guild_id": guild_id},
        {"$pull": {"membres": {"user_id": member.id}}},
    )

    await ctx.send(f"{member.mention} a été banni de la guilde.")

@bot.command(name="gdelete")
async def gdelete(ctx, guild_id: int):
    # Vérifier que l'utilisateur est autorisé à supprimer la guilde (par exemple, propriétaire)
    if ctx.author.id != 792755123587645461:  # ISEY_ID
        return await ctx.send("Tu n'as pas la permission de supprimer cette guilde.")
    
    # Vérifier si la guilde existe dans la base de données
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde:
        return await ctx.send(f"Aucune guilde trouvée avec l'ID {guild_id}.")

    # Supprimer la guilde
    collection35.delete_one({"guild_id": guild_id})

    await ctx.send(f"La guilde avec l'ID {guild_id} a été supprimée avec succès.")

# Commande .gdep : Déposer des coins dans la banque de la guilde
@bot.command(name="gdep")
async def gdep(ctx, amount: str):
    guild_id = ctx.guild.id

    if amount == "all":
        # Déposer tout l'argent dans la banque
        user_data = collection.find_one({"guild_id": guild_id, "user_id": ctx.author.id})
        amount = user_data.get("cash", 0)

        if amount == 0:
            return await ctx.send("Tu n'as pas de coins à déposer.")

    # Convertir la quantité en entier
    amount = int(amount)

    # Déposer les coins dans la banque de la guilde
    collection35.update_one(
        {"guild_id": guild_id},
        {"$inc": {"bank": amount}},
    )

    # Déduire les coins du joueur
    collection.update_one(
        {"guild_id": guild_id, "user_id": ctx.author.id},
        {"$inc": {"cash": -amount}},
    )

    await ctx.send(f"{amount:,} coins ont été déposés dans la banque de la guilde.")

# Commande .gkick : Expulser un membre de la guilde
@bot.command(name="gkick")
async def gkick(ctx, member: discord.Member):
    guild_id = ctx.guild.id

    # Vérifier si le membre est dans la guilde
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or not any(membre['user_id'] == member.id for membre in guilde['membres']):
        return await ctx.send(f"{member.mention} n'est pas dans la guilde.")

    # Expulser le membre
    collection35.update_one(
        {"guild_id": guild_id},
        {"$pull": {"membres": {"user_id": member.id}}},
    )

    await ctx.send(f"{member.mention} a été expulsé de la guilde.")

# Commande .gleave : Quitter la guilde
@bot.command(name="gleave")
async def gleave(ctx):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    # Vérifier si l'utilisateur est dans la guilde
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or not any(membre['user_id'] == user_id for membre in guilde['membres']):
        return await ctx.send("Tu n'es pas dans cette guilde.")

    # Quitter la guilde
    collection35.update_one(
        {"guild_id": guild_id},
        {"$pull": {"membres": {"user_id": user_id}}},
    )

    await ctx.send(f"{ctx.author.mention} a quitté la guilde.")

# Commande .gowner : Transférer la propriété de la guilde
@bot.command(name="gowner")
async def gowner(ctx, new_owner: discord.Member):
    guild_id = ctx.guild.id

    # Vérifier si l'utilisateur est le propriétaire actuel (par exemple, le créateur)
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or not any(membre['user_id'] == ctx.author.id and membre['role'] == 'Créateur' for membre in guilde['membres']):
        return await ctx.send("Tu n'es pas le propriétaire de la guilde.")

    # Transférer la propriété
    collection35.update_one(
        {"guild_id": guild_id, "membres.user_id": ctx.author.id},
        {"$set": {"membres.$.role": "Membre"}},
    )
    collection35.update_one(
        {"guild_id": guild_id, "membres.user_id": new_owner.id},
        {"$set": {"membres.$.role": "Créateur"}},
    )

    await ctx.send(f"La propriété de la guilde a été transférée à {new_owner.mention}.")

# Commande .gunban : Débannir un membre de la guilde
@bot.command(name="gunban")
async def gunban(ctx, member: discord.Member):
    guild_id = ctx.guild.id

    # Vérifier si le membre est banni
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or not any(membre['user_id'] == member.id and membre['role'] == 'Banni' for membre in guilde['membres']):
        return await ctx.send(f"{member.mention} n'est pas banni de cette guilde.")

    # Débannir le membre
    collection35.update_one(
        {"guild_id": guild_id},
        {"$pull": {"membres": {"user_id": member.id, "role": "Banni"}}},
    )

    await ctx.send(f"{member.mention} a été débanni de la guilde.")

# Commande .gwith : Retirer des coins de la banque de la guilde
@bot.command(name="gwith")
async def gwith(ctx, amount: int):
    guild_id = ctx.guild.id

    # Récupérer les informations de la guilde
    guilde = collection35.find_one({"guild_id": guild_id})
    if not guilde or guilde.get("bank", 0) < amount:
        return await ctx.send("La banque de la guilde n'a pas assez de coins.")

    # Retirer les coins de la banque
    collection35.update_one(
        {"guild_id": guild_id},
        {"$inc": {"bank": -amount}},
    )

    # Ajouter les coins au joueur (ici on les ajoute à l'auteur de la commande)
    collection.update_one(
        {"guild_id": guild_id, "user_id": ctx.author.id},
        {"$inc": {"cash": amount}},
    )

    await ctx.send(f"{amount:,} coins ont été retirés de la banque de la guilde.")

@bot.tree.command(name="dep-guild-inventory", description="Dépose un item de ton inventaire vers celui de ta guilde")
@app_commands.describe(item_id="ID de l'item à transférer", quantite="Quantité à transférer")
async def dep_guild_inventory(interaction: discord.Interaction, item_id: int, quantite: int):
    user = interaction.user
    guild_id = interaction.guild.id
    user_id = user.id

    if quantite <= 0:
        return await interaction.response.send_message("❌ La quantité doit être supérieure à 0.", ephemeral=True)

    # Vérifie la guilde du joueur
    guilde = collection35.find_one({"guild_id": guild_id, "membres.user_id": user_id})
    if not guilde:
        return await interaction.response.send_message("❌ Tu n'es dans aucune guilde.", ephemeral=True)

    # Vérifie l'inventaire du joueur
    items = list(collection17.find({
        "guild_id": guild_id,
        "user_id": user_id,
        "item_id": item_id
    }))

    if len(items) < quantite:
        return await interaction.response.send_message(f"❌ Tu n'as pas `{quantite}` de cet item dans ton inventaire.", ephemeral=True)

    # Supprimer les items du joueur
    for i in range(quantite):
        collection17.delete_one({
            "_id": items[i]["_id"]
        })

    # Ajouter à l'inventaire de la guilde
    existing = collection36.find_one({
        "guild_id": guild_id,
        "item_id": item_id
    })

    if existing:
        collection36.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"quantity": quantite}}
        )
    else:
        # On récupère les infos du premier item pour les détails
        item_data = items[0]
        collection36.insert_one({
            "guild_id": guild_id,
            "item_id": item_id,
            "item_name": item_data.get("item_name", "Inconnu"),
            "emoji": item_data.get("emoji", ""),
            "quantity": quantite
        })

    await interaction.response.send_message(
        f"✅ Tu as transféré **{quantite}x** `{item_id}` dans l'inventaire de ta guilde.",
        ephemeral=True
    )

@bot.tree.command(name="with-guild-inventory", description="Retire un item de l'inventaire de la guilde vers le tien")
@app_commands.describe(item_id="ID de l'item à retirer", quantite="Quantité à retirer")
async def with_guild_inventory(interaction: discord.Interaction, item_id: int, quantite: int):
    user = interaction.user
    guild_id = interaction.guild.id
    user_id = user.id

    if quantite <= 0:
        return await interaction.response.send_message("❌ La quantité doit être supérieure à 0.", ephemeral=True)

    # Vérifie la guilde du joueur
    guilde = collection35.find_one({"guild_id": guild_id, "membres.user_id": user_id})
    if not guilde:
        return await interaction.response.send_message("❌ Tu n'es dans aucune guilde.", ephemeral=True)

    # Vérifie l'inventaire de la guilde
    guild_item = collection36.find_one({
        "guild_id": guild_id,
        "item_id": item_id
    })

    if not guild_item or guild_item.get("quantity", 0) < quantite:
        return await interaction.response.send_message("❌ Pas assez de cet item dans l'inventaire de la guilde.", ephemeral=True)

    # Retirer les items de la guilde
    new_quantity = guild_item["quantity"] - quantite
    if new_quantity > 0:
        collection36.update_one(
            {"_id": guild_item["_id"]},
            {"$set": {"quantity": new_quantity}}
        )
    else:
        collection36.delete_one({"_id": guild_item["_id"]})

    # Ajouter les items dans l'inventaire du joueur
    insert_items = []
    for _ in range(quantite):
        insert_items.append({
            "guild_id": guild_id,
            "user_id": user_id,
            "item_id": item_id,
            "item_name": guild_item.get("item_name", "Inconnu"),
            "emoji": guild_item.get("emoji", "")
        })
    if insert_items:
        collection17.insert_many(insert_items)

    await interaction.response.send_message(
        f"📦 Tu as récupéré **{quantite}x** `{item_id}` depuis l'inventaire de la guilde.",
        ephemeral=True
    )

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
