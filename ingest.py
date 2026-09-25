import os
import numpy as np
from pinecone import Pinecone, ServerlessSpec

# 1. Initialize Pinecone Client
# Retrieves key from environment variable set on Render or local shell
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "YOUR_PINECONE_API_KEY_HERE")
INDEX_NAME = "apex-sports-index"

pc = Pinecone(api_key=PINECONE_API_KEY)

# 2. Ensure Serverless Index Exists (8-Dimensional Cosine Similarity)
existing_indexes = [idx.name for idx in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    print(f"Creating Pinecone Index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=8,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

# 3. Vectorization Engine (Mirrors VectorEngine in main.py)
def normalize_nba_stats(off, defense, pace, to_pct, efg, rest, travel, injury):
    off_norm = (off - 90.0) / (130.0 - 90.0)
    def_norm = (defense - 90.0) / (130.0 - 90.0)
    pace_norm = (pace - 90.0) / (110.0 - 90.0)
    to_norm = to_pct / 25.0
    efg_norm = (efg - 40.0) / (65.0 - 40.0)
    rest_norm = min(rest / 7.0, 1.0)
    travel_norm = min(travel / 3000.0, 1.0)
    injury_norm = max(0.0, min(injury, 1.0))
    
    vec = np.array([off_norm, def_norm, pace_norm, to_norm, efg_norm, rest_norm, travel_norm, injury_norm])
    return np.clip(vec, 0.0, 1.0).tolist()

# 4. Historical Dataset Seeding
RAW_HISTORICAL_GAMES = [
    {
        "id": "HIST_NBA_2024_001",
        "team": "Boston Celtics",
        "opponent": "Golden State Warriors",
        "sport": "NBA",
        "date": "2024-03-12",
        "score": "118-112",
        "stats": (122.4, 110.1, 98.5, 12.1, 56.4, 2, 450, 0.05)
    },
    {
        "id": "HIST_NBA_2024_002",
        "team": "Denver Nuggets",
        "opponent": "LA Lakers",
        "sport": "NBA",
        "date": "2023-11-20",
        "score": "108-104",
        "stats": (118.2, 112.5, 96.0, 11.5, 54.8, 3, 1200, 0.10)
    },
    {
        "id": "HIST_NBA_2024_003",
        "team": "Milwaukee Bucks",
        "opponent": "Miami Heat",
        "sport": "NBA",
        "date": "2024-02-14",
        "score": "112-106",
        "stats": (116.0, 114.2, 100.2, 13.8, 52.1, 1, 800, 0.25)
    }
]

# 5. Format & Upsert Records
vectors_to_upsert = []
for game in RAW_HISTORICAL_GAMES:
    vec = normalize_nba_stats(*game["stats"])
    vectors_to_upsert.append({
        "id": game["id"],
        "values": vec,
        "metadata": {
            "sport": game["sport"],
            "team_name": game["team"],
            "matchup": f"{game['team']} vs {game['opponent']}",
            "date": game["date"],
            "final_score": game["score"]
        }
    })

print(f"Upserting {len(vectors_to_upsert)} historical games into Pinecone...")
index.upsert(vectors=vectors_to_upsert)
print("Ingestion complete successfully!")
