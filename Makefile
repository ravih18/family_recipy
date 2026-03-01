.PHONY: dev build up down logs logs-app pull deploy setup help

# ─── Local sans Docker ────────────────────────────────────────────────────────

dev:
	uv run python -m uvicorn app.main:app --reload

# ─── Docker ───────────────────────────────────────────────────────────────────

build:
	docker compose up -d --build app

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

logs-app:
	docker compose logs -f app

# ─── Production (VPS) ─────────────────────────────────────────────────────────

pull:
	git pull origin main

deploy:
	git pull origin main
	docker compose up -d --build
	@echo "✅ Recettes déployées"

# ─── Installation initiale sur le VPS ────────────────────────────────────────

setup:
	@echo "📁 Création du dossier data/"
	mkdir -p data
	@echo "⚠️  N'oublie pas de créer ton fichier .env !"
	@echo "   cp .env.example .env && nano .env"
	@echo "✅ Setup terminé"

# ─── Aide ─────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "Commandes disponibles :"
	@echo ""
	@echo "  Local :"
	@echo "    make dev          → lancer en local sans Docker (uv)"
	@echo "    make down         → arrêter Docker"
	@echo "    make logs         → voir tous les logs"
	@echo "    make logs-app     → logs de l'app seulement"
	@echo ""
	@echo "  Production :"
	@echo "    make deploy       → git pull + rebuild + restart"
	@echo ""