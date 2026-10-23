#!/usr/bin/env bash
set -euo pipefail
docker compose -f docker-compose.replica.yml down -v
