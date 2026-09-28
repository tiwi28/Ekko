"""Read digests, record interactions, and the cron-protected endpoint that builds today's digest."""

import datetime as dt
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from psycopg import Connection
from psycopg_pool import ConnectionPool

from app.db import get_conn
from app.ingestion.run_daily import run_daily
from app.schemas import DigestOut, InteractionIn, RunAccepted
from app.security import get_current_user_id, require_cron_secret

log = logging.getLogger(__name__)

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/today", response_model=DigestOut)
def get_today(
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> DigestOut:
    """Today's digest (UTC), filtered to the user's topics."""
    return get_by_date(dt.datetime.now(dt.UTC).date(), user_id, conn)


@router.get("/{digest_date}", response_model=DigestOut)
def get_by_date(
    digest_date: dt.date,
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> DigestOut:
    """Digest for a given date, filtered to the user's topics.

    TODO:
      - SQL: find the digest id for digest_date; 404 if none
      - SQL: select digest_items joined to items (title, url, source,
        published_at) and topics, ordered by rank
      - filter to the user's topics (decide: what if they picked none?)
      - optionally hide items the user dismissed (interactions table)
    """
    raise NotImplementedError("get_by_date")


@router.post("/items/{digest_item_id}/interactions", status_code=status.HTTP_204_NO_CONTENT)
def record_interaction(
    digest_item_id: int,
    body: InteractionIn,
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> None:
    """Log a view / click / save / dismiss.

    TODO:
      - SQL: insert into interactions
      - catch psycopg.errors.ForeignKeyViolation -> 404 (unknown digest item)
    """
    raise NotImplementedError("record_interaction")


def _run_in_background(pool: ConnectionPool, for_date: dt.date) -> None:
    # Background tasks run after the response is sent, so the request's
    # get_conn connection is already gone. Borrow a fresh one from the pool.
    try:
        with pool.connection() as conn:
            run_daily(conn, for_date)
    except Exception:
        log.exception("daily run failed for %s", for_date)


@router.post(
    "/run",
    response_model=RunAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_cron_secret)],
)
def trigger_daily_run(request: Request, background: BackgroundTasks) -> RunAccepted:
    """Called once a day by GitHub Actions with the X-Cron-Secret header.

    Returns 202 immediately and runs the pipeline in the background, because
    fetching + Gemini calls can outlast the HTTP client's timeout.
    """
    for_date = dt.datetime.now(dt.UTC).date()
    background.add_task(_run_in_background, request.app.state.pool, for_date)
    return RunAccepted(date=for_date)
