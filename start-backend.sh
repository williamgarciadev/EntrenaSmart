#!/bin/bash
# Start the EntrenaSmart backend API server

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting EntrenaSmart Backend API...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"

    # Create a minimal .env for development
    cat > .env << 'EOF'
# Development configuration
TELEGRAM_BOT_TOKEN=dev_token_placeholder
TRAINER_TELEGRAM_ID=123456789

# PostgreSQL Database (usar PostgreSQL en lugar de SQLite)
DATABASE_URL=postgresql://entrenasmart:entrenasmart123@localhost:5432/entrenasmart

# API Configuration
API_SECRET_KEY=dev-secret-key
API_CORS_ORIGINS=http://localhost:5173

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Timezone
TIMEZONE=America/Bogota

# Development mode
DEBUG=true
ENVIRONMENT=development
EOF
    echo -e "${GREEN}.env file created${NC}"
fi

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p storage logs

# Initialize database tables
echo -e "${YELLOW}Initializing PostgreSQL database tables...${NC}"
PYTHONPATH=backend:$PYTHONPATH python3 -c "from src.models.base import init_db; init_db()" || {
    echo -e "${RED}Failed to initialize database${NC}"
    echo -e "${YELLOW}Make sure PostgreSQL is running and accessible on localhost:5432${NC}"
    exit 1
}
echo -e "${GREEN}Database initialized${NC}"

# Check if dependencies are installed
python3 -c "import fastapi" 2>/dev/null || {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -q -r requirements.txt || {
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    }
    echo -e "${GREEN}Dependencies installed${NC}"
}

# Start the server
echo -e "${GREEN}Starting API server on http://localhost:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

PYTHONPATH=backend:$PYTHONPATH python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
