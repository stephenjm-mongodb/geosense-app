# GeoSense MongoDB Learning App

GeoSense is a small field-intelligence application for experimenting with MongoDB geospatial queries, time-series collections, aggregation, change streams, replica sets, sharding, Atlas Search, and Vector Search.

## Deployment modes

* `local`: standalone MongoDB; easiest starting point.
* `replica`: three-node replica set; enables change streams and transactions.
* `sharded`: three config servers, a three-node shard replica set, and `mongos`.
* Atlas Search and Vector Search require MongoDB Atlas. Local mode uses regex and Python cosine-similarity fallbacks.

## Prerequisites

* Docker and Docker Compose v2
* Python 3.11+ if running scripts outside Docker
* `mongosh` is optional; the scripts use the Python driver

## Start locally

```bash
./scripts/start-local.sh
./scripts/seed.sh local
./scripts/index.sh local
curl http://localhost:8000/health
```

API docs: http://localhost:8000/docs

Run experiments:

```bash
./scripts/explain.sh local
./scripts/telemetry.sh local 30
./scripts/workload.sh local mixed 30
```

Stop and delete local data:

```bash
./scripts/stop.sh local
```

## Start a replica set

```bash
./scripts/start-replica.sh
./scripts/seed.sh replica
./scripts/index.sh replica
./scripts/workload.sh replica dispatch 30
```

The replica-set URI is:

```text
mongodb://mongo1:27017,mongo2:27017,mongo3:27017/geosense?replicaSet=rs0
```

Use this mode for change streams, transactions, failover, and majority write concern experiments.

## Start a sharded cluster

```bash
./scripts/start-sharded.sh
./scripts/seed.sh sharded
./scripts/index.sh sharded
./scripts/explain.sh sharded
```

The application connects through `mongos` at `mongodb://localhost:27017` and the cluster is configured with one sharded database and a hashed `incidents.incidentId` shard key. This topology is for learning, not production.

## Atlas Search and Vector Search

Set `MONGODB_URI` to an Atlas connection string and set `GEOSENSE_ATLAS_SEARCH=true`. Then run:

```bash
python scripts/create_search_indexes.py
python scripts/generate_embeddings.py
```

The app attempts Atlas Search and Vector Search first when enabled. If unavailable, lexical search falls back to a regex query and semantic search falls back to local cosine similarity over stored vectors.

## API highlights

```text
GET  /health
GET  /agents/nearby?longitude=-6.26&latitude=53.35&max_distance_m=5000
POST /incidents
POST /incidents/{incident_id}/assign
POST /sensors/{sensor_id}/readings
GET  /sensors/{sensor_id}/trend
GET  /search/lexical?q=water
GET  /search/semantic?q=water leak near school
GET  /search/hybrid?q=water leak
GET  /reports/response-time
```

## Learning sequence

1. Run local mode and inspect CRUD, indexes, and `explain("executionStats")`.
2. Create and query the time-series collection.
3. Compare geospatial queries with and without indexes.
4. Run the replica set; inspect `rs.status()`, change streams, transactions, and failover.
5. Run the sharded cluster; compare targeted and scatter-gather queries.
6. Use Atlas for Lucene Search and Vector Search.
7. Run the mixed workload and compare OLTP latency during reporting queries.

## Safety

This is a disposable local learning environment. Do not expose MongoDB ports publicly and do not use production credentials or data.
