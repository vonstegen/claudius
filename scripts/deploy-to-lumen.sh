#!/usr/bin/env bash
# Deploy Claudius to Lumen from Echelon
# Run from Echelon: bash scripts/deploy-to-lumen.sh

set -euo pipefail

LUMEN_HOST="desktop-rssp6ga-1"
REMOTE_DIR="~/claudius"

echo "🏛️  Deploying Claudius to Lumen..."

# Push latest to GitHub
echo "  Pushing to GitHub..."
git push origin main

# Pull on Lumen
echo "  Pulling on Lumen..."
ssh "$LUMEN_HOST" "cd $REMOTE_DIR && git pull origin main"

# Rebuild and restart Docker
echo "  Rebuilding container..."
ssh "$LUMEN_HOST" "cd $REMOTE_DIR && docker compose down && docker compose up -d --build"

# Verify
echo "  Checking health..."
sleep 5
ssh "$LUMEN_HOST" "docker ps | grep claudius"

echo "🏛️  Deployment complete"
