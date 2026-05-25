# ── Stage 1 : builder ────────────────────────────────────────────────
# Installe les outils de compilation et construit les wheels Python
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ✅ FIX mysqlclient : pkg-config + default-libmysqlclient-dev obligatoires
# ✅ libpq-dev : nécessaire pour compiler psycopg2 (si non-binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2 : runtime ────────────────────────────────────────────────
# Image finale légère : pas de gcc, pas d'outils de build
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=helpdesk_project.settings

WORKDIR /app

# ✅ libpq5    : runtime PostgreSQL (psycopg2)
# ✅ libmariadb3 : runtime MySQL/MariaDB (mysqlclient compilé au build)
# ✅ curl      : pour le HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home appuser

# Copie uniquement les packages installés depuis le builder
COPY --from=builder /install /usr/local

# Copie le code source
COPY --chown=appuser:appgroup . .

# Répertoires nécessaires avec les bons droits
RUN mkdir -p staticfiles mediafiles logs \
    && chown -R appuser:appgroup /app

USER appuser

RUN python manage.py collectstatic --noinput

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "helpdesk_project.wsgi:application"]