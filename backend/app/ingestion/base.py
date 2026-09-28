"""Interface every news source implements."""

from abc import ABC, abstractmethod
from datetime import datetime

import httpx

from app.ingestion.normalize import NormalizedItem


class SourceAdapter(ABC):
    """Fetch recent stories from one upstream source.

    Subclasses set ``slug`` (must match a row in the ``sources`` table) and
    implement ``fetch``. Adapters don't touch the database.
    """

    slug: str
    timeout_seconds: float = 20.0

    def __init__(self, client: httpx.Client | None = None) -> None:
        # Share one client across adapters in run_daily if you like; tests can
        # inject an httpx.Client with a MockTransport.
        self.client = client or httpx.Client(
            timeout=self.timeout_seconds,
            headers={"User-Agent": "ekko/0.1"},
            follow_redirects=True,
        )

    @abstractmethod
    def fetch(self, since: datetime) -> list[NormalizedItem]:
        """Return stories published at or after ``since`` (UTC).

        Should not raise for a single bad story: skip it and keep going.
        May raise for total failure (network down, auth rejected) so
        run_daily can log it and carry on with the other sources.
        """
        raise NotImplementedError
