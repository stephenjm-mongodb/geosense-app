#!/usr/bin/env bash
set -euo pipefail
docker compose -f docker-compose.sharded.yml up -d
COMPOSE_FILE=docker-compose.sharded.yml ./scripts/init-sharded-cluster.sh
