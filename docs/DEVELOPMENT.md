# QPilot AI — Development Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Manual Local Setup](#manual-local-setup)
4. [Project Structure](#project-structure)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [n8n Workflow Setup](#n8n-workflow-setup)
8. [Running Tests](#running-tests)
9. [API Reference](#api-reference)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker | 24+ | Container runtime |
| Docker Compose | 2.20+ | Multi-service orchestration |
| Node.js | 20+ | Frontend dev server |
| Python | 3.11+ | Backend dev server |
| Git | any | Version control |

---

## Quick Start (Docker)

The fastest way to run everything:

```bash
# 1. Clone and enter project
git clone <repo> && cd qpilot

# 2. Set up environment
cp .env.example .env
# Open .env and set at minimum:
#   OPENAI_API_KEY=sk-...
#   JWT_SECRET=<any 32+ char random string>

# 3. One-command startup
bash scripts/dev-setup.sh
```

That's it. The script starts all containers, runs migrations, and seeds the DB.

| Service  | URL                        |
|----------|----------------------------|
| App      | http://localhost:3000      |
| API      | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |
| n8n      | http://localhost:5678      |

Login: `admin@qpilot.ai` / `qpilot123`

---

## Manual Local Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy from root .env.example, adjust DATABASE_URL)
cp ../.env.example .env
# Set DATABASE_URL to point to your local PostgreSQL

# Run migrations
alembic upgrade head

# Seed database
python ../scripts/seed.py

# Start dev server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

---

## Project Structure

```
qpilot/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/       # Route handlers (one file per domain)
│   │   │   ├── deps.py          # Shared FastAPI dependencies
│   │   │   └── router.py        # Registers all routers
│   │   ├── core/
│   │   │   ├── config.py        # Settings from environment
│   │   │   ├── exceptions.py    # Custom exception classes
│   │   │   └── security.py      # JWT + password utilities
│   │   ├── db/
│   │   │   └── database.py      # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   └── models.py        # SQLAlchemy ORM models (9 tables)
│   │   ├── schemas/
│   │   │   └── schemas.py       # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── ai_service.py   # OpenAI calls + retry logic
│   │   │   │   └── prompts.py      # Prompt library (6 prompts)
│   │   │   └── integrations/
│   │   │       ├── github_service.py
│   │   │       ├── jira_service.py
│   │   │       └── slack_service.py
│   │   ├── middleware/          # CORS, logging, rate limiting
│   │   └── main.py              # FastAPI app entry point
│   ├── alembic/                 # Database migrations
│   ├── tests/
│   │   ├── unit/                # Unit tests (no external deps)
│   │   └── integration/         # Full pipeline tests
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   │   ├── auth/login/      # Login page
│   │   │   ├── dashboard/       # Dashboard home
│   │   │   ├── requirements/    # Requirements list + detail
│   │   │   ├── scenarios/       # Scenarios browser
│   │   │   ├── test-cases/      # Test cases with script viewer
│   │   │   ├── workflows/       # Workflow execution monitor
│   │   │   └── logs/            # Activity log
│   │   ├── components/
│   │   │   └── layout/Sidebar.tsx
│   │   ├── lib/api.ts           # Axios instance + interceptors
│   │   ├── services/index.ts    # All API call functions
│   │   ├── store/auth.ts        # Zustand auth state
│   │   └── types/index.ts       # TypeScript types
│   ├── tests/
│   │   ├── utils/               # Shared Playwright helpers
│   │   └── generated/           # AI-generated test scripts
│   └── playwright.config.ts
│
├── n8n-workflows/
│   └── main-qa-pipeline.json    # Import this into n8n
│
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── scripts/
│   ├── dev-setup.sh             # One-command local setup
│   ├── seed.py                  # Database seeder
│   └── init-db.sql              # Postgres init (creates n8n DB)
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Backend Development

### Adding a new endpoint

1. Create or modify a file in `backend/app/api/v1/endpoints/`
2. Add request/response schemas to `backend/app/schemas/schemas.py`
3. Register the router in `backend/app/api/v1/router.py`
4. Write tests in `backend/tests/unit/`

### Adding a database migration

```bash
cd backend
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

### Running linter

```bash
cd backend
black app/ tests/
isort app/ tests/
flake8 app/ tests/
```

---

## Frontend Development

### Adding a new page

1. Create `src/app/<route>/page.tsx`
2. Add navigation link to `src/components/layout/Sidebar.tsx`
3. Add any new API calls to `src/services/index.ts`
4. Add TypeScript types to `src/types/index.ts`

### Styling conventions

- Use Tailwind utility classes
- Custom component classes are defined in `globals.css` (`@layer components`)
- Use `clsx` for conditional classes
- Brand color: `brand-600` (indigo)

---

## n8n Workflow Setup

### Import the workflow

1. Open n8n at http://localhost:5678
2. Login (admin/changeme by default)
3. Click **Workflows → Import** 
4. Upload `n8n-workflows/main-qa-pipeline.json`
5. Set environment variables in n8n:
   - `BACKEND_URL` = `http://backend:8000`
   - `BACKEND_API_TOKEN` = a valid JWT from your backend

### Webhook URLs

| Webhook | URL |
|---|---|
| Requirement submitted | `http://localhost:5678/webhook/requirement-submitted` |
| Approval received | `http://localhost:5678/webhook/approval-approved` |

### Testing a workflow manually

```bash
curl -X POST http://localhost:5678/webhook/requirement-submitted \
  -H "Content-Type: application/json" \
  -d '{
    "requirement_id": "<uuid>",
    "requirement_title": "Test Feature",
    "requirement_description": "Testing the n8n workflow manually"
  }'
```

---

## Running Tests

### Backend unit + integration tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Frontend E2E tests (Playwright)

```bash
cd frontend
npx playwright install   # first time only
npx playwright test

# Interactive UI mode
npx playwright test --ui

# Specific file
npx playwright test tests/generated/login-positive-flow.spec.ts
```

---

## API Reference

The interactive API docs are auto-generated at:
- Swagger UI: http://localhost:8000/docs
- ReDoc:      http://localhost:8000/redoc

### Key endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Get JWT token |
| GET  | `/api/v1/auth/profile` | Current user |
| POST | `/api/v1/requirements` | Create requirement |
| GET  | `/api/v1/requirements` | List requirements |
| POST | `/api/v1/scenarios/generate` | AI scenario generation |
| POST | `/api/v1/test-cases/generate` | AI test case generation |
| POST | `/api/v1/test-cases/generate-all` | Bulk generate (used by n8n) |
| POST | `/api/v1/approvals` | Submit QA approval |
| POST | `/api/v1/automation/generate` | Generate Playwright script |
| POST | `/api/v1/integrations/jira/create` | Create Jira ticket |
| POST | `/api/v1/integrations/slack/notify` | Send Slack message |
| GET  | `/api/v1/dashboard/stats` | Dashboard statistics |
| GET  | `/api/v1/health` | Health check |

---

## Deployment

### Frontend → Vercel

```bash
cd frontend
npx vercel --prod
# Set NEXT_PUBLIC_API_URL to your backend URL
```

### Backend → Railway or Render

1. Connect your GitHub repo
2. Set root directory to `backend`
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example`

### PostgreSQL → Supabase or Railway

1. Create a PostgreSQL database
2. Update `DATABASE_URL` in your backend env

### n8n → n8n Cloud

1. Create account at https://n8n.io
2. Import `n8n-workflows/main-qa-pipeline.json`
3. Update webhook URLs to use n8n Cloud URLs
4. Update `N8N_WEBHOOK_BASE_URL` in your backend env

---

## Troubleshooting

### "Connection refused" on API calls
- Check backend is running: `docker compose ps`
- Check `NEXT_PUBLIC_API_URL` is set correctly

### "OPENAI_API_KEY not set"
- Make sure `.env` has `OPENAI_API_KEY=sk-...`
- Restart the backend container: `docker compose restart backend`

### Database migration errors
- Reset: `docker compose down -v && docker compose up -d`
- Then re-run: `docker compose exec backend alembic upgrade head`

### n8n webhook not firing
- Confirm n8n is running: http://localhost:5678
- Check the workflow is **active** (toggle in n8n UI)
- Verify `WEBHOOK_URL` env var in n8n container matches your host
