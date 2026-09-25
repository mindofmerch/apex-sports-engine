import os
import time
import requests

# Memory cache layer to prevent spamming The Odds API and hitting rate limits
_ODDS_CACHE = {
    "data": None,
    "timestamp": 0
}
CACHE_TTL = 300  # Cache live odds for 5 minutes (300 seconds)

def fetch_cached_odds(odds_api_key):
    global _ODDS_CACHE
    current_time = time.time()
    
    # Return cached odds if still fresh
    if _ODDS_CACHE["data"] and (current_time - _ODDS_CACHE["timestamp"] < CACHE_TTL):
        return _ODDS_CACHE["data"]
    
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
    params = {
        "apiKey": odds_api_key,
        "regions": "us",
        "markets": "spreads,totals,h2h",
        "oddsFormat": "american"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Update cache
    _ODDS_CACHE["data"] = data
    _ODDS_CACHE["timestamp"] = current_time
    return data

def process_current_nfl_game(home_team, away_team):
    try:
        odds_api_key = os.getenv("API_KEYS")
        
        if not odds_api_key:
            raise ValueError("API_KEYS environment variable is missing on Render.")

        data = fetch_cached_odds(odds_api_key)

        live_game = None
        for game in data:
            if (home_team.lower() in game.get("home_team", "").lower() and 
                away_team.lower() in game.get("away_team", "").lower()):
                live_game = game
                break

        historical_data = {
            "matchupCount": 6,
            "homeTeamHistoricalWins": 4,
            "awayTeamHistoricalWins": 2,
            "averagePointDifferential": 4.5
        }

        prediction_result = synthesize_game_script_and_scores(live_game, historical_data, home_team, away_team)

        return {
            "success": True,
            "brand": "Y.E.S. Sports: Your Edge Sports",
            "matchup": f"{away_team} @ {home_team}",
            "marketData": live_game.get("bookmakers", [{}])[0] if live_game and live_game.get("bookmakers") else "No active market odds found",
            "historicalContext": historical_data,
            "prediction": prediction_result
        }

    except Exception as error:
        print(f"Y.E.S. Sports Pipeline Error: {error}")
        raise error

def synthesize_game_script_and_scores(live_odds, history, home_team, away_team):
    market_spread = 0.0
    market_total = 45.5

    if live_odds and live_odds.get("bookmakers"):
        bookmaker = live_odds["bookmakers"][0]
        for market in bookmaker.get("markets", []):
            if market["key"] == "spreads":
                for outcome in market.get("outcomes", []):
                    if home_team.lower() in outcome.get("name", "").lower():
                        market_spread = outcome.get("point", 0.0)
            elif market["key"] == "totals":
                if market.get("outcomes"):
                    market_total = market["outcomes"][0].get("point", 45.5)

    historical_adjustment = history["averagePointDifferential"] * 0.3
    home_implied = (market_total / 2) - (market_spread / 2) + historical_adjustment
    away_implied = (market_total / 2) + (market_spread / 2) - historical_adjustment

    game_script_narrative = (
        f"{home_team} projected to control tempo early, forcing a pass-heavy script."
        if market_spread < -3
        else "A tight contest projected; expect efficient red-zone clock control."
    )

    return {
        "predictedScoreHome": max(0, round(home_implied)),
        "predictedScoreAway": max(0, round(away_implied)),
        "marketSpreadUsed": market_spread,
        "marketTotalUsed": market_total,
        "gameScriptNarrative": game_script_narrative
    }
