#!/bin/bash

# YouTube Shorts Generator - Development Startup Script

echo "🎬 Starting YouTube Shorts Generator in Development Mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads outputs temp logs

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Start development services
echo "🚀 Starting development services..."
docker-compose --profile dev up --build

echo "✅ Development environment started!"
echo "🌐 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"