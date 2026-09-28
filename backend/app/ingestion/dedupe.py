"""Remove duplicates within a batch and persist new items."""

from psycopg import Connection

from app.ingestion.normalize import NormalizedItem


def dedupe(items: list[NormalizedItem]) -> list[NormalizedItem]:
    """Collapse the same story appearing multiple times in this batch.

    TODO:
      - exact dupes: same (source, external_id)
      - cross-source dupes: same canonical URL (HN + Reddit often link the
        same article). Keep the one with higher engagement, or merge?
      - stretch: near-duplicate titles (normalised title equality / fuzzy match)
    """
    raise NotImplementedError


def store_items(conn: Connection, items: list[NormalizedItem]) -> list[int]:
    """Insert items, skipping ones already stored on a previous run. Return ids.

    TODO:
      - SQL: INSERT INTO items (...) VALUES (...)
             ON CONFLICT (source, external_id) DO UPDATE SET engagement = EXCLUDED.engagement
             RETURNING id
        (DO UPDATE rather than DO NOTHING so RETURNING gives ids for existing rows too,
         and engagement stays fresh)
      - raw_json needs psycopg.types.json.Jsonb(item.raw_json)
      - conn.cursor().executemany(..., returning=True) handles many rows in one go
    """
    raise NotImplementedError
