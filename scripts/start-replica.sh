#!/usr/bin/env bash
set -euo pipefail
docker compose -f docker-compose.replica.yml up -d
COMPOSE_FILE=docker-compose.replica.yml ./scripts/init-replica-set.sh
