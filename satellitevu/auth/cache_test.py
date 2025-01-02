from allure import story, title
from configparser import ConfigParser
from pathlib import Path

from pyfakefs.fake_filesystem import FakeFilesystem

from .cache import AppDirCache, MemoryCache

TEST_DIR = Path("/test")


@story("Cache")
class TestCache:
    @title("Empty cache save")
    def test_empty_cache_save(self, fs: FakeFilesystem):
        fs.makedir(TEST_DIR)
        cache = AppDirCache(TEST_DIR)
        parser = ConfigParser()

        cache.save("test-client", "test-access")

        parser.read(TEST_DIR / "tokencache")
        assert {key: value for key, value in parser.items("test-client")} == {
            "access_token": "test-access",
        }

    @title("Empty cache load")
    def test_empty_cache_load(self, fs: FakeFilesystem):
        fs.makedir(TEST_DIR)
        cache = AppDirCache(TEST_DIR)

        assert cache.load("test-client") is None

    @title("Partial cache save")
    def test_partial_cache_save(self, fs: FakeFilesystem):
        fs.makedir(TEST_DIR)
        cache = AppDirCache(TEST_DIR)
        cache_file = TEST_DIR / "tokencache"

        parser = ConfigParser()
        parser.add_section("other-client")
        parser["other-client"]["access_token"] = "foo"
        with open(cache_file, "w") as handle:
            parser.write(handle)

        cache.save("test-client", "test-access")

        parser = ConfigParser()
        parser.read(cache_file)
        assert {key: value for key, value in parser.items("test-client")} == {
            "access_token": "test-access",
        }
        assert {key: value for key, value in parser.items("other-client")} == {
            "access_token": "foo",
        }

    @title("Cache update")
    def test_cache_update(self, fs: FakeFilesystem):
        fs.makedir(TEST_DIR)
        cache = AppDirCache(TEST_DIR)
        cache_file = TEST_DIR / "tokencache"

        parser = ConfigParser()
        parser.add_section("test-client")
        parser["test-client"]["access_token"] = "foo"
        with open(cache_file, "w") as handle:
            parser.write(handle)

        cache.save("test-client", "bar")

        parser = ConfigParser()
        parser.read(cache_file)
        assert {key: value for key, value in parser.items("test-client")} == {
            "access_token": "bar",
        }

    @title("Empty memory cache")
    def test_memory_cache_empty(self):
        cache = MemoryCache()

        assert cache.load("test-client") is None

    @title("Memory cache")
    def test_memory_cache(self):
        cache = MemoryCache()
        cache.save("test-client", "bar")

        assert cache.load("test-client") == "bar"
