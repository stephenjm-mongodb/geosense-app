import os, sys
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient, GEOSPHERE, ASCENDING

uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri, serverSelectionTimeoutMS=5000)[os.getenv("MONGODB_DATABASE", "geosense")]
try:
    db.create_collection("sensorReadings", timeseries={"timeField": "timestamp", "metaField": "sensorId", "granularity": "minutes"}, expireAfterSeconds=60*60*24*30)
except Exception:
    pass
now = datetime.now(timezone.utc)
db.agents.delete_many({}); db.facilities.delete_many({}); db.incidents.delete_many({}); db.knowledgeDocuments.delete_many({}); db.sensorReadings.delete_many({})
db.agents.insert_many([{"agentId": f"A-{i:03}", "name": f"Agent {i}", "skills": ["water", "air"] if i % 2 else ["power", "fire"], "available": True, "location": {"type": "Point", "coordinates": [-6.26 + i/1000, 53.35 + i/1000]}, "updatedAt": now} for i in range(1, 11)])
db.facilities.insert_many([{"facilityId": "F-001", "name": "Dublin Operations", "location": {"type": "Point", "coordinates": [-6.26, 53.35]}}, {"facilityId": "F-002", "name": "Cork Operations", "location": {"type": "Point", "coordinates": [-8.47, 51.90]}}])
for i in range(1, 21):
    db.incidents.insert_one({"incidentId": f"I-{i:04}", "title": "Water leak" if i % 2 else "Air quality alert", "description": "Sensor detected an environmental condition requiring field inspection", "category": "water" if i % 2 else "air", "severity": "high" if i % 5 == 0 else "medium", "status": "open", "location": {"type": "Point", "coordinates": [-6.26 + i/10000, 53.35 + i/10000]}, "createdAt": now - timedelta(hours=i)})
docs = [{"title": "Water leak response", "body": "Inspect valves, isolate the affected area, and record the repair.", "tags": ["water", "repair"]}, {"title": "Air quality response", "body": "Verify the sensor, inspect ventilation, and notify the operations team.", "tags": ["air", "sensor"]}, {"title": "Power outage response", "body": "Check the local supply and dispatch a qualified power technician.", "tags": ["power", "dispatch"]}]
db.knowledgeDocuments.insert_many(docs)
print("Seeded", db.name)
