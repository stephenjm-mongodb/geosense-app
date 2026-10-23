import os
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
print("Watching incidents; Ctrl-C to stop")
try:
    with db.incidents.watch(full_document="updateLookup") as stream:
        for change in stream:
            print(change)
except Exception as exc:
    print("Change streams require a replica set or sharded cluster:", exc)
