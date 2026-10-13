# Ekko

A daily tech news digest for aspiring software engineers, with a simple todo list built in.

Each day Ekko gathers the most relevant tech stories, summarises them, and explains why they matter for someone growing their career in software.

> Work in progress. Many endpoints are still stubs.

## Stack

FastAPI · PostgreSQL (Neon) · React + Vite

## How it fits together

```
GitHub Actions cron ──POST /digest/run──▶ FastAPI backend ◀──fetch── React frontend
                                              │
                                    raw SQL (psycopg 3)
                                              ▼
                                          Postgres
```

- **Frontend** (`frontend/`) is a single-page React app. It calls the backend over HTTP and never touches the database.
- **Backend** (`backend/`) is a FastAPI app. It serves the API and also contains the daily news pipeline.
- **Database** is Postgres, accessed with **raw SQL only**: no ORM and no query builder. The schema lives in hand-written, numbered migration files.
- **Scheduler** is a GitHub Actions workflow (`.github/workflows/daily.yml`) that calls a secret-protected endpoint once a day to build that day's digest.

## The daily pipeline

`backend/app/ingestion/run_daily.py` runs these steps in order:

1. **Fetch**: each source adapter (`hackernews.py`, `reddit.py`, `rss.py`) implements the `SourceAdapter` interface in `base.py` and pulls recent stories.
2. **Normalize**: every story is converted into one common shape (`normalize.py`), regardless of where it came from.
3. **Dedupe**: the same story appearing twice is collapsed, and new items are saved (`dedupe.py`).
4. **Tag**: stories are matched to topics using keyword lists (`tagging.py`).
5. **Score**: candidates are ranked by recency, engagement and source weight, and the top N are picked (`scoring.py`).
6. **Enrich**: Gemini writes a summary and a "why it matters" line for each pick (`enrich.py`).

The result is stored as one `digests` row per day, with its ranked `digest_items`.

## Code map

### Backend (`backend/app/`)

| File | What it does |
|---|---|
| `main.py` | Creates the app, opens the DB connection pool on startup, sets up CORS, and mounts the routers |
| `config.py` | Typed settings read from environment variables |
| `db.py` | The psycopg connection pool, plus a dependency that gives each request its own transaction |
| `security.py` | Password hashing and the "who is the current user" dependency |
| `schemas.py` | Pydantic models for request and response bodies |
| `routers/auth.py` | Sign up, log in, log out, current user |
| `routers/topics.py` | All topics, and the user's chosen topics |
| `routers/digest.py` | Today's digest, recording clicks/saves, and the cron endpoint |
| `routers/tasks.py` | The user's todo list |
| `ingestion/` | The daily pipeline described above |

### Database (`backend/migrations/`)

`001_init.sql` defines the whole schema:

- **Users and auth**: `users` and `sessions`. Only a hash of each session token is stored, so a leaked database can't be used to log in.
- **Preferences**: `topics` (seeded with 5 topics) and `user_topics`.
- **Content**: `sources`, `items` and `item_topics`, which hold the raw stories from the pipeline.
- **Digests**: `digests`, `digest_items`, and `interactions` (views, clicks, saves, dismissals).
- **Todo**: `tasks`. Unfinished tasks from earlier days carry over into today's list.

The file explains its own design choices inline. Each foreign key has a comment explaining its `ON DELETE` behaviour, and each index has a comment naming the query it serves.

### Frontend (`frontend/src/`)

| File | What it does |
|---|---|
| `main.jsx` | Mounts React into `index.html` |
| `App.jsx` | Page layout; checks that the API is reachable |
| `api.js` | A single wrapper around `fetch` that contains every backend call |
| `components/TopicPicker.jsx` | Pick the topics you care about |
| `components/Digest.jsx` | Today's stories with summaries and "why it matters" |
| `components/TodoList.jsx` | Add and view tasks |

## Design choices

- **Raw SQL over an ORM**: every query is visible and parameterized, which makes it clear exactly what hits the database.
- **One transaction per request**: a request's writes either all commit or all roll back.
- **Scheduling with GitHub Actions instead of a worker process**: there's nothing extra to host, and the endpoint it calls is protected by a shared secret.
- **"Today" is the UTC date**: there's no per-user timezone yet.
