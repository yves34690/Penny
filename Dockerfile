# Dockerfile pour le scheduler Penny
FROM python:3.12-slim

LABEL maintainer="Claude Agent"
LABEL description="Scheduler automatique pour synchronisation Pennylane -> PostgreSQL"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Créer répertoire de travail
WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m ipykernel install --user --name python3 --display-name "Python 3"

# Copier le code source
COPY src/ ./src/
COPY data/ ./data/

# Créer répertoire pour les logs
RUN mkdir -p logs

# Commande de démarrage
CMD ["python", "src/notebook_scheduler.py"]
