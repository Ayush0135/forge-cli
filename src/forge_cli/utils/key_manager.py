import itertools
from typing import List


class RoundRobinKeyManager:
    """Manages round-robin rotation of API keys to bypass rate limits."""

    def __init__(self, keys: List[str]):
        if not keys:
            raise ValueError("At least one API key must be provided.")
        self.keys = keys
        self._cycle = itertools.cycle(self.keys)
        self.current_key = next(self._cycle)

    def get_key(self) -> str:
        """Get the current API key to use."""
        return self.current_key

    def next_key(self) -> str:
        """Mark the current key as exhausted/rate-limited and move to the next one."""
        self.current_key = next(self._cycle)
        return self.current_key
