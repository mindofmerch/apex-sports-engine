import os
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pinecone import Pinecone, ServerlessSpec

# 1. Initialize FastAPI Application
app = FastAPI(
    title="APEX NFL Vector Intelligence Engine",
    description="Production-Grade NFL Match Twin & Edge Engine",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. NFL Historical Baseline Seeding Data
NFL_HISTORICAL_GAMES = [
    {
        "id": "HIST_NFL_2024_KC_BUF",
        "values": [0.78, 0.25, 0.82, 0.18, 0.68, 0.85, 0.40, 0.05],
        "metadata": {"sport": "NFL", "date": "2024-01-14", "matchup": "BUF @ KC", "final_score": "24 - 27"}
    },
    {
        "id": "HIST_NFL_2023_SF_DAL",
        "values": [0.90, 0.15, 0.75, 0.10, 0.82, 0.60, 0.10, 0.00],
        "metadata": {"sport": "NFL", "date": "2023-10-08", "matchup": "DAL @ SF", "final_score": "10 - 31"}
    },
    {
        "id": "HIST_NFL_2024_BAL_DET",
        "values": [0.82, 0.30, 0.70, 0.22, 0.72, 0.75, 0.50, 0.10],
        "metadata": {"sport": "NFL", "date": "2024-11-10", "matchup": "DET @ BAL", "final_score": "28 - 35"}
    }
]

# 3. Initialize Pinecone & Auto-Seed NFL Index
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()
INDEX_NAME = "apex-sports-index"

pinecone_index = None

if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if INDEX_NAME not in existing_indexes:
            print(f"Creating Pinecone Index '{INDEX_NAME}'...")
            pc.create_index(
                name=INDEX_NAME,
                dimension=8,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            
        pinecone_index = pc.Index(INDEX_NAME)
        
        # Auto-seed if empty
        stats = pinecone_index.describe_index_stats()
        if stats.get("total_vector_count", 0) == 0:
            print("Seeding initial NFL historical database vectors...")
            pinecone_index.upsert(vectors=NFL_HISTORICAL_GAMES)
            print("NFL Seeding complete!")
            
    except Exception as e:
        print(f"Pinecone initialization error: {e}")

# 4. NFL Schemas
class RawNFLStats(BaseModel):
    team_name: str
    offensive_rating: float   # Points / Yards per game scale (e.g. 10.0 to 40.0)
    defensive_rating: float   # Points allowed scale (e.g. 10.0 to 40.0)
    pace: float               # Snaps per game (e.g. 50.0 to 80.0)
    turnover_pct: float       # Turnover rate (0 to 30)
    effective_fg_pct: float   # Success rate / 3rd-down conversion efficiency (0 to 100)
    rest_days: float          # Days since last game (0 to 10)
    travel_miles: float       # Travel distance (0 to 3000)
    injury_impact: float      # Key starter absence weight (0.0 to 1.0)

class SimilarityRequest(BaseModel):
    target_vector: List[float]
    top_k: int = 5

# 5. NFL Normalization Engine
class NFLEngine:
    @staticmethod
    def normalize_stats(stats: RawNFLStats) -> np.ndarray:
        off_norm = (stats.offensive_rating - 10.0) / (40.0 - 10.0)
        def_norm = (stats.defensive_rating - 10.0) / (40.0 - 10.0)
        pace_norm = (stats.pace - 50.0) / (80.0 - 50.0)
        to_norm = stats.turnover_pct / 30.0
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

# 6. Endpoints
@app.get("/")
def read_root():
    vector_count = 0
    if pinecone_index:
        try:
            stats = pinecone_index.describe_index_stats()
            vector_count = stats.get("total_vector_count", 0)
        except Exception:
            pass

    return {
        "status": "Online",
        "sport": "NFL",
        "engine": "APEX NFL Vector Intelligence Engine",
        "pinecone_connected": pinecone_index is not None,
        "indexed_vectors": vector_count
    }

@app.post("/api/v1/vectorize")
def vectorize_nfl_stats(stats: RawNFLStats):
    try:
        vector = NFLEngine.normalize_stats(stats)
        return {
            "team_name": stats.team_name,
            "sport": "NFL",
            "vector": vector.tolist(),
            "vector_dimensions": len(vector)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/match-twins")
def find_nfl_twin_games(request: SimilarityRequest):
    if not pinecone_index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized.")

    try:
        # Query Pinecone with strict NFL filter
        query_response = pinecone_index.query(
            vector=request.target_vector,
            top_k=request.top_k,
            include_metadata=True,
            filter={"sport": {"$eq": "NFL"}}
        )

        results = []
        for match in query_response.matches:
            meta = match.metadata or {}
            sim_score = round(float(match.score) * 100, 2)
            
            euc_dist = 0.0
            if match.values:
                db_vec = np.array(match.values, dtype=float)
                target_vec = np.array(request.target_vector, dtype=float)
                euc_dist = NFLEngine.euclidean_distance(target_vec, db_vg if 'db_vg' in locals() else db_vec)

            results.append({
                "game_id": match.id,
                "date": meta.get("date", "N/A"),
                "matchup": meta.get("matchup", "N/A"),
                "final_score": meta.get("final_score", "N/A"),
                "similarity_score": sim_score,
                "euclidean_distance": round(euc_dist, 4)
            })

        return {
            "sport": "NFL",
            "total_matches_returned": len(results),
            "top_k_twins": results
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
