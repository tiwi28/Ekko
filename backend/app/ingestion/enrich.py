"""Gemini: summary + "why this matters for you" for each selected item."""

from dataclasses import dataclass

from psycopg import Connection

from app.config import Settings
from app.ingestion.scoring import ScoredItem

PROMPT_TEMPLATE = """\
You are writing for aspiring software engineers (students and early-career devs).

Title: {title}
Source: {source}
URL: {url}
Text: {text}

Return JSON with two fields:
  "summary": 2-3 plain sentences on what happened.
  "why_it_matters": 1-2 sentences on why this matters to someone trying to
                    break into or grow in software engineering.
"""


@dataclass(slots=True)
class EnrichedItem:
    item_id: int
    topic_id: int | None
    rank: int
    summary: str
    why_it_matters: str


def enrich_one(settings: Settings, *, title: str, source: str, url: str, text: str | None) -> tuple[str, str]:
    """Call Gemini for one item and return (summary, why_it_matters).

    TODO:
      - from google import genai; client = genai.Client(api_key=settings.gemini_api_key)
      - client.models.generate_content(model=settings.gemini_model, contents=prompt,
        config={"response_mime_type": "application/json"})
      - parse JSON; on failure fall back to something sane rather than crash the run
      - retry once on 429/5xx
    """
    raise NotImplementedError


def enrich_items(conn: Connection, settings: Settings, top: list[ScoredItem]) -> list[EnrichedItem]:
    """Enrich each selected item, preserving rank order (rank 1 = best).

    TODO:
      - SQL: load title, source, url, raw_text for the top item ids
      - call enrich_one for each (sequential is fine for ~10 items)
    """
    raise NotImplementedError
