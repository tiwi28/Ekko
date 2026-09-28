import os

# Settings are required at import time; give tests dummy values so they never
# need a real .env. setdefault leaves real env vars alone if you have them set.
for key, value in {
    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
    "GEMINI_API_KEY": "test",
    "REDDIT_CLIENT_ID": "test",
    "REDDIT_CLIENT_SECRET": "test",
    "CRON_SECRET": "test-cron-secret",
    "JWT_SECRET": "test-jwt-secret-at-least-32-bytes-long",
}.items():
    os.environ.setdefault(key, value)
