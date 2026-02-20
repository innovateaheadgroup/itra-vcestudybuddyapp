# VCE Prep Buddy (MVP)

Production-ready MVP for **VCE Applied Computing (2025+ accreditation)** covering:

- **Software Development** and **Data Analytics**
- **Units 1-4**
- **Foundation Track (Units 1-2)** + **Scored Track (Units 3-4)** with integrity guardrails

## Monorepo structure

```txt
/apps/web            React + Vite + TypeScript + Tailwind
/apps/api            FastAPI + SQLAlchemy 2 + Alembic + Postgres
/packages/shared     Shared TS constants/types
```

## Core routes in app

- `/dashboard`
- `/learn`
- `/practice`
- `/exam-skills`
- `/buddy`
- `/tools/code-lab`
- `/tools/data-lab`
- `/quick-wins`
- `/sat` (hidden in Units 1-2)
- `/projects`
- `/profile`

## Tech stack

- **Frontend:** React, Vite, TypeScript, Tailwind, React Router, React Query
- **Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Database:** Postgres
- **Auth:** JWT access + refresh, password reset flow (email stub)
- **Testing:** pytest (backend)
- **Dev containers:** Docker Compose (`web` + `api` + `postgres`)

---

## 1) Quick start (Docker Compose)

From repo root:

```bash
docker compose up --build
```

Services:

- Web: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Postgres: localhost:5432

### Seed data (inside API container or local shell)

```bash
cd apps/api
python scripts/seed.py
```

Demo user:

- `student@example.com`
- `ChangeMe123!`

---

## 2) Local development without Docker

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Lint/format/test:

```bash
ruff check .
black .
pytest -q
```

### Frontend

```bash
npm install
npm run dev --workspace apps/web
```

Lint/format:

```bash
npm run lint --workspace apps/web
npm run format --workspace apps/web
```

---

## 3) Migrations

```bash
cd apps/api
alembic upgrade head
```

Initial migration: `apps/api/alembic/versions/0001_initial.py`

---

## 4) Environment variables

Copy `.env.example` and override values in deployment environments.

Important vars:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS`
- `LLM_PROVIDER` (`mock` by default)
- `LLM_MODEL`
- `BUDDY_SCORING_REFUSAL_PATTERNS`
- `CODE_RUN_RATE_LIMIT_PER_MINUTE`
- `CODE_RUN_TIMEOUT_SECONDS`
- `MAX_UPLOAD_SIZE_MB`
- `FRONTEND_URL`

> No external API keys are required to run locally. Buddy uses a mock provider by default.

---

## 5) Deployment notes

- Set `APP_ENV=production`
- Provide strong JWT secrets via environment variables
- Use managed Postgres and secure `DATABASE_URL`
- Configure trusted CORS origins
- Run migrations during deploy (`alembic upgrade head`)
- Seed only in non-production or controlled setup steps

---

## 6) Feature highlights

- Curriculum map: subjects -> topics -> lessons -> questions
- Practice engine with set builder, marking, rubric feedback
- Exam Skills templates + command terms + timed practice + case annotation scaffolds
- Buddy coaching endpoint with scored-mode refusal policy
- Code Lab runner with rate limits and safety guardrails
- Data Lab CSV preview, inferred types, cleaning suggestions, chart config persistence
- Quick Wins spaced repetition scheduler
- SAT Hub tracker, milestones, evidence log, HTML export
- Units 1-2 Projects module with submission + stub feedback
