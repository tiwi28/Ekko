"""Pydantic request/response models for the HTTP API (the API contract, separate from DB rows)."""

import datetime as dt
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

# ---- auth -------------------------------------------------------------------


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: dt.datetime


# ---- topics -----------------------------------------------------------------


class TopicOut(BaseModel):
    id: int
    slug: str
    name: str


class TopicSelection(BaseModel):
    slugs: list[str]


# ---- digest -----------------------------------------------------------------


class DigestItemOut(BaseModel):
    id: int
    rank: int
    title: str
    url: str
    source: str
    topic: TopicOut | None
    summary: str
    why_it_matters: str
    published_at: dt.datetime


class DigestOut(BaseModel):
    id: int
    date: dt.date
    items: list[DigestItemOut]


class InteractionIn(BaseModel):
    action: Literal["view", "click", "save", "dismiss"]


class RunAccepted(BaseModel):
    status: Literal["accepted"] = "accepted"
    date: dt.date


# ---- tasks ------------------------------------------------------------------


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    completed: bool | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    created_at: dt.datetime
    completed_at: dt.datetime | None
    carried_from_date: dt.date | None
