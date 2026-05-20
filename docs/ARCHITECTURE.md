# QPilot AI — Architecture Decisions

## ADR-001: FastAPI over Django/Flask

**Decision:** Use FastAPI as the backend framework.

**Rationale:**
- Native async/await — required for non-blocking OpenAI API calls
- Automatic OpenAPI schema generation from type hints (free Swagger UI)
- Pydantic v2 integration for validation with near-zero boilerplate
- SQLAlchemy async support with the same codebase

---

## ADR-002: n8n for workflow orchestration

**Decision:** Use n8n as the workflow engine instead of Celery/Airflow.

**Rationale:**
- Visual workflow editor — non-engineers can inspect and modify automation flows
- Built-in retry, error handling, and webhook support
- 400+ native integrations (Slack, Jira, GitHub, etc.)
- Self-hostable with Docker; no broker (Redis/RabbitMQ) required for MVP
- Workflows are JSON-exportable for version control

**Trade-off:** n8n adds a service to run. For MVP this is acceptable.

---

## ADR-003: PostgreSQL over MongoDB

**Decision:** Use relational PostgreSQL, not document storage.

**Rationale:**
- Requirements → Scenarios → Test Cases → Scripts is a well-defined relational hierarchy
- Foreign keys enforce referential integrity at the DB level
- Complex queries (JOIN scenarios with requirements, aggregate counts) are natural in SQL
- Alembic migrations give us auditable schema evolution

---

## ADR-004: Structured JSON outputs from AI

**Decision:** All AI calls must return structured JSON, never free text.

**Rationale:**
- Free text responses from OpenAI cannot be reliably parsed into domain objects
- JSON output with a defined schema allows validation before DB insertion
- Hallucinations produce invalid JSON or fail schema validation — detectable at runtime
- Prompts explicitly state "return ONLY valid JSON" and include the output schema

**Implementation:** `prompts.py` embeds the JSON schema in every system prompt. `ai_service.py` strips markdown fences and calls `json.loads()`. Invalid JSON triggers a retry (up to 3 attempts).

---

## ADR-005: Zustand over Redux for frontend state

**Decision:** Use Zustand for global state management instead of Redux Toolkit.

**Rationale:**
- Auth state (token + user object) is the only truly global state
- Zustand has zero boilerplate vs Redux's action/reducer/selector pattern
- API server state (requirements list, scenarios) belongs in React Query (TanStack Query), not global store
- Bundle size: Zustand is ~1KB vs Redux Toolkit ~10KB

---

## ADR-006: JWT stored in localStorage (MVP)

**Decision:** Store JWT in localStorage, not httpOnly cookies, for MVP.

**Rationale:**
- Simpler to implement for MVP (no server-side cookie handling needed)
- Acceptable for a developer-facing internal tool

**Known risk:** XSS can steal the token from localStorage.

**Migration path:** In production, move to httpOnly cookies with a `/refresh` endpoint. The auth service is structured so this is a ~50 line change.

---

## ADR-007: Alembic for migrations over auto-migration

**Decision:** Use explicit Alembic revision files, not SQLAlchemy's `create_all()`.

**Rationale:**
- `create_all()` silently ignores existing tables — dangerous in production
- Alembic generates `upgrade()` and `downgrade()` scripts for safe forward and rollback
- Migration history is auditable in git

---

## ADR-008: Monorepo structure

**Decision:** All services live in one repository.

**Rationale:**
- Single PR can span backend + frontend + workflow changes atomically
- Simpler CI/CD for an MVP (one pipeline)
- Shared `.env.example` at root gives a single source of truth for required config

**Migration path:** When the team grows, split into separate repos with a shared type package.
