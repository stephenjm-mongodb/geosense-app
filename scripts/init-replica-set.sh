#!/usr/bin/env bash
set -euo pipefail
COMPOSE=${COMPOSE_FILE:-docker-compose.replica.yml}
for i in {1..30}; do docker compose -f "$COMPOSE" exec -T mongo1 mongosh --quiet --eval 'db.adminCommand({ping:1})' >/dev/null 2>&1 && break || sleep 2; done
docker compose -f "$COMPOSE" exec -T mongo1 mongosh --quiet --eval 'try { rs.status() } catch (e) { rs.initiate({_id:"rs0",members:[{_id:0,host:"mongo1:27017"},{_id:1,host:"mongo2:27017"},{_id:2,host:"mongo3:27017"}]}) }'
echo "Replica set initialized"
