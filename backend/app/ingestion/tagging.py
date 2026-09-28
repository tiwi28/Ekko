"""Assign topics to items."""

from psycopg import Connection

# Starter keyword map, keyed by topics.slug. Tune as you go.
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "ai-ml": ["ai", "llm", "gpt", "gemini", "claude", "machine learning", "neural", "model"],
    "big-tech": ["google", "apple", "meta", "microsoft", "amazon", "nvidia"],
    "startups-funding": ["startup", "raises", "series a", "series b", "seed", "funding", "yc"],
    "hiring-layoffs": ["hiring", "layoff", "laid off", "job market", "interview", "new grad"],
    "dev-tools": ["github", "vscode", "rust", "python", "typescript", "framework", "release"],
}


def tag_item(title: str, text: str | None) -> set[str]:
    """Return the topic slugs that match this item.

    TODO: keyword match against lowercased title (+ text). Watch out for
    substring false positives ("ai" in "said") - match on word boundaries.
    """
    raise NotImplementedError


def tag_items(conn: Connection, item_ids: list[int]) -> None:
    """Tag each stored item and write item_topics rows.

    TODO:
      - SQL: load id, title, raw_text for item_ids
      - call tag_item for each
      - SQL: insert (item_id, topic_id) pairs, resolving slug -> topic id
             ON CONFLICT DO NOTHING (re-running the pipeline must be safe)
    """
    raise NotImplementedError
