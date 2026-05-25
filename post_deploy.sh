#!/bin/bash
# ============================================================
# post_deploy.sh — Script de post-déploiement o2switch
# Exécuté automatiquement après chaque déploiement FTP
# ============================================================

set -e  # Arrête le script si une commande échoue

# ── Couleurs pour les logs ───────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}[✓]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo "=================================================="
echo "  Post-déploiement HelpDesk — $(date)"
echo "=================================================="

# ── 1. Chemin du projet (à adapter selon ton o2switch) ───────
DEPLOY_PATH="${DEPLOY_PATH:-$HOME/public_html/helpdesk}"
cd "$DEPLOY_PATH" || error "Répertoire $DEPLOY_PATH introuvable"
log "Répertoire : $DEPLOY_PATH"

# ── 2. Activation du virtualenv Python ───────────────────────
VENV_PATH="$DEPLOY_PATH/venv"
if [ ! -d "$VENV_PATH" ]; then
    warn "Virtualenv absent, création en cours..."
    python3.13 -m venv "$VENV_PATH" || error "Impossible de créer le virtualenv"
    log "Virtualenv créé"
fi

source "$VENV_PATH/bin/activate" || error "Impossible d'activer le virtualenv"
log "Virtualenv activé"

# ── 3. Installation des dépendances ──────────────────────────
log "Installation des dépendances..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt || error "Échec de l'installation des dépendances"
log "Dépendances installées"

# ── 4. Variables d'environnement ─────────────────────────────
# Charge le .env de production s'il existe sur le serveur
if [ -f "$DEPLOY_PATH/.env.production" ]; then
    export $(grep -v '^#' "$DEPLOY_PATH/.env.production" | xargs)
    log "Variables d'environnement chargées"
else
    warn ".env.production absent — assure-toi que les variables sont définies dans cPanel"
fi

export DJANGO_SETTINGS_MODULE=helpdesk_project.settings

# ── 5. Migrations de la base de données ──────────────────────
log "Application des migrations..."
python manage.py migrate --noinput || error "Échec des migrations"
log "Migrations appliquées"

# ── 6. Collecte des fichiers statiques ───────────────────────
log "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear || error "Échec de collectstatic"
log "Fichiers statiques collectés"

# ── 7. Vérification de la configuration Django ───────────────
log "Vérification de la configuration..."
python manage.py check --deploy 2>&1 | grep -v "^System check" || true

# ── 8. Redémarrage de l'application Passenger ────────────────
# o2switch utilise Passenger pour servir les apps Python
RESTART_FILE="$DEPLOY_PATH/tmp/restart.txt"
mkdir -p "$DEPLOY_PATH/tmp"
touch "$RESTART_FILE" || warn "Impossible de créer tmp/restart.txt"
log "Application redémarrée (Passenger)"

# ── 9. Nettoyage des fichiers .pyc ───────────────────────────
find "$DEPLOY_PATH" -name "*.pyc" -delete 2>/dev/null
find "$DEPLOY_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
log "Fichiers .pyc nettoyés"

echo ""
echo "=================================================="
log "Déploiement terminé avec succès !"
echo "=================================================="
