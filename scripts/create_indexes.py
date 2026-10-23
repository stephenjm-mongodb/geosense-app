import os
from pymongo import MongoClient, GEOSPHERE, ASCENDING, DESCENDING
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
for collection, indexes in {
    "agents": [("location", GEOSPHERE), ("available", ASCENDING), ("skills", ASCENDING)],
    "facilities": [("location", GEOSPHERE)],
    "incidents": [("location", GEOSPHERE), ("status", ASCENDING), ("category", ASCENDING), ("createdAt", DESCENDING)],
    "sensorReadings": [("sensorId", ASCENDING), ("timestamp", DESCENDING)],
    "knowledgeDocuments": [("title", ASCENDING), ("tags", ASCENDING)],
}.items():
    for field, kind in indexes:
        print(collection, db[collection].create_index([(field, kind)]))
