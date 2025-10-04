#!/bin/bash

# Certificate Generation System - Quick Deployment Script

echo "🚀 Certificate Generation System - Deployment Script"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo "   Especially update: SECRET_KEY, SMTP_* settings"
    read -p "Press Enter after you've configured .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p certificates qr_codes

# Build and start the application
echo "🔨 Building Docker containers..."
docker-compose build

echo "🚀 Starting the application..."
docker-compose up -d

# Wait a moment for the application to start
sleep 10

# Health check
echo "🔍 Checking application health..."
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Access your application at: http://localhost:8000"
    echo "📊 View logs with: docker-compose logs -f certificate-app"
    echo "🛑 Stop application with: docker-compose down"
else
    echo "❌ Application health check failed"
    echo "📊 Check logs with: docker-compose logs certificate-app"
fi

echo ""
echo "🎉 Deployment complete!"