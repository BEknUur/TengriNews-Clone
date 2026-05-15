from django.core.cache import caches
from django.utils.crypto import salted_hmac
from typing import Any

def _get_cache():
    """Lazily resolve the `article_cache` alias to avoid import-time access."""
    return caches["article_cache"]


def make_article_detail_key(article_id: int) -> str:
    return f"article:detail:{article_id}"


def get_list_version() -> int:
    """Return current article list version (0 if missing)."""
    try:
        raw_client = _get_cache().client.get_client(write=False)
        val = raw_client.get("article:list:version")
        if val is None:
            return 0
        # redis returns bytes in python redis client
        if isinstance(val, bytes):
            try:
                return int(val.decode())
            except Exception:
                return 0
        return int(val)
    except Exception:
        return 0


def make_article_list_key(params: dict[str, Any]) -> str:
    """Build stable list cache key including a version number."""
    key_src = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    short = salted_hmac("article_list", key_src).hexdigest()[:12]
    version = get_list_version()
    return f"article:list:v{version}:{short}"


def cache_set(key: str, value, ttl: int):
    _get_cache().set(key, value, ttl)


def cache_get(key: str):
    return _get_cache().get(key)


def cache_delete(key: str):
    _get_cache().delete(key)


def incr_list_version():
    # atomic increment for list versioning
    raw_client = _get_cache().client.get_client(write=True)
    return raw_client.incr("article:list:version")
from django.core.cache import caches
from django.utils.crypto import salted_hmac
from typing import Any

def _get_cache():
    """Lazily resolve the `article_cache` alias to avoid import-time access."""
    return caches["article_cache"]


def make_article_detail_key(article_id: int) -> str:
    return f"article:detail:{article_id}"


def get_list_version() -> int:
    """Return current article list version (0 if missing)."""
    try:
        raw_client = _get_cache().client.get_client(write=False)
        val = raw_client.get("article:list:version")
        if val is None:
            return 0
        # redis returns bytes in python redis client
        if isinstance(val, bytes):
            try:
                return int(val.decode())
            except Exception:
                return 0
        return int(val)
    except Exception:
        return 0


def make_article_list_key(params: dict[str, Any]) -> str:
    """Build stable list cache key including a version number."""
    key_src = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    short = salted_hmac("article_list", key_src).hexdigest()[:12]
    version = get_list_version()
    return f"article:list:v{version}:{short}"


def cache_set(key: str, value, ttl: int):
    _get_cache().set(key, value, ttl)


def cache_get(key: str):
    return _get_cache().get(key)


def cache_delete(key: str):
    _get_cache().delete(key)


def incr_list_version():
    # atomic increment for list versioning
    raw_client = _get_cache().client.get_client(write=True)
    return raw_client.incr("article:list:version")