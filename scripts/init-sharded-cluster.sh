#!/usr/bin/env bash
set -euo pipefail
COMPOSE=${COMPOSE_FILE:-docker-compose.sharded.yml}
wait_for() { for i in {1..40}; do docker compose -f "$COMPOSE" exec -T "$1" mongosh --quiet --eval 'db.adminCommand({ping:1})' >/dev/null 2>&1 && return 0 || sleep 2; done; return 1; }
for c in cfg1 shard1a mongos; do wait_for "$c"; done
docker compose -f "$COMPOSE" exec -T cfg1 mongosh --quiet --eval 'try { rs.status() } catch(e) { rs.initiate({_id:"csrs",configsvr:true,members:[{_id:0,host:"cfg1:27017"},{_id:1,host:"cfg2:27017"},{_id:2,host:"cfg3:27017"}]}) }'
docker compose -f "$COMPOSE" exec -T shard1a mongosh --quiet --eval 'try { rs.status() } catch(e) { rs.initiate({_id:"shardrs",members:[{_id:0,host:"shard1a:27017"},{_id:1,host:"shard1b:27017"},{_id:2,host:"shard1c:27017"}]}) }'
sleep 8
docker compose -f "$COMPOSE" exec -T mongos mongosh --quiet --eval 'try { sh.addShard("shardrs/shard1a:27017,shard1b:27017,shard1c:27017") } catch(e) {} ; sh.enableSharding("geosense"); db.getSiblingDB("geosense").incidents.createIndex({incidentId:"hashed"}); try { sh.shardCollection("geosense.incidents", {incidentId:"hashed"}) } catch(e) {}'
echo "Sharded cluster initialized"
