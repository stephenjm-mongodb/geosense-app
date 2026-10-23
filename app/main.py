import math
import os
import re
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo import ReturnDocument, GEOSPHERE, ASCENDING, DESCENDING
from app.db import db, ping

app = FastAPI(title="GeoSense", version="0.1.0")
ATLAS_SEARCH = os.getenv("GEOSENSE_ATLAS_SEARCH", "false").lower() == "true"

class Point(BaseModel):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)

class IncidentIn(BaseModel):
    incidentId: str
    title: str
    description: str
    category: str = "general"
    severity: str = "medium"
    location: Point
    sensorIds: list[str] = []

class ReadingIn(BaseModel):
    timestamp: datetime | None = None
    value: float
    metric: str = "temperature"
    unit: str = "celsius"

class AssignIn(BaseModel):
    requiredSkill: str

class SearchIn(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=50)


def now():
    return datetime.now(timezone.utc)

def clean(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value

def geo(point: Point):
    return {"type": "Point", "coordinates": [point.longitude, point.latitude]}

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b)); na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def local_embedding(text: str, dim: int = 32):
    values = [0.0] * dim
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        values[hash(token) % dim] += 1.0
    return values

@app.get("/health")
def health():
    try:
        ping()
        return {"status": "ok", "database": db.name, "atlasSearch": ATLAS_SEARCH}
    except Exception as exc:
        raise HTTPException(503, detail=f"MongoDB unavailable: {exc}")

@app.post("/incidents")
def create_incident(body: IncidentIn):
    doc = body.model_dump(); doc["location"] = geo(body.location); doc["createdAt"] = now(); doc["status"] = "open"
    db.incidents.insert_one(doc)
    return doc

@app.get("/agents/nearby")
def nearby_agents(longitude: float, latitude: float, max_distance_m: int = Query(5000, ge=1, le=100000)):
    pipeline = [{"$geoNear": {"near": {"type": "Point", "coordinates": [longitude, latitude]}, "distanceField": "distanceMeters", "maxDistance": max_distance_m, "spherical": True}}, {"$match": {"available": True}}, {"$limit": 50}]
    return clean(list(db.agents.aggregate(pipeline)))

@app.post("/incidents/{incident_id}/assign")
def assign_incident(incident_id: str, body: AssignIn):
    incident = db.incidents.find_one({"incidentId": incident_id})
    if not incident: raise HTTPException(404, "Incident not found")
    coords = incident["location"]["coordinates"]
    candidates = db.agents.aggregate([{"$geoNear": {"near": {"type": "Point", "coordinates": coords}, "distanceField": "distanceMeters", "spherical": True}}, {"$match": {"available": True, "skills": body.requiredSkill}}, {"$limit": 20}])
    for candidate in candidates:
        updated = db.agents.find_one_and_update({"_id": candidate["_id"], "available": True}, {"$set": {"available": False, "updatedAt": now()}}, return_document=ReturnDocument.AFTER)
        if updated:
            result = db.incidents.find_one_and_update({"incidentId": incident_id, "status": "open"}, {"$set": {"status": "assigned", "agentId": updated["agentId"], "assignedAt": now()}}, return_document=ReturnDocument.AFTER)
            if result: return clean({"incident": result, "agent": updated})
            db.agents.update_one({"_id": updated["_id"]}, {"$set": {"available": True}})
    raise HTTPException(409, "No available agent could be assigned")

@app.post("/sensors/{sensor_id}/readings")
def add_reading(sensor_id: str, body: ReadingIn):
    doc = body.model_dump(); doc["sensorId"] = sensor_id; doc["timestamp"] = doc["timestamp"] or now()
    result = db.sensorReadings.insert_one(doc); doc["_id"] = str(result.inserted_id); return doc

@app.get("/sensors/{sensor_id}/trend")
def trend(sensor_id: str, limit: int = Query(100, ge=1, le=1000)):
    return clean(list(db.sensorReadings.find({"sensorId": sensor_id}).sort("timestamp", DESCENDING).limit(limit)))

@app.get("/search/lexical")
def lexical(q: str, limit: int = Query(10, ge=1, le=50)):
    if ATLAS_SEARCH:
        try:
            return clean(list(db.knowledgeDocuments.aggregate([{"$search": {"text": {"query": q, "path": ["title", "body"]}}}, {"$limit": limit}, {"$project": {"title": 1, "body": 1, "score": {"$meta": "searchScore"}}}])))
        except Exception:
            pass
    rx = {"$regex": re.escape(q), "$options": "i"}
    return clean(list(db.knowledgeDocuments.find({"$or": [{"title": rx}, {"body": rx}]}).limit(limit)))

@app.post("/search/semantic")
def semantic(body: SearchIn):
    vector = local_embedding(body.query)
    if ATLAS_SEARCH:
        try:
            return clean(list(db.knowledgeDocuments.aggregate([{"$vectorSearch": {"index": "knowledge_vector", "path": "embedding", "queryVector": vector, "numCandidates": 100, "limit": body.limit}}, {"$project": {"title": 1, "body": 1, "score": {"$meta": "vectorSearchScore"}}}])))
        except Exception:
            pass
    docs = list(db.knowledgeDocuments.find({"embedding": {"$exists": True}}))
    for doc in docs: doc["score"] = cosine(vector, doc["embedding"])
    return clean(sorted(docs, key=lambda d: d["score"], reverse=True)[:body.limit])

@app.get("/search/hybrid")
def hybrid(q: str, limit: int = Query(10, ge=1, le=50)):
    lexical_docs = lexical(q, limit=limit); semantic_docs = semantic(SearchIn(query=q, limit=limit))
    merged = {}
    for rank, doc in enumerate(lexical_docs): merged[str(doc.get("_id"))] = {**doc, "hybridScore": 1/(rank+1)}
    for rank, doc in enumerate(semantic_docs):
        key = str(doc.get("_id")); merged.setdefault(key, {**doc, "hybridScore": 0}); merged[key]["hybridScore"] += 1/(rank+1)
    return clean(sorted(merged.values(), key=lambda d: d["hybridScore"], reverse=True)[:limit])

@app.get("/reports/response-time")
def response_time():
    return clean(list(db.incidents.aggregate([{"$group": {"_id": "$category", "count": {"$sum": 1}, "avgSeverity": {"$avg": {"$switch": {"branches": [{"case": {"$eq": ["$severity", "critical"]}, "then": 4}, {"case": {"$eq": ["$severity", "high"]}, "then": 3}, {"case": {"$eq": ["$severity", "medium"]}, "then": 2}], "default": 1}}}}}])))

@app.get("/reports/thresholds")
def thresholds():
    return clean(list(db.sensorReadings.aggregate([{"$group": {"_id": {"sensorId": "$sensorId", "metric": "$metric"}, "max": {"$max": "$value"}, "avg": {"$avg": "$value"}, "count": {"$sum": 1}}}, {"$sort": {"max": -1}}])))
