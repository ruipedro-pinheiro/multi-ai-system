#!/bin/bash
# Chika - One-Click Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/ruipedro-pinheiro/multi-ai-system/main/install.sh | bash

set -e

REPO_URL="https://github.com/ruipedro-pinheiro/multi-ai-system.git"
INSTALL_DIR="$HOME/chika"

echo ""
echo "🎯 Chika Installer"
echo "=================="
echo ""
echo "Multi-AI Chat Platform - Utiliser dix IA sans chichi"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git first:"
    echo "   sudo pacman -S git  # Arch"
    echo "   sudo apt install git  # Ubuntu/Debian"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ docker-compose not found. Please install docker-compose first"
    exit 1
fi

echo "✅ All prerequisites met!"
echo ""

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "📂 Chika already installed at $INSTALL_DIR"
    read -p "   Update to latest version? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Updating..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        echo "⏭️  Skipping update"
    fi
else
    echo "📥 Cloning Chika..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Create .env if not exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚙️  Configuration:"
    echo "   Edit .env to add your API keys (optional)"
    echo "   Chika works with local Ollama by default (no keys needed!)"
    echo ""
fi

# Build and start
echo "🔨 Building Docker images (this may take a few minutes)..."
docker-compose build --quiet

echo ""
echo "🚀 Starting Chika..."
docker-compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Chika is running!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 Access Chika:"
    echo "   Web UI:   http://localhost:3000"
    echo "   API:      http://localhost:8000"
    echo "   Docs:     http://localhost:8000/docs"
    echo ""
    echo "📝 Useful commands:"
    echo "   Stop:     cd $INSTALL_DIR && docker-compose down"
    echo "   Logs:     cd $INSTALL_DIR && docker-compose logs -f"
    echo "   Restart:  cd $INSTALL_DIR && docker-compose restart"
    echo "   Update:   cd $INSTALL_DIR && git pull && docker-compose up -d --build"
    echo ""
    echo "💡 Quick Start:"
    echo "   1. Open http://localhost:3000"
    echo "   2. Click '+' to create a room"
    echo "   3. Send: Hello @claude and @gpt!"
    echo "   4. Watch them collaborate! 🎉"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎯 Enjoy Chika - Utiliser dix IA sans chichi!"
    echo ""
else
    echo ""
    echo "❌ Something went wrong. Check logs:"
    echo "   docker-compose logs"
    exit 1
fi
