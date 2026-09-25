import os
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from pinecone import Pinecone, ServerlessSpec

app = FastAPI(
    title="APEX Master NFL Vector Intelligence & Score Engine",
    description="Proprietary 16-Dimensional Sports Intelligence & Score Projection Engine",
    version="4.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Historical Seeding Data
MASTER_HISTORICAL_GAMES = [
    {
        "id": "HIST_NFL_2024_AFC_CHAMP_BUF_KC",
        "values": [0.82, 0.28, 0.79, 0.15, 0.74, 0.85, 0.40, 0.05, 0.10, 0.90, 0.78, 0.82, 0.65, 0.95, 0.80, 0.85],
        "metadata": {
            "sport": "NFL", "season": "2024", "date": "2024-01-21", 
            "matchup": "BUF @ KC", "final_score": "24 - 27", 
            "ats_result": "KC Covers (-2.5)", "market_signal": "Sharp Side Underdog Cover"
        }
    },
    {
        "id": "HIST_NFL_2023_WINTER_SF_GB",
        "values": [0.88, 0.18, 0.65, 0.10, 0.80, 0.70, 0.60, 0.00, 0.85, 0.80, 0.82, 0.45, 0.40, 0.30, 0.85, 0.90],
        "metadata": {
            "sport": "NFL", "season": "2023", "date": "2024-01-20", 
            "matchup": "GB @ SF", "final_score": "21 - 24", 
            "ats_result": "GB Covers (+9.5)", "market_signal": "Weather Total Under Value"
        }
    }
]

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()
INDEX_NAME = "apex-sports-index-16d"
pinecone_index = None

if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        if INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=INDEX_NAME, dimension=16, metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        pinecone_index = pc.Index(INDEX_NAME)
        stats = pinecone_index.describe_index_stats()
        if stats.get("total_vector_count", 0) == 0:
            pinecone_index.upsert(vectors=MASTER_HISTORICAL_GAMES)
    except Exception as e:
        print(f"Pinecone error: {e}")

class MasterMatchupRequest(BaseModel):
    team_name: str
    opponent_name: str
    offensive_rating: float
    defensive_rating: float
    snap_pace: float
    turnover_margin: float
    success_rate: float
    rest_advantage_days: float
    travel_miles: float
    injury_impact_weight: float
    weather_severity: float
    coaching_scheme_index: float
    public_money_pct: float
    sharp_money_indicator: float
    line_movement_volatility: float
    divisional_rivalry: float
    red_zone_efficiency: float
    pass_rush_win_rate: float

class MasterIntelligenceEngine:
    @staticmethod
    def vectorize(req: MasterMatchupRequest) -> np.ndarray:
        vec = np.array([
            (req.offensive_rating - 10.0) / 30.0,
            (req.defensive_rating - 10.0) / 30.0,
            (req.snap_pace - 50.0) / 30.0,
            (req.turnover_margin + 5.0) / 10.0,
            req.success_rate / 100.0,
            min(max(req.rest_advantage_days + 5.0, 0.0) / 10.0, 1.0),
            min(req.travel_miles / 3000.0, 1.0),
            max(0.0, min(req.injury_impact_weight, 1.0)),
            max(0.0, min(req.weather_severity, 1.0)),
            max(0.0, min(req.coaching_scheme_index, 1.0)),
            req.public_money_pct / 100.0,
            max(0.0, min(req.sharp_money_indicator, 1.0)),
            max(0.0, min(req.line_movement_volatility, 1.0)),
            max(0.0, min(req.divisional_rivalry, 1.0)),
            req.red_zone_efficiency / 100.0,
            req.pass_rush_win_rate / 100.0
        ], dtype=float)
        return np.clip(vec, 0.0, 1.0)

    @staticmethod
    def project_score(base_score_str: str, req: MasterMatchupRequest, similarity: float) -> dict:
        try:
            parts = base_score_str.split("-")
            base_team_score = float(parts[0].strip())
            base_opp_score = float(parts[1].strip())
        except Exception:
            base_team_score, base_opp_score = 24.0, 21.0

        off_modifier = (req.offensive_rating - 24.0) * 0.35
        def_modifier = (24.0 - req.defensive_rating) * 0.30
        weather_drag = req.weather_severity * -3.5

        projected_team = round(max(6.0, base_team_score + off_modifier + weather_drag), 1)
        projected_opp = round(max(6.0, base_opp_score + def_modifier + weather_drag), 1)

        edge = "NEUTRAL MARKET"
        if similarity >= 80.0 and req.sharp_money_indicator > 0.75 and req.public_money_pct < 45.0:
            edge = "ELITE SHARP FADE / VALUE EDGE (A+)"
        elif similarity >= 75.0 and req.public_money_pct > 70.0:
            edge = "PUBLIC TRAP WARNING / FADE PUBLIC (B+)"
        elif similarity >= 70.0:
            edge = "SOLID MODEL ALIGNMENT (B)"

        return {
            "projected_team_score": projected_team,
            "projected_opponent_score": projected_opp,
            "projected_total": round(projected_team + projected_opp, 1),
            "market_edge_rating": edge
        }

@app.get("/")
def serve_dashboard():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Online", "message": "Backend running, but index.html is missing from root directory."}

@app.post("/api/v1/analyze-matchup")
def analyze_matchup(req: MasterMatchupRequest):
    if not pinecone_index:
        raise HTTPException(status_code=500, detail="Pinecone vector database offline.")
    
    try:
        target_vec = MasterIntelligenceEngine.vectorize(req).tolist()
        query_response = pinecone_index.query(
            vector=target_vec, top_k=3, include_metadata=True, filter={"sport": {"$eq": "NFL"}}
        )

        matches = query_response.matches
        if not matches:
            raise HTTPException(status_code=404, detail="No matching historical vector twins found.")

        best_match = matches[0]
        meta = best_match.metadata or {}
        top_similarity = round(float(best_match.score) * 100, 2)

        score_projection = MasterIntelligenceEngine.project_score(
            meta.get("final_score", "24 - 21"), req, top_similarity
        )

        historical_twins = []
        for match in matches:
            m_meta = match.metadata or {}
            historical_twins.append({
                "historical_game_id": match.id,
                "season": m_meta.get("season", "N/A"),
                "date": m_meta.get("date", "N/A"),
                "historical_matchup": m_meta.get("matchup", "N/A"),
                "final_score": m_meta.get("final_score", "N/A"),
                "ats_outcome": m_meta.get("ats_result", "N/A"),
                "market_signal": m_meta.get("market_signal", "N/A"),
                "similarity_score": round(float(match.score) * 100, 2)
            })

        rationale = (
            f"Projection modeled directly off top structural twin {meta.get('matchup')} ({meta.get('season')}), "
            f"sharing a {top_similarity}% multidimensional alignment (Weather Factor: {req.weather_severity}, "
            f"Sharp Indicator: {req.sharp_money_indicator}, Public Handle: {req.public_money_pct}%). "
            f"The historical game concluded {meta.get('final_score')} ({meta.get('ats_result')}). "
            f"Adjusted for current offensive efficiency ({req.offensive_rating}) and defensive metrics, "
            f"the engine projects a final score of {score_projection['projected_team_score']} to "
            f"{score_projection['projected_opponent_score']}."
        )

        return {
            "target_matchup": f"{req.team_name} vs {req.opponent_name}",
            "top_twin_reference": meta.get("matchup"),
            "structural_similarity_pct": top_similarity,
            "score_prediction": score_projection,
            "analytical_rationale": rationale,
            "top_historical_twins": historical_twins
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
