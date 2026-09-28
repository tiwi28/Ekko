"""Hacker News adapter."""

from datetime import datetime

from app.ingestion.base import SourceAdapter
from app.ingestion.normalize import NormalizedItem


class HackerNewsAdapter(SourceAdapter):
    slug = "hackernews"

    # Official Firebase API: https://github.com/HackerNews/API
    TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
    # Alternative: Algolia search API supports time filters in one request
    # https://hn.algolia.com/api/v1/search?tags=story&numericFilters=created_at_i>TS

    def __init__(self, *args, max_stories: int = 100, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.max_stories = max_stories

    def fetch(self, since: datetime) -> list[NormalizedItem]:
        """TODO:
        - get top story ids, take the first max_stories
        - fetch each item (or use Algolia to avoid N requests)
        - skip non-"story" types, dead/deleted items, and anything older than since
        - external_id = str(id); url falls back to the HN discussion page for Ask HN
        - engagement = score (maybe + descendants)
        """
        raise NotImplementedError
