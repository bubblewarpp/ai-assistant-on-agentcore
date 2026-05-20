"""Agent profile CRUD service.

Profiles are user-owned harness presets layered on top of the existing Sparky
runtime. They do not replace the default generic persona.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from config import AGENT_PROFILES_TABLE, REGION
from utils import logger
from decimal import Decimal

def _json_safe(value):
    """Convert DynamoDB Decimal values into JSON-safe Python primitives."""
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    return value




DEFAULT_MEMORY_POLICY = "project"
VALID_MEMORY_POLICIES = {"off", "project", "global", "both"}


class AgentProfileService:
    def __init__(self, table_name: Optional[str] = None, region: Optional[str] = None):
        self.table_name = table_name or AGENT_PROFILES_TABLE
        self.region = region or REGION
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name) if self.table_name else None

    def _require_table(self) -> None:
        if not self.table:
            raise RuntimeError("AGENT_PROFILES_TABLE is not configured")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def normalize_profile(data: dict[str, Any]) -> dict[str, Any]:
        memory_policy = data.get("memory_policy") or DEFAULT_MEMORY_POLICY
        if memory_policy not in VALID_MEMORY_POLICIES:
            raise ValueError("memory_policy must be one of off, project, global, both")

        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        if len(name) > 80:
            raise ValueError("name must be 80 characters or fewer")

        system_prompt = (data.get("system_prompt") or "").strip()
        if len(system_prompt) > 12000:
            raise ValueError("system_prompt must be 12000 characters or fewer")

        enabled_tools = data.get("enabled_tools") or []
        if not isinstance(enabled_tools, list):
            raise ValueError("enabled_tools must be a list")

        budget_level = data.get("budget_level")
        if budget_level is not None:
            budget_level = int(budget_level)
            if budget_level < 0 or budget_level > 4:
                raise ValueError("budget_level must be between 0 and 4")

        persona = (data.get("persona") or "generic").strip() or "generic"

        return {
            "name": name,
            "system_prompt": system_prompt,
            "default_model_id": (data.get("default_model_id") or "").strip() or None,
            "budget_level": budget_level,
            "memory_policy": memory_policy,
            "enabled_tools": [str(t) for t in enabled_tools if str(t).strip()],
            "persona": persona,
        }

    async def list_profiles(self, user_id: str) -> list[dict[str, Any]]:
        self._require_table()
        try:
            response = self.table.query(
                KeyConditionExpression="user_id = :uid",
                ExpressionAttributeValues={":uid": user_id},
            )
            profiles = response.get("Items", [])
            return sorted(profiles, key=lambda p: p.get("updated_at", ""), reverse=True)
        except ClientError as e:
            logger.error(f"Failed to list agent profiles: {e}")
            raise

    async def get_profile(
        self, user_id: str, profile_id: str
    ) -> Optional[dict[str, Any]]:
        self._require_table()
        if not profile_id:
            return None
        response = self.table.get_item(Key={"user_id": user_id, "profile_id": profile_id})
        return response.get("Item")

    async def create_profile(
        self, user_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        self._require_table()
        now = self._now()
        profile = {
            "user_id": user_id,
            "profile_id": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            **self.normalize_profile(data),
        }
        self.table.put_item(Item=profile)
        return profile

    async def update_profile(
        self, user_id: str, profile_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        self._require_table()
        existing = await self.get_profile(user_id, profile_id)
        if not existing:
            return None
        merged = {**existing, **data}
        normalized = self.normalize_profile(merged)
        updated = {
            **existing,
            **normalized,
            "updated_at": self._now(),
        }
        self.table.put_item(Item=updated)
        return updated

    async def delete_profile(self, user_id: str, profile_id: str) -> bool:
        self._require_table()
        try:
            self.table.delete_item(
                Key={"user_id": user_id, "profile_id": profile_id},
                ConditionExpression="attribute_exists(user_id) AND attribute_exists(profile_id)",
            )
            return True
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                return False
            raise


agent_profile_service = AgentProfileService()
