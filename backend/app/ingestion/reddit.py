"""Reddit adapter (OAuth app-only via httpx, no praw)."""

from datetime import datetime

from app.config import Settings
from app.ingestion.base import SourceAdapter
from app.ingestion.normalize import NormalizedItem

DEFAULT_SUBREDDITS = ["cscareerquestions", "programming", "technology", "MachineLearning"]


class RedditAdapter(SourceAdapter):
    slug = "reddit"

    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    API_BASE = "https://oauth.reddit.com"

    def __init__(
        self, settings: Settings, *args, subreddits: list[str] | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.subreddits = subreddits or DEFAULT_SUBREDDITS

    def _get_token(self) -> str:
        """TODO: POST grant_type=client_credentials to TOKEN_URL with HTTP basic
        auth (client_id, client_secret) and the configured User-Agent; return
        access_token."""
        raise NotImplementedError

    def fetch(self, since: datetime) -> list[NormalizedItem]:
        """TODO:
        - GET {API_BASE}/r/{sub}/top?t=day&limit=50 with "Authorization: bearer <token>"
        - skip stickied / over_18 posts and anything older than since (created_utc)
        - external_id = post "name" (e.g. t3_abc123)
        - url = post url for link posts, permalink for self posts
        - engagement = score (maybe + num_comments)
        """
        raise NotImplementedError
