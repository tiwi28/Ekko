"""Postgres connection pool (psycopg 3) and the FastAPI dependency that hands out connections.

Usage in a route:

    @router.get("/things")
    def list_things(conn: Connection = Depends(get_conn)):
        rows = conn.execute("SELECT ...", (param,)).fetchall()

Rows come back as dicts (``dict_row``). Each request gets its own connection,
wrapped in a transaction that commits when the request succeeds and rolls back
if it raises.
"""

from collections.abc import Iterator

from fastapi import Request
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import Settings


def create_pool(settings: Settings) -> ConnectionPool:
    """Build the pool without opening it; open/close happen in the app lifespan."""
    return ConnectionPool(
        conninfo=settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        kwargs={"row_factory": dict_row},
        # Neon closes idle connections; check before handing one out.
        check=ConnectionPool.check_connection,
        open=False,
    )


def get_conn(request: Request) -> Iterator[Connection]:
    """FastAPI dependency: borrow a connection from the pool for one request.

    ``pool.connection()`` commits on clean exit and rolls back on exception,
    then returns the connection to the pool.
    """
    pool: ConnectionPool = request.app.state.pool
    with pool.connection() as conn:
        yield conn
