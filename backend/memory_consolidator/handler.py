"""Nightly memory consolidator.

Runs as a system Lambda on a daily schedule. It scans chat sessions from the
previous local day, asks Bedrock for durable recap bullets, and writes those
bullets back to AgentCore Memory as global or project-scoped events.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from datetime import datetime, time as dt_time, timedelta, timezone
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.config import Config

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

REGION = os.environ.get("REGION", os.environ.get("AWS_REGION", "us-east-1"))
CHAT_HISTORY_TABLE = os.environ.get("CHAT_HISTORY_TABLE")
PROJECT_MEMORY_ID = os.environ.get("PROJECT_MEMORY_ID")
MODEL_ID = os.environ.get("MODEL_ID")
TIMEZONE = os.environ.get("MEMORY_RECAP_TIMEZONE", "Asia/Jakarta")
MAX_SESSIONS = int(os.environ.get("MEMORY_RECAP_MAX_SESSIONS", "200"))

dynamodb = boto3.resource("dynamodb", region_name=REGION)
chat_table = dynamodb.Table(CHAT_HISTORY_TABLE) if CHAT_HISTORY_TABLE else None
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
agentcore = boto3.client(
    "bedrock-agentcore",
    region_name=REGION,
    config=Config(retries={"max_attempts": 8, "mode": "adaptive"}),
)


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return str(value)


def _window() -> tuple[str, str, str]:
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    target_date = (now - timedelta(days=1)).date()
    start = datetime.combine(target_date, dt_time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(target_date, dt_time.max, tzinfo=tz).astimezone(timezone.utc)
    return start.isoformat(), end.isoformat(), target_date.isoformat()


def _scan_sessions(start_iso: str, end_iso: str) -> list[dict[str, Any]]:
    if not chat_table:
        raise RuntimeError("CHAT_HISTORY_TABLE is not configured")

    sessions: list[dict[str, Any]] = []
    scan_kwargs = {
        "FilterExpression": Attr("created_at").between(start_iso, end_iso),
        "Limit": min(MAX_SESSIONS, 100),
    }
    while True:
        response = chat_table.scan(**scan_kwargs)
        sessions.extend(response.get("Items", []))
        if len(sessions) >= MAX_SESSIONS:
            return sessions[:MAX_SESSIONS]
        next_key = response.get("LastEvaluatedKey")
        if not next_key:
            return sessions
        scan_kwargs["ExclusiveStartKey"] = next_key


def _group_sessions(sessions: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for session in sessions:
        user_id = session.get("user_id")
        if not user_id:
            continue
        project_id = session.get("project_id") or ""
        grouped.setdefault((user_id, project_id), []).append(session)
    return grouped


def _summarize(user_id: str, project_id: str, day: str, sessions: list[dict]) -> str:
    payload = [
        {
            "session_id": s.get("session_id"),
            "created_at": s.get("created_at"),
            "description": s.get("description"),
            "project_id": s.get("project_id"),
        }
        for s in sessions
    ]
    scope = "project" if project_id else "global"
    prompt = f"""
Create durable memory recap bullets for this user's {scope} assistant activity on {day}.

Keep only durable facts, decisions, preferences, blockers, and next actions.
Do not include passwords, API keys, tokens, credentials, sensitive personal data,
casual chatter, greetings, or generic activity logs.

Return 1-8 concise bullets. If nothing durable exists, return exactly: NO_MEMORY

Sessions:
{json.dumps(payload, default=_json_default)}
""".strip()

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 900, "temperature": 0},
    )
    content = response.get("output", {}).get("message", {}).get("content", [])
    return content[0].get("text", "").strip() if content else ""


def _actor_id(user_id: str, project_id: str) -> str:
    if not project_id:
        return user_id
    return f"{user_id.replace('-', '')}_{project_id.replace('-', '')}"


def _write_memory(user_id: str, project_id: str, day: str, summary: str) -> None:
    if not PROJECT_MEMORY_ID:
        raise RuntimeError("PROJECT_MEMORY_ID is not configured")
    session_id = f"nightly-recap-{day}-{project_id or 'global'}"
    scope = "project" if project_id else "global"
    agentcore.create_event(
        memoryId=PROJECT_MEMORY_ID,
        actorId=_actor_id(user_id, project_id),
        sessionId=session_id,
        eventTimestamp=datetime.now(timezone.utc),
        payload=[
            {
                "conversational": {
                    "content": {"text": f"Nightly {scope} memory recap for {day}:\n{summary}"},
                    "role": "ASSISTANT",
                }
            }
        ],
        clientToken=str(uuid.uuid4()),
        metadata={"scope": {"stringValue": scope}, "kind": {"stringValue": "recap"}},
    )


def handler(event, context):
    start_iso, end_iso, day = _window()
    logger.info("Running memory recap for %s (%s - %s)", day, start_iso, end_iso)
    sessions = _scan_sessions(start_iso, end_iso)
    grouped = _group_sessions(sessions)
    written = 0
    skipped = 0
    failures = 0

    for (user_id, project_id), group in grouped.items():
        try:
            summary = _summarize(user_id, project_id, day, group)
            if not summary or summary.strip().upper() == "NO_MEMORY":
                skipped += 1
                continue
            _write_memory(user_id, project_id, day, summary)
            written += 1
            time.sleep(0.2)
        except Exception as e:
            failures += 1
            logger.error("Failed recap for user=%s project=%s: %s", user_id, project_id, e)

    result = {
        "day": day,
        "sessions_scanned": len(sessions),
        "groups": len(grouped),
        "written": written,
        "skipped": skipped,
        "failures": failures,
    }
    logger.info("Memory recap result: %s", json.dumps(result))
    return result
