# System Skills Provisioning
# Syncs system-skills/ directory to S3 /system/ partition and upserts DynamoDB metadata.
# When system-skills/ folder is absent, fileset returns empty — no resources created.

locals {
  system_skills_path = "${path.module}/../system-skills"

  # Exclude hidden files/directories (e.g. .DS_Store) from the fileset
  system_skills_files = toset([
    for f in fileset(local.system_skills_path, "**/*") : f
    if !anytrue([for part in split("/", f) : startswith(part, ".")])
  ])

  # Extract unique top-level directory names (skill names) from the fileset
  system_skill_names = toset(distinct([
    for f in local.system_skills_files : split("/", f)[0]
  ]))

  # Read name and description from SKILL.md frontmatter for each skill
  # Note: description parsing is handled by scripts/upsert_skill.py at apply time
  # to correctly handle multi-line YAML block scalars
  system_skill_metadata = {
    for dir in local.system_skill_names : dir => {
      name = try(
        trimspace(replace(
          regex("(?m)^name:.+$", file("${local.system_skills_path}/${dir}/SKILL.md")),
          "name:", ""
        )),
        dir
      )
    }
  }
}

# Sync system-skills/ directory to S3 /system/ partition
resource "aws_s3_object" "system_skills" {
  for_each = local.system_skills_files

  bucket = aws_s3_bucket.skills_bucket.id
  key    = "system/${each.value}"
  source = "${local.system_skills_path}/${each.value}"
  etag   = filemd5("${local.system_skills_path}/${each.value}")
}

# Upsert DynamoDB metadata records for each system skill
resource "null_resource" "system_skill_metadata" {
  for_each = local.system_skill_names

  triggers = {
    table_name    = aws_dynamodb_table.skills.name
    region        = local.aws_region
    # Re-run when SKILL.md changes
    skill_md_hash = fileexists("${local.system_skills_path}/${each.value}/SKILL.md") ? filemd5("${local.system_skills_path}/${each.value}/SKILL.md") : "none"
  }

  provisioner "local-exec" {
    command = "python3 ${path.module}/scripts/upsert_skill.py"
    environment = {
      SKILL_DIR  = "${local.system_skills_path}/${each.value}"
      TABLE_NAME = aws_dynamodb_table.skills.name
      REGION     = local.aws_region
    }
  }
}
