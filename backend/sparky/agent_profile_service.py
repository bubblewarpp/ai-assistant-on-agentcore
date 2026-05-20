"""Read-only agent profile access for the Sparky runtime."""

from __future__ import annotations

import os
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from utils import logger
from decimal import Decimal

REGION = os.environ.get("REGION", "us-east-1")
AGENT_PROFILES_TABLE = os.environ.get("AGENT_PROFILES_TABLE")



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


class AgentProfileService:
    def __init__(self, table_name: Optional[str] = None, region: Optional[str] = None):
        self.table_name = table_name or AGENT_PROFILES_TABLE
        self.region = region or REGION
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name) if self.table_name else None

    async def get_profile(
        self, user_id: str, profile_id: str
    ) -> Optional[dict[str, Any]]:
        if not self.table or not profile_id:
            return None
        try:
            response = self.table.get_item(
                Key={"user_id": user_id, "profile_id": profile_id}
            )
            return _json_safe(response.get("Item"))
        except ClientError as e:
            logger.warning(f"Failed to load agent profile {profile_id}: {e}")
            return None


agent_profile_service = AgentProfileService()
