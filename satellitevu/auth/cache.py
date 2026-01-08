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
    Abstract cache interface, implemented by actual cache classes.

    Supports storing both access tokens and optional refresh tokens.
    """

    @abstractmethod
    def save(self, client_id: str, value: str, refresh_token: Optional[str] = None):
        """
        Save access token and optional refresh token to cache.

        Args:
            client_id: Cache key (typically hash of client_id + scopes)
            value: Access token to cache
            refresh_token: Optional refresh token to cache alongside access token
        """
        pass

    @abstractmethod
    def load(self, client_id: str) -> Optional[str]:
        """
        Load access token from cache.

        Args:
            client_id: Cache key (typically hash of client_id + scopes)

        Returns:
            Access token if found, None otherwise

        Note: This method is kept for backward compatibility. Use load_tokens()
              to retrieve both access and refresh tokens.
        """
        pass

    def load_tokens(self, client_id: str) -> tuple[Optional[str], Optional[str]]:
        """
        Load both access token and refresh token from cache.

        Args:
            client_id: Cache key (typically hash of client_id + scopes)

        Returns:
            Tuple of (access_token, refresh_token). Either or both may be None.
        """
        # Default implementation for backward compatibility
        # Subclasses should override if they support refresh tokens
        access_token = self.load(client_id)
        return (access_token, None)


class MemoryCache(AbstractCache):
    _items = {}

    def save(self, client_id: str, value: str, refresh_token: Optional[str] = None):
        self._items[client_id] = {
            "access_token": value,
            "refresh_token": refresh_token,
        }

    def load(self, client_id: str) -> Optional[str]:
        item = self._items.get(client_id)
        if item is None:
            return None
        # Handle both old format (string) and new format (dict)
        if isinstance(item, str):
            return item
        return item.get("access_token")

    def load_tokens(self, client_id: str) -> tuple[Optional[str], Optional[str]]:
        item = self._items.get(client_id)
        if item is None:
            return (None, None)
        # Handle both old format (string) and new format (dict)
        if isinstance(item, str):
            return (item, None)
        return (item.get("access_token"), item.get("refresh_token"))


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

    def save(self, client_id: str, value: str, refresh_token: Optional[str] = None):
        parser = ConfigParser()
        parser.read(self.cache_file)

        try:
            parser.add_section(client_id)
        except DuplicateSectionError:
            pass
        parser[client_id]["access_token"] = value
        if refresh_token:
            parser[client_id]["refresh_token"] = refresh_token
        elif "refresh_token" in parser[client_id]:
            # Remove refresh_token if None is explicitly passed
            del parser[client_id]["refresh_token"]

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

    def load_tokens(self, client_id: str) -> tuple[Optional[str], Optional[str]]:
        try:
            parser = ConfigParser()
            parser.read(self.cache_file)

            access_token = parser[client_id].get("access_token")
            refresh_token = parser[client_id].get("refresh_token")
            return (access_token, refresh_token)
        except (FileNotFoundError, KeyError):
            return (None, None)
