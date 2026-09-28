"""Plain dataclasses mirroring database rows. Not ORM models: nothing here talks to the DB.

Build them from ``dict_row`` results, e.g. ``User(**row)``.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class User:
    id: int
    email: str
    password_hash: str
    created_at: datetime


@dataclass(slots=True)
class Topic:
    id: int
    slug: str
    name: str


@dataclass(slots=True)
class Source:
    slug: str
    name: str
    weight: Decimal


@dataclass(slots=True)
class Item:
    id: int
    source: str
    external_id: str
    url: str
    title: str
    raw_text: str | None
    author: str | None
    published_at: datetime
    engagement: int
    raw_json: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None


@dataclass(slots=True)
class Digest:
    id: int
    date: date
    created_at: datetime


@dataclass(slots=True)
class DigestItem:
    id: int
    digest_id: int
    item_id: int
    topic_id: int | None
    summary: str
    why_it_matters: str
    rank: int


@dataclass(slots=True)
class Interaction:
    id: int
    user_id: int
    digest_item_id: int
    action: str
    created_at: datetime


@dataclass(slots=True)
class Task:
    id: int
    user_id: int
    title: str
    created_at: datetime
    completed_at: datetime | None
    carried_from_date: date | None
