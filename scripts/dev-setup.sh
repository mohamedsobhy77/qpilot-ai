#!/bin/bash
# scripts/dev-setup.sh
# One-shot local development setup script
# Run: bash scripts/dev-setup.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════╗"
echo "║     QPilot AI — Dev Setup             ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# 1. Check prerequisites
command -v docker >/dev/null 2>&1 || { echo -e "${RED}✗ Docker not found. Install it first.${NC}"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo -e "${RED}✗ Docker Compose not found.${NC}"; exit 1; }
echo -e "${GREEN}✓ Docker found${NC}"

# 2. Check .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${YELLOW}⚠ .env created from .env.example — edit it with your API keys before continuing${NC}"
  echo ""
  echo "  Required keys to set:"
  echo "  - OPENAI_API_KEY"
  echo "  - JWT_SECRET (any long random string)"
  echo ""
  read -p "Press Enter after editing .env to continue, or Ctrl+C to stop..."
fi
echo -e "${GREEN}✓ .env configured${NC}"

# 3. Start containers
echo -e "\n${CYAN}Starting Docker services...${NC}"
docker compose up -d --build

# 4. Wait for DB
echo -e "\n${CYAN}Waiting for PostgreSQL to be ready...${NC}"
sleep 8
until docker compose exec -T db pg_isready -U qpilot_user -d qpilot 2>/dev/null; do
  sleep 2
done
echo -e "${GREEN}✓ PostgreSQL ready${NC}"

# 5. Run migrations
echo -e "\n${CYAN}Running Alembic migrations...${NC}"
docker compose exec -T backend alembic upgrade head
echo -e "${GREEN}✓ Migrations applied${NC}"

# 6. Seed database
echo -e "\n${CYAN}Seeding database...${NC}"
docker compose exec -T backend python /scripts/seed.py 2>/dev/null || echo "  (seed skipped — run manually if needed)"

# 7. Done
echo -e "\n${GREEN}╔═══════════════════════════════════════╗"
echo "║     QPilot AI is ready! 🚀            ║"
echo "╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Frontend:${NC}  http://localhost:3000"
echo -e "  ${CYAN}API:${NC}       http://localhost:8000"
echo -e "  ${CYAN}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${CYAN}n8n:${NC}       http://localhost:5678"
echo ""
echo -e "  ${CYAN}Login:${NC}     admin@qpilot.ai / qpilot123"
echo ""
