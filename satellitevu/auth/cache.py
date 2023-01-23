import os
from abc import ABC, abstractmethod
from configparser import ConfigParser, DuplicateSectionError
from os import replace
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from appdirs import user_cache_dir


class AbstractCache(ABC):
    """
    Abstract cache interface, implemented by actual cache classes
    """

    @abstractmethod
    def save(self, client_id: str, value: str):
        pass

    @abstractmethod
    def load(self, client_id: str) -> Optional[str]:
        pass


class MemoryCache(AbstractCache):
    _items = {}

    def save(self, client_id: str, value: str):
        self._items[client_id] = value

    def load(self, client_id: str) -> Optional[str]:
        return self._items.get(client_id)


class AppDirCache(AbstractCache):
    """
    File based token cache using an INI file in the user's cache dir or given dir.
    """

    cache_dir: Path
    cache_file: Path

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir if cache_dir else user_cache_dir("SatelliteVu"))
        self.cache_file = self.cache_dir / "tokencache"

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def save(self, client_id: str, value: str):
        parser = ConfigParser()
        parser.read(self.cache_file)

        try:
            parser.add_section(client_id)
        except DuplicateSectionError:
            pass
        parser[client_id]["access_token"] = value

        with NamedTemporaryFile("w", dir=str(self.cache_dir), delete=False) as handle:
            parser.write(handle)
        replace(handle.name, self.cache_file)

    def load(self, client_id: str) -> Optional[str]:
        try:
            parser = ConfigParser()
            parser.read(self.cache_file)

            return parser[client_id]["access_token"]
        except (FileNotFoundError, KeyError):
            return None
