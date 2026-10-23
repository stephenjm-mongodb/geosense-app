import os, sys, time, random
from datetime import datetime, timezone
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 30
end = time.time() + seconds; count = 0
while time.time() < end:
    docs = [{"sensorId": f"S-{i:03}", "timestamp": datetime.now(timezone.utc), "metric": metric, "value": round(random.gauss(20, 4), 2), "unit": "celsius"} for i in range(1, 6) for metric in ["temperature", "air_quality"]]
    db.sensorReadings.insert_many(docs); count += len(docs); time.sleep(.25)
print("inserted", count, "readings")
