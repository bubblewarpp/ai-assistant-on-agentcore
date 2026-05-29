#!/usr/bin/env bash
# Docker build and push script for AgentCore runtimes
# Usage: bash docker_build_push.sh <region> <ecr_repo_url> <image_tag> <working_dir>
set -e

REGION="$1"
ECR_REPO="$2"
IMAGE_TAG="$3"
WORKING_DIR="$4"

cd "$WORKING_DIR"

echo "Logging into ECR public..."
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

echo "Logging into ECR private ($REGION)..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_REPO"

echo "Setting up buildx..."
docker buildx create --use --name multiarch 2>/dev/null || docker buildx use multiarch

echo "Building and pushing image: $ECR_REPO:$IMAGE_TAG"
docker buildx build \
  --platform linux/arm64 \
  --build-arg AWS_REGION="$REGION" \
  -t "$ECR_REPO:$IMAGE_TAG" \
  -t "$ECR_REPO:latest" \
  --push \
  .

echo "Done: $ECR_REPO:$IMAGE_TAG"
