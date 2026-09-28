# Ekko

A daily tech news digest for aspiring software engineers, with a simple todo list underneath.

Once a day a cron job pulls stories from Hacker News, RSS feeds and Reddit. The pipeline dedupes them, tags them by topic, scores them, picks the top ~10, asks Gemini for a summary and a "why this matters for you" blurb for each, and writes that day's digest.

| Layer    | Tech                                        | Hosted on       |
|----------|---------------------------------------------|-----------------|
| Backend  | FastAPI (Python 3.11+), psycopg 3, raw SQL  | Render          |
| Database | Postgres                                    | Neon            |
| Frontend | React + Vite                                | Vercel          |
| Cron     | GitHub Actions calling `POST /digest/run`   | GitHub          |

> **Status:** scaffold only. Endpoints and pipeline steps are stubs that raise
> `NotImplementedError` (the API returns **501** for these). Look for `TODO` in the code.

## Layout

```
backend/
  app/
    main.py          FastAPI app, lifespan (DB pool), CORS, routers, /health
    config.py        env vars via pydantic-settings
    db.py            psycopg ConnectionPool + get_conn() dependency
    security.py      password hashing (stdlib scrypt), JWT, auth + cron-secret dependencies
    schemas.py       Pydantic request/response models (API contract)
    models.py        plain dataclasses mirroring DB rows (no ORM)
    routers/         auth, topics, digest, tasks
    ingestion/       source adapters + the 7 pipeline steps, run_daily.py entrypoint
  migrations/        hand-written, numbered .sql files
  tests/
frontend/            Vite + React
.github/workflows/daily.yml
```

## Prerequisites

- Python 3.11+
- Node 20+
- `psql`, the Postgres client (ships with Postgres; on Windows `winget install PostgreSQL.PostgreSQL` or use the Neon SQL editor)
- A Neon project (free tier is fine)

## 1. Database

Create a database in Neon and copy its connection string (keep `?sslmode=require`).

### Running migrations

Migrations are plain SQL files in `backend/migrations/`, applied in number order. Each one runs inside `BEGIN; ... COMMIT;`, so a failure leaves nothing half-applied.

```bash
cd backend
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/001_init.sql
```

PowerShell:

```powershell
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f migrations/001_init.sql
```

Check it worked:

```bash
psql "$DATABASE_URL" -c "\dt"
psql "$DATABASE_URL" -c "SELECT * FROM topics;"
```

Adding a migration: create `002_whatever.sql` with its own `BEGIN; ... COMMIT;`. Never edit a migration you've already applied somewhere; write a new one instead. There's no tracking table yet, so keep a note of which files each environment has had. (Adding a `schema_migrations` table and a small runner script is a good exercise.)

Starting over locally (**deletes everything**):

```sql
DROP SCHEMA public CASCADE; CREATE SCHEMA public;
```

## 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in the values
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Tests (no database needed):

```bash
pytest
```

## 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local         # VITE_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173. The backend's `CORS_ORIGINS` must include this origin (it does by default).

## 4. The daily job

### Run it manually

**A. Directly, no server needed** (easiest while developing the pipeline):

```bash
cd backend
python -m app.ingestion.run_daily              # today (UTC)
python -m app.ingestion.run_daily 2026-09-28   # a specific date
```

**B. Through the HTTP endpoint** (what the cron does). The endpoint returns `202` right away and runs the pipeline in the background, so watch the uvicorn logs:

```bash
curl -X POST http://localhost:8000/digest/run -H "X-Cron-Secret: <your CRON_SECRET>"
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/digest/run -Headers @{ "X-Cron-Secret" = "<your CRON_SECRET>" }
```

**C. From GitHub:** Actions tab → *Daily digest* → *Run workflow*.

### The scheduled run

`.github/workflows/daily.yml` runs at 11:00 UTC every day. Add these under repo → Settings → Secrets and variables → Actions:

| Secret        | Value                                          |
|---------------|------------------------------------------------|
| `BACKEND_URL` | your Render URL, e.g. `https://ekko-api.onrender.com` |
| `CRON_SECRET` | the same value as the backend's `CRON_SECRET`  |

Pipeline steps, in `backend/app/ingestion/run_daily.py`:

1. **Fetch**: `hackernews.py`, `rss.py`, `reddit.py` (all `SourceAdapter` subclasses from `base.py`)
2. **Normalize**: `normalize.py`
3. **Dedupe + store**: `dedupe.py`
4. **Tag**: `tagging.py`
5. **Score + select top N**: `scoring.py`
6. **Enrich with Gemini**: `enrich.py`
7. **Write digest**: `run_daily.write_digest`

## Deploy

**Backend on Render:** New → Web Service → point it at this repo.
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Environment: everything from `.env.example`, with `CORS_ORIGINS` set to your Vercel URL

**Frontend on Vercel:** import the repo.
- Root directory: `frontend`
- Framework preset: Vite
- Env var: `VITE_API_URL=https://<your-render-app>.onrender.com`

On Render's free tier the service sleeps after about 15 minutes idle. The workflow's `curl` retries with a long timeout to give it time to wake up.

## Environment variables

See `backend/.env.example`. Required: `DATABASE_URL`, `GEMINI_API_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `CRON_SECRET`, `JWT_SECRET`. To generate a secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
