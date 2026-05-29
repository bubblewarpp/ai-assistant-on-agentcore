#!/usr/bin/env python3
"""
Upsert a system skill metadata record into DynamoDB.
Reads SKILL_DIR, TABLE_NAME, REGION from environment variables.
"""
import sys
import os
import re
import json
import subprocess
from datetime import datetime, timezone


def parse_frontmatter(skill_md_path):
    """Parse YAML frontmatter from SKILL.md, returning name and description."""
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter block between --- delimiters
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None, None

    fm_text = fm_match.group(1)

    # Parse name (simple single-line value)
    name_match = re.search(r"^name:\s*(.+)$", fm_text, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else None

    # Parse description — handles both single-line and multi-line block scalar (|)
    desc_match = re.search(r"^description:\s*\|?\s*\n((?:[ \t]+.+\n?)+)", fm_text, re.MULTILINE)
    if desc_match:
        # Multi-line block scalar — strip leading whitespace from each line and join
        lines = desc_match.group(1).splitlines()
        description = " ".join(line.strip() for line in lines if line.strip())
    else:
        # Single-line description
        desc_inline = re.search(r"^description:\s*(.+)$", fm_text, re.MULTILINE)
        description = desc_inline.group(1).strip() if desc_inline else ""

    return name, description


def main():
    skill_dir = os.environ.get("SKILL_DIR")
    table_name = os.environ.get("TABLE_NAME")
    region = os.environ.get("REGION")

    if not skill_dir or not table_name or not region:
        print("ERROR: SKILL_DIR, TABLE_NAME, and REGION environment variables are required", file=sys.stderr)
        sys.exit(1)

    skill_name_from_dir = os.path.basename(skill_dir.rstrip("/\\"))
    skill_md_path = os.path.join(skill_dir, "SKILL.md")

    if os.path.exists(skill_md_path):
        name, description = parse_frontmatter(skill_md_path)
    else:
        name, description = None, ""

    skill_name = name if name else skill_name_from_dir
    description = description or ""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    item = {
        "user_id": {"S": "system"},
        "skill_name": {"S": skill_name},
        "description": {"S": description},
        "s3_content_path": {"S": f"system/{skill_name_from_dir}/"},
        "created_by": {"S": "system"},
        "visibility": {"S": "public"},
        "created_at": {"S": now},
        "updated_at": {"S": now},
    }

    cmd = [
        "aws", "dynamodb", "put-item",
        "--table-name", table_name,
        "--region", region,
        "--item", json.dumps(item),
    ]

    print(f"Upserting skill '{skill_name}' into table '{table_name}' ({region})")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    print(f"OK: skill '{skill_name}' upserted successfully")


if __name__ == "__main__":
    main()
