import json, os
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
search = {"name": "knowledge_search", "definition": {"mappings": {"dynamic": False, "fields": {"title": {"type": "string"}, "body": {"type": "string"}, "tags": {"type": "string"}}}}}
vector = {"name": "knowledge_vector", "type": "vectorSearch", "fields": [{"type": "vector", "path": "embedding", "numDimensions": 32, "similarity": "cosine"}]}
print(json.dumps({"searchIndex": search, "vectorIndex": vector}, indent=2))
try:
    print(db.command({"createSearchIndexes": "knowledgeDocuments", "indexes": [search]}))
except Exception as exc:
    print("Atlas Search index creation unavailable here; create it in Atlas or with Atlas CLI:", exc)
