#!/usr/bin/env bash
# Claudius first-time setup script
# Run on Lumen: bash scripts/setup.sh

set -euo pipefail

echo "🏛️  Claudius Setup"
echo "=================="

# Check prerequisites
echo ""
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found"; exit 1; }
echo "  ✓ Python $(python3 --version | cut -d' ' -f2)"

command -v claude >/dev/null 2>&1 || { echo "❌ Claude Code CLI not found. Install from https://claude.ai"; exit 1; }
echo "  ✓ Claude Code $(claude --version 2>/dev/null || echo 'installed')"

command -v docker >/dev/null 2>&1 || echo "  ⚠ Docker not found (optional, for containerized deployment)"
command -v git >/dev/null 2>&1 || { echo "❌ Git not found"; exit 1; }
echo "  ✓ Git $(git --version | cut -d' ' -f3)"

# Check Tailscale connectivity
echo ""
echo "Checking Triune Brain connectivity..."
ssh -o ConnectTimeout=3 -o BatchMode=yes gx10-b71c 'echo ok' 2>/dev/null && echo "  ✓ Vigil (gx10-b71c) reachable" || echo "  ⚠ Vigil unreachable (check Tailscale)"
ping -c1 -W2 desktop-rssp6ga-1 >/dev/null 2>&1 && echo "  ✓ Lumen (local) reachable" || echo "  ✓ Lumen (this machine)"
ssh -o ConnectTimeout=3 -o BatchMode=yes avs-dellxps 'echo ok' 2>/dev/null && echo "  ✓ Echelon (avs-dellxps) reachable" || echo "  ⚠ Echelon unreachable (may be off)"

# Create config from template
echo ""
if [ ! -f config/config.yaml ]; then
    cp config/config.example.yaml config/config.yaml
    echo "  ✓ Created config/config.yaml from template"
    echo "  → Edit config/config.yaml with your settings before starting"
else
    echo "  ✓ config/config.yaml already exists"
fi

# Create .env from template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ✓ Created .env from template"
    echo "  → Edit .env with your Telegram bot token and other secrets"
else
    echo "  ✓ .env already exists"
fi

# Create runtime directories
mkdir -p memory/conversations logs
echo "  ✓ Runtime directories created"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q -r requirements.txt
echo "  ✓ Dependencies installed"

echo ""
echo "🏛️  Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your TELEGRAM_BOT_TOKEN"
echo "  2. Edit config/config.yaml with your preferences"
echo "  3. Test: python -m src.daemon"
echo "  4. Deploy: docker compose up -d"
