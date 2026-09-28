"""The common item shape every source adapter produces, plus cleanup helpers."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class NormalizedItem:
    """One story from any source, before it has a DB id.

    Maps 1:1 onto the ``items`` table columns (minus id / created_at).
    """

    source: str            # sources.slug, e.g. "hackernews"
    external_id: str       # id in the upstream system; (source, external_id) is unique
    url: str
    title: str
    published_at: datetime  # must be timezone-aware (UTC)
    raw_text: str | None = None
    author: str | None = None
    engagement: int = 0     # points / upvotes / comment count, source-specific
    raw_json: dict[str, Any] = field(default_factory=dict)


def clean_text(text: str | None) -> str | None:
    """Strip HTML tags/entities and collapse whitespace.

    TODO: RSS and HN text fields contain HTML. html.unescape + a simple tag
    strip is probably enough; truncate very long bodies before sending to Gemini.
    """
    raise NotImplementedError


def canonicalize_url(url: str) -> str:
    """Normalise a URL so the same article from two sources compares equal.

    TODO: lowercase host, drop "www.", strip utm_* / ref query params, drop
    fragments and trailing slashes. Used by dedupe.
    """
    raise NotImplementedError


def normalize(items: list[NormalizedItem]) -> list[NormalizedItem]:
    """Apply clean_text / canonicalize_url to every item and drop unusable ones.

    TODO: drop items with no title or url; ensure published_at is UTC-aware.
    """
    raise NotImplementedError
