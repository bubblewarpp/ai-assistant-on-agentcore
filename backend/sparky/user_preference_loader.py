"""Global user preference loader from AgentCore Memory."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from utils import logger

_CACHE_TTL = 15 * 60
_TOP_K = 20


@dataclass
class _PreferenceEntry:
    text: str
    expires_at: float


_cache: dict[str, _PreferenceEntry] = {}


async def get_user_preferences(user_id: str) -> str:
    from config import memory_store

    if not memory_store or not user_id:
        return ""

    now = time.monotonic()
    cached = _cache.get(user_id)
    if cached and cached.expires_at > now:
        return cached.text

    try:
        response = await asyncio.to_thread(
            memory_store.client.retrieve_memory_records,
            memoryId=memory_store.memory_id,
            namespace=f"users/{user_id}/preferences",
            searchCriteria={
                "searchQuery": (
                    "user preferences working style communication style "
                    "technical conventions coding style tone"
                ),
                "topK": _TOP_K,
            },
            maxResults=_TOP_K,
        )
    except Exception as e:
        logger.warning(f"Global user preferences fetch failed: {e}")
        return ""

    lines = []
    for r in response.get("memoryRecordSummaries", []):
        content = r.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        if text:
            lines.append(f"- {text}")
    result = "\n".join(lines)
    _cache[user_id] = _PreferenceEntry(text=result, expires_at=now + _CACHE_TTL)
    return result
