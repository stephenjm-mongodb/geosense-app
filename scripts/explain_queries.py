import os, json
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
queries = {
    "incident_status": db.incidents.find({"status": "open"}),
    "nearby_incidents": db.incidents.find({"location": {"$near": {"$geometry": {"type": "Point", "coordinates": [-6.26, 53.35]}, "$maxDistance": 5000}}}),
    "sensor_trend": db.sensorReadings.find({"sensorId": "S-001"}).sort("timestamp", -1).limit(20),
}
for name, cursor in queries.items():
    try:
        print("\n###", name)
        print(json.dumps(cursor.explain("executionStats"), default=str, indent=2))
    except Exception as exc:
        print(name, "ERROR", exc)
