# Utilise Python 3.11 comme base
FROM python:3.11-slim

# Crée un dossier pour l'app
WORKDIR /app

# Copie les fichiers
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lance le bot
CMD ["python", "bot.py"]
