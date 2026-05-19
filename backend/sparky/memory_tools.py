"""Explicit user memory tools for Sparky."""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Literal

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from project_memory_tool import composite_actor_id
from utils import logger


def _config_value(config: RunnableConfig, key: str) -> str:
    configurable = config.get("configurable", {}) if config else {}
    return configurable.get(key, "") or ""


def _safe_text(value: str, max_len: int = 5000) -> str:
    return (value or "").strip()[:max_len]


async def create_memory_event(
    *,
    actor_id: str,
    session_id: str,
    text: str,
    role: Literal["USER", "ASSISTANT", "OTHER"] = "USER",
    metadata: dict[str, str] | None = None,
) -> None:
    """Write a conversational event to AgentCore Memory."""
    from config import memory_store

    if not memory_store:
        raise RuntimeError("Project memory is not configured")
    if not actor_id or not session_id:
        raise ValueError("actor_id and session_id are required")

    meta = {
        key: {"stringValue": str(value)}
        for key, value in (metadata or {}).items()
        if value is not None
    }
    await asyncio.to_thread(
        memory_store.client.create_event,
        memoryId=memory_store.memory_id,
        actorId=actor_id,
        sessionId=session_id,
        eventTimestamp=datetime.now(timezone.utc),
        payload=[
            {
                "conversational": {
                    "content": {"text": text},
                    "role": role,
                }
            }
        ],
        clientToken=str(uuid.uuid4()),
        metadata=meta,
    )


@tool
async def remember_memory(
    content: str,
    config: RunnableConfig,
    scope: Literal["auto", "global", "project"] = "auto",
    kind: Literal["fact", "preference", "decision", "task", "note"] = "fact",
    project_id: str = "",
    user_id: str = "",
    session_id: str = "",
) -> str:
    """Remember a durable fact, preference, decision, task, or note.

    Use this only when the user explicitly asks to remember/save something, or
    when the information is clearly a durable project decision.
    """
    user_id = user_id or _config_value(config, "actor_id") or _config_value(config, "user_id")
    session_id = session_id or _config_value(config, "thread_id") or str(uuid.uuid4())
    project_id = project_id or _config_value(config, "project_id")

    text = _safe_text(content)
    if not text:
        return json.dumps({"error": "content is required"})

    chosen_scope = scope
    if chosen_scope == "auto":
        chosen_scope = "project" if project_id else "global"

    if chosen_scope == "project" and not project_id:
        chosen_scope = "global"

    actor_id = (
        composite_actor_id(user_id, project_id)
        if chosen_scope == "project"
        else user_id
    )
    memory_text = f"Remembered {kind} ({chosen_scope}): {text}"

    try:
        await create_memory_event(
            actor_id=actor_id,
            session_id=session_id,
            text=memory_text,
            role="USER",
            metadata={"kind": kind, "scope": chosen_scope},
        )
    except Exception as e:
        logger.error(f"remember_memory failed: {e}")
        return json.dumps({"error": "Failed to store memory."})

    return json.dumps(
        {
            "status": "remembered",
            "scope": chosen_scope,
            "kind": kind,
            "message": "Memory stored. It may take a few minutes to appear in recall.",
        }
    )


@tool
async def recall_user_memory(
    query: str,
    config: RunnableConfig,
    kind: Literal["facts", "preferences", "both"] = "both",
    relevance: Literal["low", "medium", "high"] = "medium",
    limit: int = 10,
    user_id: str = "",
) -> str:
    """Recall global user memories across projects.

    Use this for user preferences, working style, and durable facts that should
    follow the user across projects.
    """
    from config import memory_store

    if not memory_store:
        return json.dumps({"memories": [], "message": "Memory is not configured."})
    user_id = user_id or _config_value(config, "actor_id") or _config_value(config, "user_id")
    if not user_id:
        return json.dumps({"memories": [], "message": "No user context available."})
    query = _safe_text(query, 1000)
    if not query:
        return json.dumps({"error": "query is required."})

    thresholds = {"low": 0.25, "medium": 0.5, "high": 0.8}
    min_score = thresholds.get(relevance, thresholds["medium"])
    namespaces = []
    if kind in ("facts", "both"):
        namespaces.append(f"users/{user_id}/facts")
    if kind in ("preferences", "both"):
        namespaces.append(f"users/{user_id}/preferences")

    async def _search(namespace: str) -> list[dict]:
        try:
            response = await asyncio.to_thread(
                memory_store.client.retrieve_memory_records,
                memoryId=memory_store.memory_id,
                namespace=namespace,
                searchCriteria={"searchQuery": query, "topK": limit},
                maxResults=limit,
            )
        except Exception as e:
            logger.warning(f"User memory search failed for {namespace}: {e}")
            return []

        records = []
        for r in response.get("memoryRecordSummaries", []):
            score = r.get("score") or 0
            content = r.get("content", {})
            text = content.get("text", "") if isinstance(content, dict) else str(content)
            if text and score >= min_score:
                records.append(
                    {"content": text, "score": score, "namespace": namespace}
                )
        return records

    results_nested = await asyncio.gather(*[_search(ns) for ns in namespaces])
    results = [item for group in results_nested for item in group]
    results.sort(key=lambda item: item.get("score") or 0, reverse=True)
    return json.dumps({"memories": results[:limit]})
