#!/bin/bash

echo "🚀 Deploying Digital Twin Bot to Production"
echo "=========================================="

# Check if production environment file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from .env.prod.example"
    exit 1
fi

# Validate required environment variables
source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_DB_PASSWORD" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Missing required environment variables"
    echo "Required: TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_DB_PASSWORD, OPENAI_API_KEY"
    exit 1
fi

echo "✅ Environment variables validated"

# Stop any existing production containers
echo "🛑 Stopping existing production containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start production services
echo "🔨 Building and starting production services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if bot is running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Production deployment successful!"
    echo ""
    echo "📊 Service status:"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    echo "📋 View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "🛑 Stop services: docker-compose -f docker-compose.prod.yml down"
else
    echo "❌ Deployment failed"
    echo "📋 Check logs: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi
