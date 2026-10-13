-- 001_init.sql
-- Initial schema for Ekko.
--
-- Applied by migrate.py, which runs this file and records version 001 in
-- schema_migrations inside ONE transaction. That's why there is no
-- BEGIN/COMMIT here: a COMMIT in the file would make the schema permanent
-- before it was recorded, so a crash in between would leave the DB changed
-- but "unmigrated" and the next run would fail on CREATE TABLE.
--
-- Conventions
--   * Surrogate keys are BIGINT GENERATED ALWAYS AS IDENTITY (the modern
--     replacement for SERIAL).
--   * All timestamps are TIMESTAMPTZ and stored in UTC.
--   * "Today" means the current UTC date for now (no per-user timezone yet).
--   * ON DELETE behaviour is chosen per FK and explained inline.

-- ---------------------------------------------------------------------------
-- Users & preferences
-- ---------------------------------------------------------------------------

CREATE TABLE users (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email          TEXT        NOT NULL UNIQUE,
    password_hash  TEXT        NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Emails are compared case-sensitively by UNIQUE, so force lowercase on write.
    CONSTRAINT users_email_lowercase CHECK (email = lower(email))
);

CREATE TABLE sessions (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- CASCADE: a session is meaningless without its user; deleting the user
    -- logs them out everywhere.
    user_id     BIGINT      NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    -- SHA-256 hex of the raw cookie token; the raw token is never stored, so
    -- a leaked DB dump can't be replayed as live sessions. A fast hash is
    -- fine here (unlike passwords) because the token is 32 random bytes,
    -- far too much entropy to brute-force.
    -- The UNIQUE index serves the per-request auth lookup:
    --   WHERE token_hash = $1 AND expires_at > now()
    -- so no separate index on token_hash is needed.
    token_hash  TEXT        NOT NULL UNIQUE CHECK (length(token_hash) = 64),
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT sessions_expires_after_created CHECK (expires_at > created_at)
);

CREATE TABLE topics (
    id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    slug  TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL
);

CREATE TABLE user_topics (
    -- A preference row means nothing without its user or topic, so both CASCADE.
    user_id   BIGINT NOT NULL REFERENCES users (id)  ON DELETE CASCADE,
    topic_id  BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    -- The PK index leads with user_id, so it also serves GET /me/topics
    -- (WHERE user_id = $1) and the delete half of PUT /me/topics
    -- (DELETE ... WHERE user_id = $1). No separate user_id index needed.
    PRIMARY KEY (user_id, topic_id)
);

-- ---------------------------------------------------------------------------
-- Ingested content
-- ---------------------------------------------------------------------------

CREATE TABLE sources (
    slug    TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    -- Multiplier applied during scoring so sources can be trusted differently.
    weight  NUMERIC(4, 2) NOT NULL DEFAULT 1.00 CHECK (weight >= 0)
);

CREATE TABLE items (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- RESTRICT: deleting a source that still has items is almost certainly a
    -- mistake. Delete (or re-point) its items first.
    -- ON UPDATE CASCADE lets you rename a source slug without orphaning rows.
    source        TEXT        NOT NULL REFERENCES sources (slug)
                              ON DELETE RESTRICT ON UPDATE CASCADE,
    external_id   TEXT        NOT NULL,   -- id in the upstream system (HN id, reddit fullname, feed guid)
    url           TEXT        NOT NULL,
    title         TEXT        NOT NULL,
    raw_text      TEXT,
    author        TEXT,
    published_at  TIMESTAMPTZ NOT NULL,
    engagement    INTEGER     NOT NULL DEFAULT 0 CHECK (engagement >= 0),  -- points / upvotes / comments
    raw_json      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE item_topics (
    -- Tags are derived data; they go wherever the item or topic goes.
    item_id   BIGINT NOT NULL REFERENCES items (id)  ON DELETE CASCADE,
    topic_id  BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, topic_id)
);

-- ---------------------------------------------------------------------------
-- Digests
-- ---------------------------------------------------------------------------

CREATE TABLE digests (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date        DATE        NOT NULL UNIQUE,   -- one digest per calendar day (UTC)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE digest_items (
    -- Surrogate id so interactions can point at a single digest entry.
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- CASCADE: regenerating a day's digest = delete the digest row, rebuild.
    digest_id       BIGINT  NOT NULL REFERENCES digests (id) ON DELETE CASCADE,
    -- RESTRICT: a published digest should never silently lose an entry
    -- because someone pruned old items. Prune digests first.
    item_id         BIGINT  NOT NULL REFERENCES items (id)   ON DELETE RESTRICT,
    -- SET NULL: removing a topic shouldn't erase history; the entry just
    -- becomes "untagged". Hence nullable.
    topic_id        BIGINT           REFERENCES topics (id)  ON DELETE SET NULL,
    summary         TEXT    NOT NULL,
    why_it_matters  TEXT    NOT NULL,
    rank            INTEGER NOT NULL CHECK (rank > 0),
    -- The same story shouldn't appear twice in one day's digest.
    CONSTRAINT digest_items_digest_item_key UNIQUE (digest_id, item_id)
);

-- ---------------------------------------------------------------------------
-- User activity
-- ---------------------------------------------------------------------------

CREATE TABLE interactions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- CASCADE on both: activity is personal data (goes with the user) and is
    -- meaningless once the digest entry is gone.
    user_id         BIGINT      NOT NULL REFERENCES users (id)        ON DELETE CASCADE,
    digest_item_id  BIGINT      NOT NULL REFERENCES digest_items (id) ON DELETE CASCADE,
    action          TEXT        NOT NULL
                    CHECK (action IN ('view', 'click', 'save', 'dismiss')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tasks (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id            BIGINT      NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    title              TEXT        NOT NULL CHECK (length(trim(title)) > 0),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at       TIMESTAMPTZ,          -- NULL = still open
    carried_from_date  DATE,                 -- set when an unfinished task rolls over to a new day
    CONSTRAINT tasks_completed_after_created CHECK (completed_at IS NULL OR completed_at >= created_at)
);

-- ---------------------------------------------------------------------------
-- Indexes
--
-- Note: PRIMARY KEY and UNIQUE constraints above already create their own
-- indexes (users.email, topics.slug, digests.date, the composite PKs, ...).
-- These are the extra ones.
-- ---------------------------------------------------------------------------

-- Serves the scoring/ranking step: "items published in the last 24-48h",
-- i.e. WHERE published_at >= now() - interval '1 day'. Also keeps pruning
-- old items (WHERE published_at < ...) cheap.
CREATE INDEX items_published_at_idx ON items (published_at);

-- Serves ingestion dedupe: INSERT ... ON CONFLICT (source, external_id) DO ...
-- ON CONFLICT needs a unique index/constraint on exactly these columns.
CREATE UNIQUE INDEX items_source_external_id_key ON items (source, external_id);

-- Serves GET /me/tasks, both halves:
--   today:       WHERE user_id = $1 AND created_at >= <start of today UTC>
--   carry-overs: WHERE user_id = $1 AND created_at <  <start of today UTC>
--                  AND completed_at IS NULL
--                ranked ROW_NUMBER() OVER (ORDER BY created_at DESC), keep <= 5
-- Both are a range on created_at within one user. The index can be scanned
-- backwards, so it also serves the DESC ordering.
CREATE INDEX tasks_user_id_created_at_idx ON tasks (user_id, created_at);

-- Serves ON DELETE CASCADE from users (Postgres does NOT index FK columns
-- automatically; without this, deleting a user scans all of sessions) and
-- a future "log out everywhere" (DELETE FROM sessions WHERE user_id = $1).
CREATE INDEX sessions_user_id_idx ON sessions (user_id);

-- Serves per-user activity lookups: "what has this user clicked/dismissed
-- recently?" (WHERE user_id = $1 AND created_at >= ...), e.g. for hiding
-- dismissed stories or future personalisation.
CREATE INDEX interactions_user_id_created_at_idx ON interactions (user_id, created_at);

-- Serves reading a digest: "all entries for digest X" (WHERE digest_id = $1
-- ORDER BY rank). The UNIQUE (digest_id, item_id) constraint also leads with
-- digest_id, but this one keeps the rank-ordered read explicit.
CREATE INDEX digest_items_digest_id_idx ON digest_items (digest_id);

-- ---------------------------------------------------------------------------
-- Seed data
-- ---------------------------------------------------------------------------

INSERT INTO topics (slug, name) VALUES
    ('ai-ml',            'AI & Machine Learning'),
    ('big-tech',         'Big Tech'),
    ('startups-funding', 'Startups & Funding'),
    ('hiring-layoffs',   'Hiring & Layoffs'),
    ('dev-tools',        'Developer Tools');

INSERT INTO sources (slug, name, weight) VALUES
    ('hackernews', 'Hacker News', 1.00),
    ('rss',        'RSS Feeds',   1.00),
    ('reddit',     'Reddit',      0.80);
