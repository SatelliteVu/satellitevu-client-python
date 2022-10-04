from typing import Dict, Optional

from pytest import fixture

from .auth.cache import AbstractCache


class MemoryCache(AbstractCache):
    cache: Dict[str, str]

    def __init__(self):
        super().__init__()
        self.cache = {}

    def save(self, client_id: str, value: str):
        self.cache[client_id] = value

    def load(self, client_id: str) -> Optional[str]:
        return self.cache.get(client_id)


@fixture
def memory_cache():
    return MemoryCache()
