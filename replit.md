# DTIC Dashboard - GLPI Metrics

## Project Overview

This is a GLPI Dashboard application that displays metrics and statistics from a GLPI ticketing system. It consists of:

- **Backend**: FastAPI (Python) API server that connects to GLPI and provides metrics endpoints
- **Frontend**: React + Vite + TypeScript dashboard with date range filtering

## Recent Changes (October 6, 2025)

- Installed Python 3.11 and Node.js 20 modules for Replit environment
- Configured backend dependencies (FastAPI, Uvicorn, requests, python-dotenv)
- Configured frontend dependencies (React, Vite, Radix UI components, Recharts)
- Set up Vite to bind to 0.0.0.0:5000 for Replit proxy compatibility
- Created workflows for backend (port 8000) and frontend (port 5000)
- Created backend/.env file with placeholder GLPI credentials
- Configured deployment to use VM target with single-port serving

## Project Architecture

### Backend (`backend/`)
- **main.py**: FastAPI application entry point
- **api/**: Router modules for endpoints (ranking, stats, tickets)
- **logic/**: Business logic for metrics calculation
- **glpi_client.py**: GLPI API client with authentication and caching
- **schemas.py**: Pydantic models for API responses

### Frontend (`frontend/`)
- **src/App.tsx**: Main dashboard component
- **src/components/**: UI components (DateRangePicker, Figma components, Radix UI)
- **src/services/api.ts**: API client for backend communication
- **src/types/api.d.ts**: TypeScript type definitions

## Environment Setup

The backend requires GLPI API credentials in `backend/.env`:

```
API_URL=http://your-glpi-server/apirest.php
APP_TOKEN=your_app_token
USER_TOKEN=your_user_token
RANKING_TECHNICIAN_PARENT_GROUP_ID=17
CACHE_TTL_SEC=300
SESSION_TTL_SEC=300
```

## Development Workflows

- **Backend API**: Runs on localhost:8000 (console output)
- **Frontend**: Runs on 0.0.0.0:5000 (web view)

The frontend proxies API requests to the backend via `/api` path.

## Deployment

Configured for VM deployment (always-running) because the application:
- Maintains in-memory caching for GLPI session tokens
- Provides stateful API responses
- Serves both backend API and frontend assets

In production, the backend serves on port 5000 and includes the built frontend at `/dashboard`.

## User Preferences

None specified yet.

## Important Notes

1. The application requires valid GLPI credentials to function properly
2. Frontend is configured to work with Replit's proxy system (0.0.0.0 binding)
3. Backend uses localhost binding for security in development
4. Both workflows should be running for the dashboard to display live data
5. The .env file contains placeholder values and must be updated with real credentials
