import os, sys, time, random
from datetime import datetime, timezone
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
mode = sys.argv[1] if len(sys.argv) > 1 else "mixed"; seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 30
end = time.time() + seconds; count = 0
while time.time() < end:
    if mode in ("dispatch", "mixed"):
        db.incidents.find_one({"status": "open"}); db.agents.find_one({"available": True}); count += 2
    if mode in ("telemetry", "mixed"):
        db.sensorReadings.insert_one({"sensorId": "S-001", "timestamp": datetime.now(timezone.utc), "metric": "temperature", "value": random.random()*30}); count += 1
    if mode in ("analytics", "mixed"):
        list(db.incidents.aggregate([{"$group": {"_id": "$category", "count": {"$sum": 1}}} ])); count += 1
    if mode == "search":
        list(db.knowledgeDocuments.find({"$or": [{"title": {"$regex": "water", "$options": "i"}}, {"body": {"$regex": "water", "$options": "i"}}]})); count += 1
print("operations", count, "in", seconds, "seconds")
