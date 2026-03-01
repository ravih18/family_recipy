.PHONY: dev docker-dev build up down logs pull deploy install-docker

# ─── Local sans Docker ────────────────────────────────────────────────────────

# Lancer en local sans Docker
dev:
	uv run python -m uvicorn app.main:app --reload

# ─── Docker dev (test local avec Docker) ──────────────────────────────────────

# Lancer en Docker local avec hot reload (test avant push)
docker-dev:
	docker compose -f docker-compose.dev.yml up --build

# Arrêter le Docker dev
docker-dev-down:
	docker compose -f docker-compose.dev.yml down

# ─── Docker local ─────────────────────────────────────────────────────────────

# Builder et lancer l'app seule (dev Docker)
build:
	docker compose up -d --build app

# Lancer tout (app + nginx + certbot)
up:
	docker compose up -d --build

# Arrêter tout
down:
	docker compose down

# Voir les logs en temps réel
logs:
	docker compose logs -f

# Logs de l'app seulement
logs-app:
	docker compose logs -f app

# ─── Production (VPS) ─────────────────────────────────────────────────────────

# Récupérer les dernières modifications depuis Git
pull:
	git pull origin main

# Déployer (pull + rebuild + restart)
deploy:
	git pull origin main
	docker compose up -d --build

# Renouveler le certificat SSL
ssl-renew:
	docker compose run --rm certbot renew
	docker compose restart nginx

# ─── Installation initiale sur le VPS ────────────────────────────────────────

# Installer Docker sur Ubuntu (à lancer une seule fois sur le VPS)
install-docker:
	apt install -y ca-certificates curl gnupg git ufw make
	install -m 0755 -d /etc/apt/keyrings
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
	chmod a+r /etc/apt/keyrings/docker.asc
	echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $$(. /etc/os-release && echo "$$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
	apt update
	apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
	systemctl enable docker
	systemctl start docker
	@echo "✅ Docker installé avec succès"

# Initialisation complète du VPS (après clone du repo)
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
	@echo "    make dev            → lancer en local sans Docker"
	@echo "    make docker-dev     → Docker local avec hot reload"
	@echo "    make docker-dev-down → arrêter le Docker dev"
	@echo "    make down         → arrêter Docker"
	@echo "    make logs         → voir tous les logs"
	@echo "    make logs-app     → logs de l'app seulement"
	@echo ""
	@echo "  Production :"
	@echo "    make deploy       → git pull + rebuild + restart"
	@echo "    make ssl-renew    → renouveler le certificat SSL"
	@echo ""
	@echo "  Installation VPS :"
	@echo "    make install-docker → installer Docker sur Ubuntu"
	@echo "    make setup          → initialisation après git clone"
	@echo ""