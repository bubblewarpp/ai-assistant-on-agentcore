#!/usr/bin/env python3
"""
Create OpenSearch Serverless index for Bedrock Knowledge Base.
Reads REGION and COLLECTION_ENDPOINT from environment variables.
"""
import os
import sys
import time

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def main():
    region = os.environ.get("REGION")
    endpoint = os.environ.get("COLLECTION_ENDPOINT")

    if not region or not endpoint:
        print("ERROR: REGION and COLLECTION_ENDPOINT environment variables are required", file=sys.stderr)
        sys.exit(1)

    service = "aoss"
    index_name = "bedrock-knowledge-base-default-index"

    print(f"Waiting 90s for OpenSearch Serverless collection to be active...")
    time.sleep(90)

    # Get credentials
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token,
    )

    # Create OpenSearch client
    host = endpoint.replace("https://", "")
    client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=60,
    )

    # Index mapping for Bedrock KB
    index_body = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "bedrock-knowledge-base-default-vector": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "engine": "faiss",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {},
                    },
                },
                "AMAZON_BEDROCK_TEXT_CHUNK": {"type": "text"},
                "AMAZON_BEDROCK_METADATA": {"type": "text", "index": False},
            }
        },
    }

    # Create index with retries
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if client.indices.exists(index=index_name):
                print(f"Index '{index_name}' already exists")
                break
            response = client.indices.create(index=index_name, body=index_body)
            print(f"Index created: {response}")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(30)
            else:
                raise


if __name__ == "__main__":
    main()
