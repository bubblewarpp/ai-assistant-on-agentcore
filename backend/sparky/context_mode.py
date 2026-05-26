"""Runtime context mode controls for Sparky.

Modes:
- new: New Context. Do not use saved user memory.
- saved: Saved Context. Use saved memory and continue learning.

This is intentionally in-memory per runtime process so it does not require
Terraform changes. The frontend sends memory_mode on each chat request.
"""

from __future__ import annotations

from utils import logger

_SESSION_CONTEXT_MODES: dict[str, str] = {}


def normalize_context_mode(value) -> str:
    mode = str(value or "saved").strip().lower()
    if mode in {"new", "new_context", "clean", "fresh", "off", "none"}:
        return "new"
    return "saved"


def set_session_context_mode(session_id: str, mode) -> str:
    normalized = normalize_context_mode(mode)
    if session_id:
        _SESSION_CONTEXT_MODES[session_id] = normalized
        logger.info(
            "CONTEXT_MODE_SET session=%s mode=%s",
            session_id,
            normalized,
        )
    return normalized


def get_session_context_mode(session_id: str) -> str:
    if not session_id:
        return "saved"
    return _SESSION_CONTEXT_MODES.get(session_id, "saved")


def should_use_saved_context(session_id: str) -> bool:
    return get_session_context_mode(session_id) == "saved"


def clear_session_context_mode(session_id: str) -> None:
    if session_id:
        _SESSION_CONTEXT_MODES.pop(session_id, None)
