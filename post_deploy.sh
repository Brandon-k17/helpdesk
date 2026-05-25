#!/bin/bash
# ============================================================
# post_deploy.sh — Déclenché par cron après détection de deploy
# Placé dans le répertoire du projet, uploadé via FTP
# ============================================================

DEPLOY_PATH="$HOME/public_html/helpdesk"
LOCK_FILE="$DEPLOY_PATH/.deploy_pending"
LOG_FILE="$DEPLOY_PATH/deploy.log"

# Si pas de fichier .deploy_pending, rien à faire
if [ ! -f "$LOCK_FILE" ]; then
    exit 0
fi

# Supprime le lock immédiatement pour éviter les doubles exécutions
rm -f "$LOCK_FILE"

echo "=== Déploiement démarré : $(date) ===" >> "$LOG_FILE"

cd "$DEPLOY_PATH" || exit 1

# Active le virtualenv
source "$DEPLOY_PATH/venv/bin/activate"

# Installe les dépendances
pip install --quiet -r requirements.txt >> "$LOG_FILE" 2>&1

# Charge les variables d'environnement
if [ -f "$DEPLOY_PATH/.env.production" ]; then
    export $(grep -v '^#' "$DEPLOY_PATH/.env.production" | xargs)
fi

export DJANGO_SETTINGS_MODULE=helpdesk_project.settings

# Migrations
python manage.py migrate --noinput >> "$LOG_FILE" 2>&1

# Collecte des statiques
python manage.py collectstatic --noinput --clear >> "$LOG_FILE" 2>&1

# Nettoyage .pyc
find "$DEPLOY_PATH" -name "*.pyc" -delete 2>/dev/null
find "$DEPLOY_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Redémarre Passenger
mkdir -p "$DEPLOY_PATH/tmp"
touch "$DEPLOY_PATH/tmp/restart.txt"

echo "=== Déploiement terminé : $(date) ===" >> "$LOG_FILE"
