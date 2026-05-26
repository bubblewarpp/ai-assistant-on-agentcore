"""Global user context loader from AgentCore Memory.

Loads saved user facts and preferences for Saved Context mode.

Modes:
- New Context: skip saved memory.
- Saved Context: load saved user memory from AgentCore.
"""

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


async def _retrieve_namespace(memory_store, namespace: str, query: str, limit: int) -> list[str]:
    try:
        response = await asyncio.to_thread(
            memory_store.client.retrieve_memory_records,
            memoryId=memory_store.memory_id,
            namespace=namespace,
            searchCriteria={
                "searchQuery": query,
                "topK": limit,
            },
            maxResults=limit,
        )
    except Exception as e:
        logger.warning(f"Global user memory fetch failed for {namespace}: {e}")
        return []

    lines: list[str] = []

    for record in response.get("memoryRecordSummaries", []):
        content = record.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        text = (text or "").strip()

        if text:
            lines.append(text)

    return lines


async def get_user_preferences(user_id: str, session_id: str | None = None) -> str:
    """Return saved user memory text for prompt injection.

    Kept as get_user_preferences() to avoid changing existing callers, but it now
    loads both preferences and facts because remember_memory may store durable
    user instructions in either namespace depending on kind/strategy extraction.
    """
    if session_id:
        try:
            from context_mode import should_use_saved_context, get_session_context_mode

            mode = get_session_context_mode(session_id)

            if not should_use_saved_context(session_id):
                logger.info(
                    "CONTEXT_MODE_SKIP_PREFERENCES session=%s mode=%s",
                    session_id,
                    mode,
                )
                return ""

            logger.info(
                "CONTEXT_MODE_USE_PREFERENCES session=%s mode=%s",
                session_id,
                mode,
            )
        except Exception as e:
            logger.warning(
                "Context mode check failed, using saved context by default: %s",
                e,
            )

    from config import memory_store

    if not memory_store or not user_id:
        return ""

    cache_key = f"{user_id}:saved_context"
    now = time.monotonic()

    cached = _cache.get(cache_key)
    if cached and cached.expires_at > now:
        logger.info(
            "USER_PREFERENCES_CACHE_HIT user=%s session=%s has_text=%s",
            user_id,
            session_id,
            bool(cached.text.strip()),
        )
        return cached.text

    query = (
        "user preferences facts working style communication style "
        "technical conventions coding style tone AWS MCP aws-knowledge-mcp "
        "preferred tools deployment preferences"
    )

    namespaces = [
        f"users/{user_id}/preferences",
        f"users/{user_id}/facts",
    ]

    results_nested = await asyncio.gather(
        *[_retrieve_namespace(memory_store, namespace, query, _TOP_K) for namespace in namespaces]
    )

    seen: set[str] = set()
    lines: list[str] = []

    for group in results_nested:
        for text in group:
            normalized = " ".join(text.split())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            lines.append(f"- {normalized}")

    result = "\n".join(lines)

    # Do not cache empty result. If user saves memory immediately after an empty
    # recall, empty caching makes Saved Context look broken until TTL expires.
    if result.strip():
        _cache[cache_key] = _PreferenceEntry(text=result, expires_at=now + _CACHE_TTL)
    else:
        _cache.pop(cache_key, None)

    logger.info(
        "USER_PREFERENCES_RESULT user=%s session=%s namespaces=%s count=%s has_text=%s",
        user_id,
        session_id,
        ",".join(namespaces),
        len(lines),
        bool(result.strip()),
    )

    return result
