import os
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pinecone import Pinecone, ServerlessSpec

# 1. Initialize FastAPI Application
app = FastAPI(
    title="APEX Sports Vector Matching Engine",
    description="Phase 2/3 Engine: Auto-Provisioned Pinecone Vector Database & Match Engine",
    version="2.1.0"
)

# Enable CORS for cross-origin frontend dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialize Pinecone Client & Ensure Index Exists
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()
INDEX_NAME = "apex-sports-index"

pinecone_index = None

if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Fetch list of active indexes
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        # Auto-create index if missing to prevent 404 errors
        if INDEX_NAME not in existing_indexes:
            print(f"Index '{INDEX_NAME}' not found. Auto-creating serverless index...")
            pc.create_index(
                name=INDEX_NAME,
                dimension=8,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            
        pinecone_index = pc.Index(INDEX_NAME)
        print("Successfully authenticated and connected to Pinecone!")
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")
else:
    print("Warning: PINECONE_API_KEY environment variable is not set on Render.")

# 3. Domain Schemas & Models
class RawTeamStats(BaseModel):
    team_name: str
    sport: str  # e.g., 'NBA', 'NFL'
    offensive_rating: float
    defensive_rating: float
    pace: float
    turnover_pct: float
    effective_fg_pct: float
    rest_days: float
    travel_miles: float
    injury_impact: float

class SimilarityRequest(BaseModel):
    target_vector: List[float]
    top_k: int = 5
    sport_filter: Optional[str] = None

# 4. Vector Normalization & Math Engine
class VectorEngine:
    @staticmethod
    def normalize_stats(stats: RawTeamStats) -> np.ndarray:
        if stats.sport.upper() == "NBA":
            off_norm = (stats.offensive_rating - 90.0) / (130.0 - 90.0)
            def_norm = (stats.defensive_rating - 90.0) / (130.0 - 90.0)
            pace_norm = (stats.pace - 90.0) / (110.0 - 90.0)
            to_norm = stats.turnover_pct / 25.0
            efg_norm = (stats.effective_fg_pct - 40.0) / (65.0 - 40.0)
        else:
            off_norm = stats.offensive_rating / 150.0
            def_norm = stats.defensive_rating / 150.0
            pace_norm = stats.pace / 120.0
            to_norm = stats.turnover_pct / 100.0
            efg_norm = stats.effective_fg_pct / 100.0

        rest_norm = min(stats.rest_days / 7.0, 1.0)
        travel_norm = min(stats.travel_miles / 3000.0, 1.0)
        injury_norm = max(0.0, min(stats.injury_impact, 1.0))

        vector = np.array([
            off_norm, def_norm, pace_norm, to_norm,
            efg_norm, rest_norm, travel_norm, injury_norm
        ], dtype=float)

        return np.clip(vector, 0.0, 1.0)

    @staticmethod
    def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        return float(np.linalg.norm(v1 - v2))

# 5. API Endpoints
@app.get("/")
def read_root():
    return {
        "status": "Online",
        "engine": "APEX Vector Ingestion & Pinecone Match Engine",
        "phase": 2,
        "pinecone_connected": pinecone_index is not None
    }

@app.post("/api/v1/vectorize")
def vectorize_team_stats(stats: RawTeamStats):
    try:
        vector = VectorEngine.normalize_stats(stats)
        return {
            "team_name": stats.team_name,
            "sport": stats.sport,
            "vector": vector.tolist(),
            "vector_dimensions": len(vector)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/match-twins")
def find_twin_games(request: SimilarityRequest):
    if not pinecone_index:
        raise HTTPException(
            status_code=500, 
            detail="Pinecone is not initialized. Please verify PINECONE_API_KEY in Render environment settings."
        )

    try:
        metadata_filter = {}
        if request.sport_filter:
            metadata_filter = {"sport": {"$eq": request.sport_filter.upper()}}

        # Query vector database
        query_response = pinecone_index.query(
            vector=request.target_vector,
            top_k=request.top_k,
            include_metadata=True,
            filter=metadata_filter if metadata_filter else None
        )

        results = []
        for match in query_response.matches:
            meta = match.metadata or {}
            sim_score = round(float(match.score) * 100, 2)
            
            euc_dist = 0.0
            if match.values:
                db_vec = np.array(match.values, dtype=float)
                target_vec = np.array(request.target_vector, dtype=float)
                euc_dist = VectorEngine.euclidean_distance(target_vec, db_vec)

            results.append({
                "game_id": match.id,
                "sport": meta.get("sport", "N/A"),
                "date": meta.get("date", "N/A"),
                "matchup": meta.get("matchup", "N/A"),
                "final_score": meta.get("final_score", "N/A"),
                "similarity_score": sim_score,
                "euclidean_distance": round(euc_dist, 4)
            })

        return {
            "total_matches_returned": len(results),
            "top_k_twins": results
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/seed-database")
def seed_pinecone_data():
    """Quick seeding route to populate the Pinecone index with sample games."""
    if not pinecone_index:
        raise HTTPException(status_code=500, detail="Pinecone index not initialized.")

    sample_games = [
        {
            "id": "HIST_NBA_001",
            "values": [0.85, 0.32, 0.65, 0.42, 0.78, 0.28, 0.10, 0.05],
            "metadata": {"sport": "NBA", "date": "2024-03-12", "matchup": "GSW @ BOS", "final_score": "112 - 118"}
        },
        {
            "id": "HIST_NBA_002",
            "values": [0.78, 0.45, 0.52, 0.38, 0.71, 0.42, 0.25, 0.12],
            "metadata": {"sport": "NBA", "date": "2023-11-20", "matchup": "LAL @ DEN", "final_score": "104 - 108"}
        },
        {
            "id": "HIST_NFL_001",
            "values": [0.72, 0.28, 0.81, 0.20, 0.65, 0.85, 0.40, 0.10],
            "metadata": {"sport": "NFL", "date": "2024-01-14", "matchup": "BUF @ KC", "final_score": "24 - 27"}
        }
    ]

    pinecone_index.upsert(vectors=sample_games)
    return {"status": "Success", "message": f"Successfully seeded {len(sample_games)} games into Pinecone!"}
