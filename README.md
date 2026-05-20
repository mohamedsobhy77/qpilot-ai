# QPilot AI — AI-Powered QA Automation Platform

> Transform software requirements into complete QA assets using AI, workflow automation, and DevOps integrations.

## What it does

QPilot AI takes a requirement or user story and automatically generates:
- ✅ Test Scenarios (positive, negative, edge cases)
- ✅ Detailed Test Cases (steps, preconditions, expected results)
- ✅ Playwright Automation Scripts
- ✅ Jira Tickets
- ✅ GitHub commits
- ✅ Slack notifications

## Architecture

```
Frontend (Next.js)
      ↓
n8n Workflow Engine (orchestration)
      ↓
Backend API (FastAPI)
      ↓
AI Services (OpenAI)
      ↓
PostgreSQL Database
      ↓
External Integrations (Jira · GitHub · Slack)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React, TailwindCSS |
| Backend | FastAPI (Python 3.11) |
| Workflow | n8n |
| AI | OpenAI GPT-4 |
| Database | PostgreSQL 15 |
| Automation | Playwright |
| Integrations | Jira, GitHub, Slack |
| DevOps | Docker, Docker Compose |

## Project Structure

```
qpilot/
├── frontend/          # Next.js app (user interface)
├── backend/           # FastAPI app (business logic + AI)
├── n8n-workflows/     # Exported n8n workflow JSONs
├── docker/            # Dockerfiles per service
├── docs/              # Architecture + API docs
├── scripts/           # Dev utility scripts
└── docker-compose.yml # Local dev environment
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend dev)
- Python 3.11+ (for backend dev)

### 1. Clone and configure
```bash
git clone <repo>
cd qpilot
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start all services
```bash
docker-compose up -d
```

### 3. Run database migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 4. Access the app
- Frontend:   http://localhost:3000
- Backend API: http://localhost:8000
- API Docs:   http://localhost:8000/docs
- n8n:        http://localhost:5678

## Environment Variables

See `.env.example` for all required variables.

## License

MIT
