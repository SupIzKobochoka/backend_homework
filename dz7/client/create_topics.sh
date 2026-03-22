#!/usr/bin/env bash
set -e

docker compose exec -T redpanda rpk topic create moderation --brokers redpanda:9092 || true
docker compose exec -T redpanda rpk topic create moderation.dlq --brokers redpanda:9092 || true

echo "Topics created: moderation, moderation.dlq"