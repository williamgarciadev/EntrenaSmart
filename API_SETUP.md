# API Connection Setup Guide

This document explains how to fix and prevent the `ERR_CONNECTION_REFUSED` error when connecting the frontend to the backend API.

## Problem

The frontend was trying to connect to `http://localhost:8000/api/students` but getting a connection refused error because the backend API server wasn't running.

## Solution

### Quick Start

Use the provided startup script:

```bash
./start-backend.sh
```

This script will:
1. Create a `.env` file if it doesn't exist
2. Create required directories (`storage/`, `logs/`)
3. Initialize the database if needed
4. Install Python dependencies if needed
5. Start the backend API server on port 8000

### Manual Setup

If you prefer to start the backend manually:

1. **Create the .env file** (if it doesn't exist):
   ```bash
   cp .env.example .env
   # Edit .env and set the required values, or use the minimal dev config in start-backend.sh
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create required directories**:
   ```bash
   mkdir -p storage logs
   ```

4. **Initialize the database**:
   ```bash
   PYTHONPATH=backend:$PYTHONPATH python3 -c "from src.models.base import init_db; init_db()"
   ```

5. **Start the backend API server**:
   ```bash
   PYTHONPATH=backend:$PYTHONPATH python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Verification

Test that the API is working:

```bash
# Health check
curl http://localhost:8000/health

# List students (requires authentication)
curl -H "Authorization: Bearer dev-secret-key" http://localhost:8000/api/students
```

## Frontend Configuration

The frontend is already configured to connect to the backend:
- Vite proxy configuration in `frontend/vite.config.ts` forwards `/api` requests to `http://localhost:8000`
- CORS is configured on the backend to accept requests from `http://localhost:5173`

## Development Workflow

1. Start the backend: `./start-backend.sh`
2. In another terminal, start the frontend: `cd frontend && npm run dev`
3. Access the application at `http://localhost:5173`

## Authentication

For development, the API accepts the following token:
- Token: `dev-secret-key`
- Use in requests: `Authorization: Bearer dev-secret-key`

## Troubleshooting

### Port already in use
If port 8000 is already in use:
```bash
# Find the process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)
```

### Module not found errors
Make sure to set `PYTHONPATH` when running the backend:
```bash
PYTHONPATH=backend:$PYTHONPATH python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database errors
If you get database errors, try reinitializing:
```bash
rm storage/entrenasmart.db
PYTHONPATH=backend:$PYTHONPATH python3 -c "from src.models.base import init_db; init_db()"
```

## Files Created

- `.env` - Environment configuration (gitignored)
- `storage/entrenasmart.db` - SQLite database (gitignored)
- `logs/bot.log` - Application logs (gitignored)
- `start-backend.sh` - Startup script

## Architecture

```
Frontend (React/Vite)     Backend (FastAPI)        Database
http://localhost:5173  →  http://localhost:8000  →  SQLite/PostgreSQL
                          /api/students
                          /api/schedules
                          /api/training-config
                          /api/templates
                          /api/auth
```
