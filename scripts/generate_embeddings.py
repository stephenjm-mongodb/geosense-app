import os, re, hashlib
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db = MongoClient(uri)[os.getenv("MONGODB_DATABASE", "geosense")]
dim = int(os.getenv("GEOSENSE_EMBEDDING_DIM", "32"))
def embed(text):
    v = [0.0] * dim
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        v[int(hashlib.sha256(token.encode()).hexdigest(), 16) % dim] += 1.0
    return v
for doc in db.knowledgeDocuments.find({}):
    text = f"{doc.get('title', '')} {doc.get('body', '')}"
    db.knowledgeDocuments.update_one({"_id": doc["_id"]}, {"$set": {"embedding": embed(text)}})
print("Generated deterministic demo vectors. Replace with a real embedding provider for semantic quality.")
