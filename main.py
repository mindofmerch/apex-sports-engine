import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Initialize FastAPI App
app = FastAPI(
    title="APEX Sports Vector Matching Engine",
    description="Phase 1 Backend Engine: Feature Scaling, Vectorization, and k-NN Match Engine",
    version="1.0.0"
)

# Enable CORS for local and web frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 1. DOMAIN SCHEMAS & MODELS
# -------------------------------------------------------------------

class RawTeamStats(BaseModel):
    team_name: str
    sport: str  # e.g., 'NBA', 'NFL'
    offensive_rating: float  # Off Efficiency / Points per 100
    defensive_rating: float  # Def Efficiency / Points Allowed
    pace: float              # Possessions / Snap Count per Game
    turnover_pct: float      # Turnover Rate percentage (0-100)
    effective_fg_pct: float  # eFG% or Success Rate (0-100)
    rest_days: float         # Days off since last game (0-10)
    travel_miles: float      # Distance traveled for fixture (0-3000)
    injury_impact: float     # Key starter absence weight (0.0 to 1.0)

class SimilarityRequest(BaseModel):
    target_vector: List[float]
    top_k: int = 5
    sport_filter: Optional[str] = None

# -------------------------------------------------------------------
# 2. VECTORIZATION & FEATURE NORMALIZATION ENGINE
# -------------------------------------------------------------------

class VectorEngine:
    @staticmethod
    def normalize_stats(stats: RawTeamStats) -> np.ndarray:
        if stats.sport.upper() == "NBA":
            off_norm = (stats.offensive_rating - 90.0) / (130.0 - 90.0)
            def_norm = (stats.defensive_rating - 90.0) / (130.0 - 90.0)
            pace_norm = (stats.pace - 90.0) / (110.0 - 90.0)
            to_norm = stats.turnover_pct / 25.0
            efg_norm = (stats.effective_fg_pct - 40.0) / (65.0 - 40.0)
        elif stats.sport.upper() == "NFL":
            off_norm = (stats.offensive_rating - 10.0) / (40.0 - 10.0)
            def_norm = (stats.defensive_rating - 10.0) / (40.0 - 10.0)
            pace_norm = (stats.pace - 50.0) / (80.0 - 50.0)
            to_norm = stats.turnover_pct / 30.0
            efg_norm = stats.effective_fg_pct / 100.0
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
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return float(dot_product / (norm_v1 * norm_v2))

    @staticmethod
    def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        return float(np.linalg.norm(v1 - v2))

# -------------------------------------------------------------------
# 3. MOCK HISTORICAL VECTOR DATABASE
# -------------------------------------------------------------------

HISTORICAL_DATABASE: List[dict] = [
    {
        "game_id": "HIST_NBA_001",
        "sport": "NBA",
        "date": "2024-03-12",
        "home_team": "Boston Celtics",
        "away_team": "Golden State Warriors",
        "score_home": 118,
        "score_away": 112,
        "vector": [0.85, 0.32, 0.65, 0.42, 0.78, 0.28, 0.10, 0.05]
    },
    {
        "game_id": "HIST_NBA_002",
        "sport": "NBA",
        "date": "2023-11-20",
        "home_team": "Denver Nuggets",
        "away_team": "LA Lakers",
        "score_home": 108,
        "score_away": 104,
        "vector": [0.78, 0.45, 0.52, 0.38, 0.71, 0.42, 0.25, 0.12]
    },
    {
        "game_id": "HIST_NFL_001",
        "sport": "NFL",
        "date": "2024-01-14",
        "home_team": "Kansas City Chiefs",
        "away_team": "Buffalo Bills",
        "score_home": 27,
        "score_away": 24,
        "vector": [0.72, 0.28, 0.81, 0.20, 0.65, 0.85, 0.40, 0.10]
    },
    {
        "game_id": "HIST_NFL_002",
        "sport": "NFL",
        "date": "2023-12-10",
        "home_team": "San Francisco 49ers",
        "away_team": "Dallas Cowboys",
        "score_home": 31,
        "score_away": 10,
        "vector": [0.91, 0.15, 0.75, 0.12, 0.82, 0.57, 0.05, 0.00]
    }
]

# -------------------------------------------------------------------
# 4. API ENDPOINTS
# -------------------------------------------------------------------

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "engine": "APEX Vector Ingestion & k-NN Engine",
        "phase": 1,
        "endpoints": ["/api/v1/vectorize", "/api/v1/match-twins", "/api/v1/database"]
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
    target = np.array(request.target_vector, dtype=float)
    results = []

    for game in HISTORICAL_DATABASE:
        if request.sport_filter and game["sport"].upper() != request.sport_filter.upper():
            continue

        db_vec = np.array(game["vector"], dtype=float)
        cos_sim = VectorEngine.cosine_similarity(target, db_vec)
        euc_dist = VectorEngine.euclidean_distance(target, db_vec)

        results.append({
            "game_id": game["game_id"],
            "sport": game["sport"],
            "date": game["date"],
            "matchup": f"{game['away_team']} @ {game['home_team']}",
            "final_score": f"{game['score_away']} - {game['score_home']}",
            "similarity_score": round(cos_sim * 100, 2),
            "euclidean_distance": round(euc_dist, 4)
        })

    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
    return {
        "total_matches_searched": len(HISTORICAL_DATABASE),
        "top_k_twins": results[:request.top_k]
    }

@app.get("/api/v1/database")
def get_historical_database():
    return {"count": len(HISTORICAL_DATABASE), "games": HISTORICAL_DATABASE}
