# Dockerfile pour Render avec Python 3.13 complet
FROM python:3.13

# Définir le répertoire de travail dans le container
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste des fichiers dans le container
COPY . .

# Commande pour lancer ton bot
CMD ["python", "bot.py"]
