import asyncio
import logging
from typing import Any, Optional
import aiohttp
from aiohttp import ClientTimeout
from django.conf import settings

logger = logging.getLogger(__name__)

_SEMAPHORE = asyncio.Semaphore(int(getattr(settings, "EXTERNAL_API_CONCURRENCY", 10)))

class ExternalAPIError(Exception):
    pass

async def _fetch_once(session: aiohttp.ClientSession, url: str, **kwargs) -> dict[str, Any]:
    # Support settings.EXTERNAL_API_URL_TIMEOUT as defined in settings/base.py
    timeouts = getattr(settings, "EXTERNAL_API_URL_TIMEOUT", {"connect": 2.0, "read": 5.0})
    timeout = ClientTimeout(connect=timeouts.get("connect", 2.0), sock_read=timeouts.get("read", 5.0))
    async with session.get(url, timeout=timeout, **kwargs) as resp:
        text = await resp.text()
        if resp.status >= 500:
            raise ExternalAPIError(f"external server error {resp.status}")
        if resp.status >= 400:
            raise ExternalAPIError(f"client error {resp.status}: {text}")
        return await resp.json()

async def fetch_external(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> dict[str, Any]:
    """
    Fetch external endpoint with retries and backoff.
    Returns parsed JSON or raises ExternalAPIError on failure.
    """
    backoff = settings.EXTERNAL_API_BACKOFF
    retries = settings.EXTERNAL_API_RETRIES
    session = _get_session()
    async with _SEMAPHORE:
        attempt = 0
        while True:
            try:
                return await _fetch_once(session, url, params=params, headers=headers)
            except (aiohttp.ClientError, asyncio.TimeoutError, ExternalAPIError) as exc:
                attempt += 1
                if attempt > retries:
                    logger.exception("fetch_external failed after retries")
                    raise ExternalAPIError(str(exc)) from exc
                wait = backoff * (2 ** (attempt - 1))
                logger.warning("fetch_external attempt %d failed, backing off %.2fs: %s", attempt, wait, exc)
                await asyncio.sleep(wait)

_session: Optional[aiohttp.ClientSession] = None

def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        timeout = ClientTimeout(total=None)  
        _session = aiohttp.ClientSession(timeout=timeout)
    return _session

async def close_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None