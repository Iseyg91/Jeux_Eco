
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------Items:
#-----------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
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
        "id": 869,
        "emoji": "<:brook:1367570627157954660>",
        "title": "Pièce Brook",
        "description": "Une pièce  mystérieuse et brillante, sans utilité apparente pour l'instant, mais qui semble receler un pouvoir caché en attente d'être découvert.",
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

    @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.secondary)
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

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.secondary)
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
@item.command(name="store", description="Affiche la boutique d'items")
async def item_store(interaction: discord.Interaction):
    embed = get_page_embed(0)
    view = Paginator(user=interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

# Appel de la fonction pour insérer les items dans la base de données lors du démarrage du bot
insert_items_into_db()

async def item_autocomplete(interaction: discord.Interaction, current: str):
    # On filtre les items qui contiennent ce que l'utilisateur est en train d'écrire
    results = []
    for item in ITEMS:
        if current.lower() in item["title"].lower():
            results.append(app_commands.Choice(name=item["title"], value=item["title"]))

    # On limite à 25 résultats max (Discord ne permet pas plus)
    return results[:25]

# Commande d'achat avec recherche par nom d'item
@item.command(name="buy", description="Achète un item de la boutique via son nom.")
@app_commands.describe(item_name="Nom de l'item à acheter", quantity="Quantité à acheter (défaut: 1)")
@app_commands.autocomplete(item_name=item_autocomplete)  # Lier l'autocomplétion à l'argument item_name
async def item_buy(interaction: discord.Interaction, item_name: str, quantity: int = 1):
    user_id = interaction.user.id
    guild_id = interaction.guild.id

    # Chercher l'item en utilisant le nom récupéré via l'autocomplétion
    item = collection16.find_one({"title": item_name})
    if not item:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Item introuvable",
            description="Aucun item avec ce nom n'a été trouvé dans la boutique.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if quantity <= 0:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Quantité invalide",
            description="La quantité doit être supérieure à zéro.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if item.get("quantity", 0) < quantity:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Stock insuffisant",
            description=f"Il ne reste que **{item.get('quantity', 0)}x** de cet item en stock.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Vérifier les requirements avant de permettre l'achat
    valid, message = await check_requirements(interaction.user, item.get("requirements", {}))
    if not valid:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Prérequis non remplis",
            description=message,
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    user_data = collection.find_one({"user_id": user_id, "guild_id": guild_id}) or {"cash": 0}
    total_price = int(item["price"]) * quantity

    if user_data.get("cash", 0) < total_price:
        embed = discord.Embed(
            title="<:classic_x_mark:1362711858829725729> Fonds insuffisants",
            description=f"Tu n'as pas assez de <:ecoEther:1341862366249357374> pour cet achat.\nPrix total : **{total_price:,}**",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Retirer l'argent du joueur
    collection.update_one(
        {"user_id": user_id, "guild_id": guild_id},
        {"$inc": {"cash": -total_price}},
        upsert=True
    )

    # Mise à jour de l'inventaire simple (collection7)
    inventory_data = collection7.find_one({"user_id": user_id, "guild_id": guild_id})
    if inventory_data:
        inventory = inventory_data.get("items", {})
        inventory[str(item["id"])] = inventory.get(str(item["id"]), 0) + quantity
        collection7.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": {"items": inventory}}
        )
    else:
        collection7.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "items": {str(item["id"]): quantity}
        })

    # Mise à jour de l'inventaire structuré (collection17)
    documents = [{
        "guild_id": guild_id,
        "user_id": user_id,
        "item_id": item["id"],
        "item_name": item["title"],
        "emoji": item.get("emoji"),
        "price": item["price"],
        "acquired_at": datetime.utcnow()
    } for _ in range(quantity)]
    if documents:
        collection17.insert_many(documents)

    # Mise à jour du stock boutique
    collection16.update_one(
        {"id": item["id"]},
        {"$inc": {"quantity": -quantity}}
    )

    # Gestion de la suppression des rôles et items après achat
    if item.get("remove_after_purchase"):
        remove_config = item["remove_after_purchase"]

        if remove_config.get("roles", False) and item.get("role_id"):
            role = discord.utils.get(interaction.guild.roles, id=item["role_id"])
            if role:
                await interaction.user.remove_roles(role)
                print(f"Rôle {role.name} supprimé pour {interaction.user.name} après l'achat.")

        if remove_config.get("items", False):
            inventory_data = collection7.find_one({"user_id": user_id, "guild_id": guild_id})
            if inventory_data:
                inventory = inventory_data.get("items", {})
                if str(item["id"]) in inventory:
                    inventory[str(item["id"])] -= quantity
                    if inventory[str(item["id"])] <= 0:
                        del inventory[str(item["id"])]
                    collection7.update_one(
                        {"user_id": user_id, "guild_id": guild_id},
                        {"$set": {"items": inventory}}
                    )
                    print(f"{quantity} de l'item {item['title']} supprimé de l'inventaire de {interaction.user.name}.")

    # Envoi du message de succès
    embed = discord.Embed(
        title="<:Check:1362710665663615147> Achat effectué",
        description=(
            f"Tu as acheté **{quantity}x {item['title']}** {item.get('emoji', '')} "
            f"pour **{total_price:,}** {item.get('emoji_price', '')} !"
        ),
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)
    
@item.command(name="inventory", description="Affiche l'inventaire d'un utilisateur")
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

async def item_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    results = []
    items = list(collection16.find().limit(100))  # Charger les 100 premiers items de la collection

    for item in items:
        title = item.get("title", "Sans nom")
        
        # On vérifie si l'input actuel de l'utilisateur est dans le nom de l'item
        if current.lower() in title.lower():
            results.append(app_commands.Choice(name=title, value=title))

    return results[:25]  # On limite à 25 résultats

@item.command(name="info", description="Affiche toutes les informations d'un item de la boutique")
@app_commands.describe(id="Nom de l'item à consulter")
@app_commands.autocomplete(id=item_autocomplete)  # <-- On associe l'autocomplétion ici
async def item_info(interaction: discord.Interaction, id: str):
    # On cherche l'item par le nom
    item = collection16.find_one({"title": id})

    if not item:
        embed = discord.Embed(
            title="❌ Item introuvable",
            description="Aucun item trouvé avec ce nom.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    formatted_price = f"{item['price']:,}".replace(",", " ")

    embed = discord.Embed(
        title=f"📦 Détails de l'item : {item['title']}",
        color=discord.Color.blue()
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

    embed.add_field(name="**Nom de l'item**", value=item['title'], inline=False)
    embed.add_field(name="**Description**", value=item['description'], inline=False)
    embed.add_field(name="ID", value=str(item['id']), inline=True)
    embed.add_field(name="Prix", value=f"{formatted_price} {item['emoji_price']}", inline=True)
    embed.add_field(name="Quantité", value=str(item.get('quantity', 'Indisponible')), inline=True)

    tradeable = "✅ Oui" if item.get("tradeable", False) else "❌ Non"
    usable = "✅ Oui" if item.get("usable", False) else "❌ Non"
    embed.add_field(name="Échangeable", value=tradeable, inline=True)
    embed.add_field(name="Utilisable", value=usable, inline=True)

    if item.get("use_effect"):
        embed.add_field(name="Effet à l'utilisation", value=item["use_effect"], inline=False)

    if item.get("requirements"):
        requirements = item["requirements"]
        req_message = []

        if "roles" in requirements:
            for role_id in requirements["roles"]:
                role = discord.utils.get(interaction.guild.roles, id=role_id)
                if role:
                    req_message.append(f"• Rôle requis : <@&{role_id}> ({role.name})")
                else:
                    req_message.append(f"• Rôle requis : <@&{role_id}> (Introuvable)")

        if "items" in requirements:
            for required_item_id in requirements["items"]:
                item_in_inventory = await check_user_has_item(interaction.user, required_item_id)
                if item_in_inventory:
                    req_message.append(f"• Item requis : ID {required_item_id} (Possédé)")
                else:
                    req_message.append(f"• Item requis : ID {required_item_id} (Non possédé)")

        embed.add_field(
            name="Prérequis",
            value="\n".join(req_message) if req_message else "Aucun prérequis",
            inline=False
        )
    else:
        embed.add_field(name="Prérequis", value="Aucun prérequis", inline=False)

    emoji = item.get("emoji")
    if emoji:
        try:
            emoji_id = emoji.split(":")[2].split(">")[0]
            embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png")
        except Exception as e:
            print(f"Erreur lors de l'extraction de l'emoji : {e}")

    embed.set_footer(text="🛒 Etherya • Détails de l'item")

    await interaction.response.send_message(embed=embed)

async def item_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    user = interaction.user
    user_id = user.id
    guild_id = interaction.guild.id

    # Chercher les items dans l'inventaire de l'utilisateur
    owned_items = collection17.find({"user_id": user_id, "guild_id": guild_id})
    
    results = []
    
    for owned_item in owned_items:
        item_id = owned_item["item_id"]
        item_data = collection16.find_one({"id": item_id})
        
        if item_data and current.lower() in item_data["title"].lower():
            results.append(app_commands.Choice(name=item_data["title"], value=str(item_id)))
    
    return results[:25]  # Limiter à 25 résultats

@item.command(name="use", description="Utilise un item de ton inventaire.")
@app_commands.describe(item_id="Nom de l'item à utiliser")
@app_commands.autocomplete(item_id=item_autocomplete)  # <-- On ajoute l'autocomplétion ici
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

    # Vérifier si l'utilisateur a le rôle spécifique qui permet d'utiliser des items malgré les rôles bloquants
    special_role_id = 1365310665417556011
    if special_role_id in [role.id for role in user.roles]:
        embed = discord.Embed(
            title=f"<:Check:1362710665663615147> Utilisation de l'item",
            description=f"Tu as utilisé **{item_data['title']}** {item_data.get('emoji', '')}, malgré les restrictions de rôle.",
            color=discord.Color.green()
        )
        return await interaction.response.send_message(embed=embed)

    # Vérification des rôles bloquants
    if item_data.get("blocked_roles"):
        blocked_roles = item_data["blocked_roles"]
        
        # Compter combien de rôles bloquants l'utilisateur possède
        user_blocked_roles = [role for role in user.roles if role.id in blocked_roles]
        
        # Vérification si l'utilisateur a le rôle spécial qui permet de dépasser la limite
        special_role_id = 1365310665417556011
        limit = 1  # Limite par défaut si l'utilisateur n'a pas le rôle spécial
        
        if special_role_id in [role.id for role in user.roles]:
            limit = 2  # Si l'utilisateur a le rôle spécial, on augmente la limite à 2

        # Si l'utilisateur a trop de rôles bloquants (>= limite), on bloque l'utilisation
        if len(user_blocked_roles) >= limit:
            embed = discord.Embed(
                title="<:classic_x_mark:1362711858829725729> Utilisation bloquée",
                description="Tu ne peux pas utiliser cet item en raison de tes rôles bloquants.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

    # Si aucun rôle ne bloque, continuer normalement (comme dans ton code actuel)
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
        if item_data["remove_after_use"].get("roles", False):
            role = discord.utils.get(interaction.guild.roles, id=item_data["role_id"])
            if role and role in user.roles:
                await user.remove_roles(role)
                embed.add_field(name="⚠️ Rôle supprimé", value=f"Le rôle **{role.name}** a été supprimé après l'utilisation de l'item.", inline=False)
                print(f"Rôle {role.name} supprimé pour {interaction.user.name} après l'utilisation de l'item.")
        
        if item_data["remove_after_use"].get("items", False):
            collection17.delete_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "item_id": item_id
            })
            print(f"Item ID {item_id} supprimé de l'inventaire de {interaction.user.name}.")

    await interaction.response.send_message(embed=embed)

# Fonction d'autocomplétion pour l'ID des items
async def item_autocomplete(interaction: discord.Interaction, current: str):
    results = []
    # Recherche parmi les items dans la collection
    items = collection16.find()
    
    # Ajoute les items dont le nom correspond à ce que l'utilisateur tape
    for item in items:
        if current.lower() in item["title"].lower():
            results.append(Choice(name=f"{item['title']} (ID: {item['id']})", value=item['id']))
    
    return results[:25]  # Limite à 25 résultats maximum

@item.command(name="give", description="(Admin) Donne un item à un utilisateur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    member="Utilisateur à qui donner l'item",
    item_id="ID de l'item à donner",
    quantity="Quantité d'items à donner"
)
@app_commands.autocomplete(item_id=item_autocomplete)  # Ajout de l'autocomplétion pour item_id
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

# Fonction d'autocomplétion pour l'ID des items
async def item_autocomplete(interaction: discord.Interaction, current: str):
    results = []
    # Recherche parmi les items dans la collection
    items = collection16.find()
    
    # Ajoute les items dont le nom correspond à ce que l'utilisateur tape
    for item in items:
        if current.lower() in item["title"].lower():
            results.append(Choice(name=f"{item['title']} (ID: {item['id']})", value=item['id']))
    
    return results[:25]  # Limite à 25 résultats maximum

@item.command(name="take", description="(Admin) Retire un item d'un utilisateur.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    member="Utilisateur à qui retirer l'item",
    item_id="ID de l'item à retirer",
    quantity="Quantité d'items à retirer"
)
@app_commands.autocomplete(item_id=item_autocomplete)  # Ajout de l'autocomplétion pour item_id
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

# Fonction d'autocomplétion pour l'ID des items, filtrée par l'inventaire de l'utilisateur
async def item_autocomplete(interaction: discord.Interaction, current: str):
    results = []
    guild_id = interaction.guild.id
    user_id = interaction.user.id

    # Recherche des items que le joueur possède dans son inventaire
    owned_items = collection17.find({"user_id": user_id, "guild_id": guild_id})

    # Ajoute les items dont le nom correspond à ce que l'utilisateur tape
    for item in owned_items:
        item_data = collection16.find_one({"id": item["item_id"]})
        if item_data and current.lower() in item_data["title"].lower():
            results.append(Choice(name=f"{item_data['title']} (ID: {item_data['id']})", value=item_data['id']))
    
    return results[:25]  # Limite à 25 résultats maximum

@item.command(name="sell", description="Vends un item à un autre utilisateur pour un prix donné.")
@app_commands.describe(
    member="L'utilisateur à qui vendre l'item",
    item_id="ID de l'item à vendre",
    price="Prix de vente de l'item",
    quantity="Quantité d'items à vendre (par défaut 1)"
)
@app_commands.autocomplete(item_id=item_autocomplete)  # Ajout de l'autocomplétion pour item_id
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

# Fonction d'autocomplétion pour les items disponibles en boutique
async def item_shop_autocomplete(interaction: discord.Interaction, current: str):
    results = []
    # Cherche tous les items de la boutique qui correspondent à ce que tape l'utilisateur
    items = collection16.find({"title": {"$regex": current, "$options": "i"}}).limit(25)

    for item in items:
        results.append(Choice(name=f"{item['title']} (ID: {item['id']})", value=item['id']))

    return results

@item.command(name="leaderboard", description="Affiche le leaderboard des utilisateurs possédant un item spécifique.")
@app_commands.describe(
    item_id="ID de l'item dont vous voulez voir le leaderboard"
)
@app_commands.autocomplete(item_id=item_shop_autocomplete)  # <<<<<< ajoute ici l'autocomplete
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

# Fonction d'autocomplétion pour les items de la boutique (déjà faite, donc on réutilise !)
async def item_shop_autocomplete(interaction: discord.Interaction, current: str):
    results = []
    items = collection16.find({"title": {"$regex": current, "$options": "i"}}).limit(25)

    for item in items:
        results.append(Choice(name=f"{item['title']} (ID: {item['id']})", value=item['id']))

    return results

@item.command(name="restock", description="Restock un item dans la boutique")
@app_commands.describe(
    item_id="ID de l'item à restock",
    quantity="Nouvelle quantité à définir"
)
@app_commands.autocomplete(item_id=item_shop_autocomplete)  # <<<< ajoute ici l'autocomplete
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

# Même autocomplétion que pour /restock (items de la boutique)
async def item_shop_autocomplete(interaction: discord.Interaction, current: str):
    results = []
    items = collection16.find({"title": {"$regex": current, "$options": "i"}}).limit(25)

    for item in items:
        results.append(app_commands.Choice(name=f"{item['title']} (ID: {item['id']})", value=item['id']))

    return results

@item.command(name="reset", description="Supprime tous les items de la boutique")
async def reset_item(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    deleted = collection16.delete_many({})  # Supprime tous les documents de la collection

    return await interaction.response.send_message(
        f"🗑️ {deleted.deleted_count} item(s) ont été supprimés de la boutique.", ephemeral=True
    )

@item.command(name="delete", description="Supprime un item spécifique de la boutique")
@app_commands.describe(item_id="L'identifiant de l'item à supprimer")
async def delete_item(interaction: discord.Interaction, item_id: str):
    if interaction.user.id != ISEY_ID:
        return await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    result = collection16.delete_one({"id": item_id})

    if result.deleted_count == 0:
        return await interaction.response.send_message("❌ Aucun item trouvé avec cet ID.", ephemeral=True)

    return await interaction.response.send_message(f"🗑️ L'item avec l'ID `{item_id}` a été supprimé de la boutique.", ephemeral=True)


