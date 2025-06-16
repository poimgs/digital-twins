#!/bin/bash

echo "🔧 Setting up Digital Twin Bot for Local Development"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.dev .env
    echo "✅ Please edit .env file with your actual credentials"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - OPENAI_API_KEY"
    echo ""
fi

# Build and start development services
echo "🚀 Starting development environment..."
docker-compose -f docker-compose.dev.yml up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if database is ready
if docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL failed to start"
    exit 1
fi

# Start the bot
echo "🤖 Starting Digital Twin Bot..."
docker-compose -f docker-compose.dev.yml up -d digital-twin-bot-dev

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📊 Services running:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Bot: running in container"
echo "   - Logs: docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "🔧 Management commands:"
echo "   - View logs: docker-compose -f docker-compose.dev.yml logs -f digital-twin-bot-dev"
echo "   - Restart bot: docker-compose -f docker-compose.dev.yml restart digital-twin-bot-dev"
echo "   - Stop all: docker-compose -f docker-compose.dev.yml down"
echo "   - Database shell: docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d digital_twin_bot"
echo ""
echo "🎯 Optional: Start pgAdmin for database management:"
echo "   docker-compose -f docker-compose.dev.yml --profile tools up -d pgadmin"
echo "   Then visit: http://localhost:8080"