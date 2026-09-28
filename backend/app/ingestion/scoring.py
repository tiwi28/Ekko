"""Score candidate items and pick the top N for the digest."""

import datetime as dt
from dataclasses import dataclass

from psycopg import Connection


@dataclass(slots=True)
class ScoredItem:
    item_id: int
    topic_id: int | None   # the topic this item will be filed under in the digest
    score: float


def score(engagement: int, source_weight: float, age_hours: float) -> float:
    """Score one item.

    TODO: pick a formula. Something HN-like is a good start:
        (engagement + 1) * source_weight / (age_hours + 2) ** 1.5
    Engagement scales differ wildly between sources; consider normalising per
    source (percentile or log) before combining.
    """
    raise NotImplementedError


def select_top(conn: Connection, for_date: dt.date, limit: int = 10) -> list[ScoredItem]:
    """Return the best ``limit`` items for the digest on ``for_date``.

    TODO (this is the ranking query - yours to write):
      - candidates: items published in the window before for_date
        (items_published_at_idx serves this)
      - join sources for weight and item_topics for topic
      - exclude items already used in a previous digest
      - order by score, maybe cap per topic so one topic can't take all 10
      - do the scoring in SQL, in Python via score(), or a mix
    """
    raise NotImplementedError
