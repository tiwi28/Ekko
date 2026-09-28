"""RSS / Atom feeds adapter (uses feedparser)."""

from datetime import datetime

from app.ingestion.base import SourceAdapter
from app.ingestion.normalize import NormalizedItem

# Starter list; edit freely.
DEFAULT_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://github.blog/feed/",
    "https://blog.pragmaticengineer.com/rss/",
]


class RSSAdapter(SourceAdapter):
    slug = "rss"

    def __init__(self, *args, feeds: list[str] | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.feeds = feeds or DEFAULT_FEEDS

    def fetch(self, since: datetime) -> list[NormalizedItem]:
        """TODO:
        - for each feed: download with self.client, parse with feedparser.parse(resp.content)
        - one failing feed shouldn't sink the rest (try/except per feed)
        - external_id = entry.id or entry.link
        - published_at from entry.published_parsed / updated_parsed (a UTC struct_time)
        - feeds have no engagement signal: leave engagement = 0
        - keep the feed URL in raw_json so you can tell feeds apart later
        """
        raise NotImplementedError
