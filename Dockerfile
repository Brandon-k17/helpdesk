# ── Stage 1 : builder ────────────────────────────────────────────────
# Installe les outils de compilation et construit les wheels Python
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# gcc + libpq-dev sont nécessaires pour compiler psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2 : runtime ────────────────────────────────────────────────
# Image finale légère : pas de gcc, pas de libpq-dev, juste le runtime
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Seule dépendance système nécessaire à l'exécution de psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copie uniquement les packages installés depuis le builder
COPY --from=builder /install /usr/local

# Copie le code source
COPY . .

EXPOSE 8000
