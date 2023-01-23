from configparser import ConfigParser
from pathlib import Path

from pyfakefs.fake_filesystem import FakeFilesystem

from .cache import AppDirCache, MemoryCache

TEST_DIR = Path("/test")


def test_empty_cache_save(fs: FakeFilesystem):
    fs.makedir(TEST_DIR)
    cache = AppDirCache(TEST_DIR)
    parser = ConfigParser()

    cache.save("test-client", "test-access")

    parser.read(TEST_DIR / "tokencache")
    assert {key: value for key, value in parser.items("test-client")} == {
        "access_token": "test-access",
    }


def test_empty_cache_load(fs: FakeFilesystem):
    fs.makedir(TEST_DIR)
    cache = AppDirCache(TEST_DIR)

    assert cache.load("test-client") is None


def test_partial_cache_save(fs: FakeFilesystem):
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


def test_cache_update(fs: FakeFilesystem):
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


def test_memory_cache_empty():
    cache = MemoryCache()

    assert cache.load("test-client") is None


def test_memory_cache():
    cache = MemoryCache()
    cache.save("test-client", "bar")

    assert cache.load("test-client") == "bar"
