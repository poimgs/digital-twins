#!/bin/bash

echo "🗄️  Connecting to Digital Twin Bot Database"
echo "==========================================="

if [ "$1" = "prod" ]; then
    echo "Connecting to production (Supabase)..."
    echo "Please use Supabase dashboard for production database access"
    exit 1
else
    echo "Connecting to local development database..."
    docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d digital_twin_bot
fi

---

# Makefile - Development commands
.PHONY: dev-up dev-down dev-logs dev-shell dev-seed dev-restart

# Development environment
dev-up:
	@echo "🚀 Starting development environment..."
	@chmod +x scripts/dev-setup.sh
	@./scripts/dev-setup.sh

dev-down:
	@echo "🛑 Stopping development environment..."
	@docker-compose -f docker-compose.dev.yml down

dev-logs:
	@echo "📋 Showing bot logs..."
	@docker-compose -f docker-compose.dev.yml logs -f digital-twin-bot-dev

dev-shell:
	@echo "🗄️  Opening database shell..."
	@chmod +x scripts/db-shell.sh
	@./scripts/db-shell.sh

dev-seed:
	@echo "🌱 Adding additional seed data..."
	@python3 scripts/seed-data.py

dev-restart:
	@echo "🔄 Restarting bot..."
	@docker-compose -f docker-compose.dev.yml restart digital-twin-bot-dev

# Production commands
prod-up:
	@echo "🚀 Starting production environment..."
	@docker-compose up -d

prod-down:
	@echo "🛑 Stopping production environment..."
	@docker-compose down

prod-logs:
	@echo "📋 Showing production logs..."
	@docker-compose logs -f

# Testing
test:
	@echo "🧪 Running tests..."
	@docker-compose -f docker-compose.dev.yml exec digital-twin-bot-dev pytest

# Code quality
lint:
	@echo "🔍 Running linters..."
	@docker-compose -f docker-compose.dev.yml exec digital-twin-bot-dev black --check src/
	@docker-compose -f docker-compose.dev.yml exec digital-twin-bot-dev flake8 src/

format:
	@echo "🎨 Formatting code..."
	@docker-compose -f docker-compose.dev.yml exec digital-twin-bot-dev black src/