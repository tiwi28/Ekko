"""List topics and manage the current user's topic selection."""

from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db import get_conn
from app.schemas import TopicOut, TopicSelection
from app.security import get_current_user_id

router = APIRouter(prefix="/topics", tags=["topics"])

# Stub data matching the seed rows in 001_init.sql, so the frontend has something
# to render before the real query exists. Delete once list_topics hits the DB.
_STUB_TOPICS = [
    TopicOut(id=1, slug="ai-ml", name="AI & Machine Learning"),
    TopicOut(id=2, slug="big-tech", name="Big Tech"),
    TopicOut(id=3, slug="startups-funding", name="Startups & Funding"),
    TopicOut(id=4, slug="hiring-layoffs", name="Hiring & Layoffs"),
    TopicOut(id=5, slug="dev-tools", name="Developer Tools"),
]


@router.get("", response_model=list[TopicOut])
def list_topics(conn: Connection = Depends(get_conn)) -> list[TopicOut]:
    """All available topics.

    TODO:
      - SQL: select every topic, ordered by name
      - replace the stub return below
    """
    return _STUB_TOPICS


@router.get("/me", response_model=list[TopicOut])
def my_topics(
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> list[TopicOut]:
    """Topics the current user has selected.

    TODO:
      - SQL: join user_topics -> topics for user_id
    """
    raise NotImplementedError("my_topics")


@router.put("/me", response_model=list[TopicOut])
def set_my_topics(
    body: TopicSelection,
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> list[TopicOut]:
    """Replace the current user's selection with ``body.slugs``.

    TODO:
      - SQL: resolve slugs to topic ids; 422 if any slug is unknown
      - SQL: delete existing user_topics rows for user_id
      - SQL: insert the new rows
        (all of this runs in one transaction because get_conn wraps the request)
      - return the new selection
    """
    raise NotImplementedError("set_my_topics")
