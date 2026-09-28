# Ekko

A daily tech news digest for aspiring software engineers, with a simple todo list built in.

Each day Ekko gathers the most relevant tech stories, summarises them, and explains why they matter for someone growing their career in software.

## Stack

FastAPI · PostgreSQL · React + Vite

## Running locally

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in the values
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

> Work in progress.
