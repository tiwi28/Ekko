"""Daily pipeline entrypoint.

Called by POST /digest/run (from the GitHub Actions cron), or manually:

    python -m app.ingestion.run_daily                 # today (UTC)
    python -m app.ingestion.run_daily 2026-09-28      # specific date
"""

import datetime as dt
import logging
import sys

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from app.config import get_settings
from app.ingestion.enrich import EnrichedItem

log = logging.getLogger(__name__)


def write_digest(conn: Connection, for_date: dt.date, items: list[EnrichedItem]) -> int:
    """Persist the day's digest and return its id.

    TODO:
      - SQL: insert into digests (date) ... ON CONFLICT (date) - decide whether a
        re-run replaces the day's digest (delete + reinsert; digest_items CASCADE)
        or is a no-op
      - SQL: insert one digest_items row per EnrichedItem
    """
    raise NotImplementedError


def run_daily(conn: Connection, for_date: dt.date) -> None:
    settings = get_settings()
    since = dt.datetime.combine(for_date, dt.time.min, dt.UTC) - dt.timedelta(days=1)
    log.info("daily run starting for %s (since %s)", for_date, since.isoformat())

    # 1. Fetch from every source (one failing source shouldn't stop the others)
    # from app.ingestion.hackernews import HackerNewsAdapter
    # from app.ingestion.rss import RSSAdapter
    # from app.ingestion.reddit import RedditAdapter
    # adapters = [HackerNewsAdapter(), RSSAdapter(), RedditAdapter(settings)]
    # raw = []
    # for adapter in adapters:
    #     try:
    #         raw.extend(adapter.fetch(since))
    #     except Exception:
    #         log.exception("source %s failed", adapter.slug)

    # 2. Normalize into the common shape
    # from app.ingestion.normalize import normalize
    # items = normalize(raw)

    # 3. Dedupe within the batch, then store (ON CONFLICT skips previously seen items)
    # from app.ingestion.dedupe import dedupe, store_items
    # items = dedupe(items)
    # item_ids = store_items(conn, items)

    # 4. Tag by topic
    # from app.ingestion.tagging import tag_items
    # tag_items(conn, item_ids)

    # 5. Score and pick the top N
    # from app.ingestion.scoring import select_top
    # top = select_top(conn, for_date, limit=settings.digest_size)

    # 6. Enrich with Gemini (summary + why it matters)
    # from app.ingestion.enrich import enrich_items
    # enriched = enrich_items(conn, settings, top)

    # 7. Write the digest
    # digest_id = write_digest(conn, for_date, enriched)
    # log.info("wrote digest %s with %d items", digest_id, len(enriched))

    log.warning("run_daily is a stub: pipeline steps are commented out")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for_date = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(dt.UTC).date()
    # A plain connection is enough for a one-off run; the with block commits on success.
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as conn:
        run_daily(conn, for_date)


if __name__ == "__main__":
    main()
