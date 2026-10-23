import os
from pymongo import MongoClient

URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE = os.getenv("MONGODB_DATABASE", "geosense")
client = MongoClient(URI, serverSelectionTimeoutMS=3000)
db = client[DATABASE]

def ping():
    return client.admin.command("ping")
