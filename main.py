from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI(title="Y.E.S. SPORTS - 2026 Vector Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2026 MOCK DATABASE & VECTOR ARCHIVE ENGINE
# ==========================================

GAMES = [
    {"id": "det_buf", "away": "DET", "home": "BUF", "spread": "DET +5.5", "total": 54.5, "signal": "Signal 15", "reprice": "+1.0"},
    {"id": "phi_ten", "away": "PHI", "home": "TEN", "spread": "PHI -7", "total": 39.5, "signal": "Signal 26", "reprice": "BASE"},
    {"id": "min_chi", "away": "MIN", "home": "CHI", "spread": "MIN +4.5", "total": 48.5, "signal": "Signal 15", "reprice": "+1.0"},
    {"id": "sea_was", "away": "SEA", "home": "WAS", "spread": "SEA -7.5", "total": 40.5, "signal": "Signal 26", "reprice": "+1.5"},
]

# Advanced Vector Twin Engine Data (History Repeats)
# Matches based on O/D-Line, Coaching Pressure, Weather, Travel, Injuries
ARCHIVE_TWINS = {
    "det_buf": {
        "trench_adv": "DET O-Line (+8.4% Win Rate) vs BUF Pass Rush",
        "weather": "Clear, 48°F, Low Wind",
        "travel": "Standard cross-conference travel, neutral rest",
        "injuries": "BUF RT out, DET CB2 questionable",
        "coaching": "High Pressure (Aggressive 4th down scripts)",
        "twins": [
            {
                "year": "2024", "week": "Wk 15", "matchup": "DET 31 - CHI 26", "sim": "96.2%",
                "reason": "Exact O-Line vs D-Line metric match. Severe coaching pressure index (>8.5). DET successfully attacked backup RT all game."
            },
            {
                "year": "2022", "week": "Wk 12", "matchup": "BUF 28 - DET 25", "sim": "91.8%",
                "reason": "Similar travel/rest differential. Heavy passing game script forced by high total (54.5). Late game turnover variance dictated the spread cover."
            }
        ],
        "gold_script": "DET establishes early interior run to neutralize edge rush. BUF responds with quick-game passing. Expect a massive 3rd quarter scoring surge. DET covers +5.5 on a late backdoor drive. Projected Score: BUF 30 - DET 27."
    },
    "phi_ten": {
        "trench_adv": "PHI D-Line (+12.1% Pressure Rate) vs TEN O-Line",
        "weather": "Rain/Wind mix, 52°F",
        "travel": "PHI traveling off short week",
        "injuries": "TEN WR1 out, PHI DL rotational players out",
        "coaching": "Conservative clock control vs Aggressive heavy-box",
        "twins": [
            {
                "year": "2025", "week": "Wk 4", "matchup": "PHI 24 - TEN 10", "sim": "94.5%",
                "reason": "Identical weather vectors. PHI defensive front completely collapsed the pocket. Low scoring, gritty script where history repeated via trench dominance."
            },
            {
                "year": "2023", "week": "Wk 14", "matchup": "BAL 20 - TEN 16", "sim": "89.1%",
                "reason": "Matches the 'road favorite off short rest' algorithm. Heavy rain depressed the total. TEN covers the massive spread late in the 4th."
            }
        ],
        "gold_script": "Ugly, trench-warfare game. PHI dominates time of possession but struggles in the red zone due to weather. TEN hangs around via field goals. PHI wins but fails to cover the -7. Projected Score: PHI 20 - TEN 16."
    }
}

# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/api/slate")
def get_slate():
    return GAMES

@app.get("/api/analyze/{game_id}")
def analyze_game(game_id: str):
    data = ARCHIVE_TWINS.get(game_id)
    if not data:
        # Fallback for games without specific mock data
        data = ARCHIVE_TWINS["det_buf"]
    return data

# ==========================================
# FRONTEND UI / HTML
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Y.E.S. SPORTS | 2026 Vector Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-onyx: #06080e;
                --bg-charcoal: #0f172a;
                --accent-gold: #fbbf24;
                --accent-amber: #f59e0b;
                --signal-green: #10b981;
                --signal-red: #ef4444;
                --glass-border: rgba(251, 191, 36, 0.2);
            }
            body {
                background-color: var(--bg-onyx);
                color: #e2e8f0;
                font-family: 'Inter', sans-serif;
                margin: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .mono { font-family: 'JetBrains Mono', monospace; }
            
            /* Glassmorphism & Neon */
            .glass-panel {
                background: rgba(15, 23, 42, 0.65);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            }
            .gold-glow {
                box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
                border: 1px solid var(--accent-gold);
            }
            .text-gold { color: var(--accent-gold); }
            .text-emerald { color: var(--signal-green); }
            .text-crimson { color: var(--signal-red); }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: var(--bg-onyx); }
            ::-webkit-scrollbar-thumb { background: var(--accent-amber); border-radius: 3px; }

            /* Nav Buttons */
            .nav-btn {
                transition: all 0.2s ease-in-out;
                border-left: 3px solid transparent;
            }
            .nav-btn:hover {
                background: rgba(245, 158, 11, 0.1);
                border-left: 3px solid var(--accent-amber);
            }
            .nav-btn.active {
                background: rgba(245, 158, 11, 0.15);
                border-left: 3px solid var(--accent-gold);
                color: var(--accent-gold);
                font-weight: 600;
            }

            /* Content Area */
            .tab-content { display: none; height: 100%; overflow-y: auto; padding: 1.5rem; }
            .tab-content.active { display: block; animation: fadeIn 0.3s ease-in-out; }
            
            @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

            /* Sliders */
            input[type=range] {
                -webkit-appearance: none;
                width: 100%;
                background: transparent;
            }
            input[type=range]::-webkit-slider-thumb {
                -webkit-appearance: none;
                height: 16px; width: 16px;
                border-radius: 50%;
                background: var(--accent-gold);
                cursor: pointer;
                margin-top: -6px;
                box-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
            }
            input[type=range]::-webkit-slider-runnable-track {
                width: 100%; height: 4px;
                cursor: pointer;
                background: #334155;
                border-radius: 2px;
            }
        </style>
    </head>
    <body>

        <!-- TOP BAR -->
        <header class="glass-panel border-b border-gray-800 flex justify-between items-center px-6 py-3 shrink-0">
            <div class="flex items-center gap-3">
                <div class="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
                <h1 class="text-xl font-bold tracking-wider"><span class="text-gold">Y.E.S.</span> SPORTS <span class="text-xs text-gray-400 ml-2 mono">v2026.4 VECTOR ENGINE</span></h1>
            </div>
            <div id="active-game-display" class="mono text-sm bg-black/50 px-4 py-1 rounded border border-gray-700 text-gold hidden">
                NO MATCHUP SELECTED
            </div>
            <div class="flex gap-4 mono text-xs text-gray-400">
                <span id="sys-time">SYS: ONLINE</span>
                <span>ARCHIVE DB: SYNCED</span>
            </div>
        </header>

        <!-- MAIN LAYOUT -->
        <div class="flex flex-1 overflow-hidden">
            
            <!-- SIDEBAR NAV -->
            <nav class="w-56 glass-panel border-r border-gray-800 flex flex-col shrink-0 z-10">
                <div class="p-4 text-xs font-bold text-gray-500 tracking-widest">COMMAND MODULE</div>
                <button class="nav-btn active px-6 py-4 text-left text-sm" onclick="switchTab('slate')">FULL SLATE</button>
                <button class="nav-btn px-6 py-4 text-left text-sm" onclick="switchTab('matchup')">MATCHUP VECTOR</button>
                <button class="nav-btn px-6 py-4 text-left text-sm" onclick="switchTab('field')">11V11 TRENCHES</button>
                <button class="nav-btn px-6 py-4 text-left text-sm" onclick="switchTab('vegas')">VEGAS INSIDER</button>
                <button class="nav-btn px-6 py-4 text-left text-sm" onclick="switchTab('whatif')">WHAT-IF ISLAND</button>
                <button class="nav-btn px-6 py-4 text-left text-sm" onclick="switchTab('parlay')">PARLAY LAB</button>
                <button class="nav-btn px-6 py-4 text-left text-sm" onclick="switchTab('postgame')">POST GAME</button>
                <button class="nav-btn px-6 py-4 text-left text-sm border-t border-gray-800 mt-auto" onclick="switchTab('goldscript')">
                    <span class="text-gold">★ GOLD SCRIPT</span>
                </button>
            </nav>

            <!-- CONTENT AREA -->
            <main class="flex-1 relative bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]">
                
                <!-- 1. FULL SLATE -->
                <div id="tab-slate" class="tab-content active">
                    <h2 class="text-2xl font-bold mb-6">WEEKLY BOARD <span class="text-sm text-gray-400 mono">|| SELECT MATCHUP TO INITIATE VECTOR SEARCH</span></h2>
                    <div id="slate-grid" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- 2. MATCHUP VECTOR (History Repeats) -->
                <div id="tab-matchup" class="tab-content">
                    <div id="matchup-empty" class="text-center text-gray-500 mt-20 mono">SELECT A GAME FROM 'FULL SLATE' TO BEGIN VECTOR MATCHING</div>
                    <div id="matchup-data" class="hidden">
                        <div class="flex justify-between items-end border-b border-gray-700 pb-4 mb-6">
                            <div>
                                <h2 class="text-3xl font-bold text-white tracking-wider" id="mu-title">AWAY @ HOME</h2>
                                <p class="text-sm text-gray-400 mono mt-1">ARCHIVE DNA SEARCH INITIALIZED...</p>
                            </div>
                            <div class="text-right mono">
                                <div class="text-emerald font-bold text-lg" id="mu-spread">SPREAD</div>
                                <div class="text-gray-400 text-sm" id="mu-total">TOTAL</div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                            <!-- DNA Inputs -->
                            <div class="glass-panel p-5 rounded-lg border-l-4 border-l-blue-500">
                                <h3 class="text-xs font-bold text-gray-400 mb-3 tracking-widest">LIVE VECTOR INPUTS</h3>
                                <ul class="space-y-3 mono text-sm text-gray-300" id="mu-vectors">
                                    <!-- Populated by JS -->
                                </ul>
                            </div>
                            
                            <!-- Historical Matches (History Repeats) -->
                            <div class="lg:col-span-2 glass-panel p-5 rounded-lg border border-gray-700 gold-glow relative overflow-hidden">
                                <div class="absolute top-0 right-0 bg-amber-500 text-black text-[10px] font-bold px-2 py-1 rounded-bl mono">PATTERN DETECTED</div>
                                <h3 class="text-sm font-bold text-gold mb-4 tracking-widest flex items-center gap-2">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                                    HISTORY REPEATS: ARCHIVE TWINS
                                </h3>
                                <div id="mu-twins" class="space-y-4">
                                    <!-- Populated by JS -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3. 11V11 TRENCHES -->
                <div id="tab-field" class="tab-content">
                    <h2 class="text-2xl font-bold mb-6">11V11 TRENCH COMBAT <span class="text-sm text-gray-400 mono">|| OFFENSIVE LINE VS DEFENSIVE LINE</span></h2>
                    <div class="glass-panel p-6 rounded-lg border border-gray-700 flex flex-col items-center justify-center h-96">
                        <div class="text-center w-full max-w-2xl relative">
                            <!-- Visual representation of the line -->
                            <div class="flex justify-between items-center bg-gray-900 rounded p-4 border border-gray-800 mb-4">
                                <div class="text-crimson font-bold">LT<br><span class="text-xs mono">VULNERABLE</span></div>
                                <div class="text-gray-400">LG</div>
                                <div class="text-emerald font-bold border-b-2 border-emerald-500">C<br><span class="text-xs mono">ADVANTAGE</span></div>
                                <div class="text-gray-400">RG</div>
                                <div class="text-crimson font-bold">RT<br><span class="text-xs mono">INJURED</span></div>
                            </div>
                            <p class="mono text-sm text-gray-400 mb-6">Y vs MIKE Alignment detected. Edge rush simulation favors Defense +14.2% pressure rate.</p>
                            
                            <div class="grid grid-cols-2 gap-4 text-left mono text-sm">
                                <div class="bg-black/50 p-4 rounded border border-gray-800">
                                    <span class="text-gold block mb-2">O-LINE METRICS</span>
                                    Pass Block Win Rate: 58%<br>
                                    Run Block Win Rate: 72%<br>
                                    Adjusted Line Yards: 4.8
                                </div>
                                <div class="bg-black/50 p-4 rounded border border-gray-800">
                                    <span class="text-gold block mb-2">D-LINE METRICS</span>
                                    Pass Rush Win Rate: <span class="text-emerald">64%</span><br>
                                    Run Stuff Rate: 21%<br>
                                    Blitz Rate: 33%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 4. VEGAS INSIDER -->
                <div id="tab-vegas" class="tab-content">
                    <h2 class="text-2xl font-bold mb-6">MARKET ARCHITECTURE <span class="text-sm text-gray-400 mono">|| SHARP FLOW & REPRICE SIGNALS</span></h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="glass-panel p-6 rounded-lg border border-gray-700">
                            <h3 class="text-gold font-bold mb-4 mono">LINE MOVEMENT & STEAM</h3>
                            <div class="space-y-4 mono text-sm">
                                <div class="flex justify-between border-b border-gray-800 pb-2">
                                    <span>Opening Line</span> <span>-4.5</span>
                                </div>
                                <div class="flex justify-between border-b border-gray-800 pb-2">
                                    <span>Current Line</span> <span class="text-emerald">-5.5</span>
                                </div>
                                <div class="flex justify-between border-b border-gray-800 pb-2">
                                    <span>Reprice Model (RP1.0)</span> <span class="text-gold">-6.2</span>
                                </div>
                                <div class="mt-4 text-xs text-gray-400">
                                    * 1.0 pt steam move triggered at 0800 HRS. Sharp money indicating late injury leak.
                                </div>
                            </div>
                        </div>
                        <div class="glass-panel p-6 rounded-lg border border-gray-700">
                            <h3 class="text-gold font-bold mb-4 mono">MONEY SPLITS</h3>
                            <div class="w-full bg-gray-900 rounded-full h-4 mb-2 mt-6 flex overflow-hidden">
                                <div class="bg-blue-600 h-4" style="width: 22%"></div>
                                <div class="bg-emerald-500 h-4" style="width: 78%"></div>
                            </div>
                            <div class="flex justify-between text-xs mono text-gray-400 mb-6">
                                <span>PUBLIC TICKETS (22%)</span> <span>SHARP MONEY (78%)</span>
                            </div>
                            
                            <div class="w-full bg-gray-900 rounded-full h-4 mb-2 flex overflow-hidden">
                                <div class="bg-red-500 h-4" style="width: 65%"></div>
                                <div class="bg-emerald-500 h-4" style="width: 35%"></div>
                            </div>
                            <div class="flex justify-between text-xs mono text-gray-400">
                                <span>OVER TICKETS (65%)</span> <span>UNDER MONEY (35%)</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 5. WHAT-IF ISLAND -->
                <div id="tab-whatif" class="tab-content">
                    <h2 class="text-2xl font-bold mb-6">WHAT-IF ISLAND <span class="text-sm text-gray-400 mono">|| LIVE PROJECTION MANIPULATION</span></h2>
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div class="glass-panel p-6 rounded-lg border border-gray-700">
                            <h3 class="text-gold font-bold mb-6 mono">ENVIRONMENTAL VARIABLES</h3>
                            
                            <div class="mb-6">
                                <label class="flex justify-between text-sm mono text-gray-300 mb-2">
                                    <span>Weather Severity (Wind/Rain)</span> <span id="val-weather">0%</span>
                                </label>
                                <input type="range" id="slider-weather" min="0" max="100" value="0" oninput="updateWhatIf()">
                            </div>

                            <div class="mb-6">
                                <label class="flex justify-between text-sm mono text-gray-300 mb-2">
                                    <span>O-Line Injury Impact</span> <span id="val-inj">BASE</span>
                                </label>
                                <input type="range" id="slider-inj" min="0" max="100" value="0" oninput="updateWhatIf()">
                            </div>
                            
                            <div class="mb-6">
                                <label class="flex justify-between text-sm mono text-gray-300 mb-2">
                                    <span>Turnover Variance</span> <span id="val-to">0</span>
                                </label>
                                <input type="range" id="slider-to" min="-3" max="3" value="0" oninput="updateWhatIf()">
                            </div>
                        </div>

                        <div class="glass-panel p-6 rounded-lg border border-gray-700 flex flex-col justify-center items-center text-center">
                            <h3 class="text-gray-400 font-bold mb-2 mono">ADJUSTED SPREAD PROJECTION</h3>
                            <div class="text-6xl font-bold text-emerald mb-2" id="wi-spread">-5.5</div>
                            <h3 class="text-gray-400 font-bold mt-6 mb-2 mono">ADJUSTED TOTAL PROJECTION</h3>
                            <div class="text-4xl font-bold text-gold" id="wi-total">48.5</div>
                            <p class="text-xs text-gray-500 mt-6 mono">Adjusting sliders automatically recalculates the game matrix using the 2026 physics engine.</p>
                        </div>
                    </div>
                </div>

                <!-- 6. PARLAY LAB -->
                <div id="tab-parlay" class="tab-content">
                    <h2 class="text-2xl font-bold mb-6">CORRELATION LAB <span class="text-sm text-gray-400 mono">|| SGP ENGINE</span></h2>
                    <div class="glass-panel p-6 rounded-lg border border-gray-700">
                        <div class="flex items-center gap-3 mb-6">
                            <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                            <span class="mono text-sm text-gray-300">HIGH-CONFIDENCE POSITIVE CORRELATION BUILDS</span>
                        </div>
                        <div class="bg-gray-900/50 p-4 rounded border border-gray-800 mb-4 flex justify-between items-center hover:border-gold transition">
                            <div>
                                <div class="font-bold text-lg">Script Alpha</div>
                                <div class="text-sm text-gray-400 mono mt-1">Away Spread + Under + Away RB Rush Yards Over</div>
                            </div>
                            <div class="text-emerald font-bold">+420</div>
                            <button class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded text-sm mono border border-gray-600">LOAD</button>
                        </div>
                        <div class="bg-gray-900/50 p-4 rounded border border-gray-800 mb-4 flex justify-between items-center hover:border-gold transition">
                            <div>
                                <div class="font-bold text-lg">Script Beta (Negative Game Script)</div>
                                <div class="text-sm text-gray-400 mono mt-1">Home Moneyline + Away QB Pass Attempts Over + Home Team Sacks Over</div>
                            </div>
                            <div class="text-emerald font-bold">+550</div>
                            <button class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded text-sm mono border border-gray-600">LOAD</button>
                        </div>
                    </div>
                </div>

                <!-- 7. POST GAME -->
                <div id="tab-postgame" class="tab-content">
                    <h2 class="text-2xl font-bold mb-6">ARCHIVE BACKTEST <span class="text-sm text-gray-400 mono">|| SYSTEM GRADING</span></h2>
                    <div class="grid grid-cols-3 gap-4 mb-6">
                        <div class="glass-panel p-4 rounded border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 mono mb-1">YTD ROI</div>
                            <div class="text-2xl font-bold text-emerald">+14.2%</div>
                        </div>
                        <div class="glass-panel p-4 rounded border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 mono mb-1">VECTOR TWIN HIT RATE</div>
                            <div class="text-2xl font-bold text-gold">68.4%</div>
                        </div>
                        <div class="glass-panel p-4 rounded border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 mono mb-1">CLV BEAT %</div>
                            <div class="text-2xl font-bold text-white">76.1%</div>
                        </div>
                    </div>
                    <div class="glass-panel p-6 rounded-lg border border-gray-700 mono text-sm text-gray-300">
                        <table class="w-full text-left">
                            <tr class="border-b border-gray-800 text-gray-500">
                                <th class="pb-2">WEEK</th>
                                <th class="pb-2">MATCHUP</th>
                                <th class="pb-2">SYSTEM PICK</th>
                                <th class="pb-2">RESULT</th>
                                <th class="pb-2">GRADE</th>
                            </tr>
                            <tr class="border-b border-gray-800/50">
                                <td class="py-3">Wk 2</td>
                                <td>KC vs CIN</td>
                                <td>CIN +5.5</td>
                                <td>KC 26 - CIN 25</td>
                                <td class="text-emerald">WIN</td>
                            </tr>
                            <tr class="border-b border-gray-800/50">
                                <td class="py-3">Wk 2</td>
                                <td>LAR vs ARI</td>
                                <td>LAR -1.5</td>
                                <td>ARI 41 - LAR 10</td>
                                <td class="text-crimson">LOSS</td>
                            </tr>
                            <tr>
                                <td class="py-3">Wk 2</td>
                                <td>TB vs DET</td>
                                <td>TB +7.5</td>
                                <td>TB 20 - DET 16</td>
                                <td class="text-emerald">WIN</td>
                            </tr>
                        </table>
                    </div>
                </div>

                <!-- 8. GOLD SCRIPT -->
                <div id="tab-goldscript" class="tab-content">
                    <div class="flex items-center gap-4 mb-6">
                        <svg class="w-10 h-10 text-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                        <h2 class="text-3xl font-bold text-gold">GOLD SCRIPT FORECAST</h2>
                    </div>
                    
                    <div class="glass-panel p-8 rounded-lg border border-gold shadow-[0_0_20px_rgba(251,191,36,0.15)] relative">
                        <div id="gs-empty" class="text-gray-500 mono">AWAITING GAME SELECTION...</div>
                        <div id="gs-content" class="hidden">
                            <h3 class="text-xl font-bold text-white mb-4 border-b border-gray-700 pb-2">AI NARRATIVE PROJECTION</h3>
                            <p id="gs-narrative" class="text-gray-300 leading-relaxed text-lg italic mb-6">
                                <!-- Populated by JS -->
                            </p>
                            
                            <div class="grid grid-cols-4 gap-4 text-center mono text-sm mb-6">
                                <div class="bg-black/50 p-3 rounded border border-gray-800">
                                    <div class="text-gray-500 mb-1">Q1</div>
                                    <div class="font-bold text-white">LOW SCORING</div>
                                </div>
                                <div class="bg-black/50 p-3 rounded border border-gray-800">
                                    <div class="text-gray-500 mb-1">Q2</div>
                                    <div class="font-bold text-white">HOME SURGE</div>
                                </div>
                                <div class="bg-black/50 p-3 rounded border border-gray-800">
                                    <div class="text-gray-500 mb-1">Q3</div>
                                    <div class="font-bold text-white">TRENCH WAR</div>
                                </div>
                                <div class="bg-black/50 p-3 rounded border border-gray-800">
                                    <div class="text-gray-500 mb-1">Q4</div>
                                    <div class="font-bold text-gold">BACKDOOR ALERT</div>
                                </div>
                            </div>
                            
                            <div class="flex justify-between items-center bg-gray-900 p-4 rounded text-xl border-l-4 border-emerald-500">
                                <span class="font-bold text-gray-400 mono text-sm">RECOMMENDED ACTION</span>
                                <span class="font-bold text-emerald">PLAY AWAY TEAM SPREAD</span>
                            </div>
                        </div>
                    </div>
                </div>

            </main>
        </div>

        <script>
            let currentGame = null;
            let baseSpread = -5.5;
            let baseTotal = 48.5;

            // 1. Tab Switching Logic
            function switchTab(tabId) {
                // Update nav styling
                document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
                event.currentTarget.classList.add('active');

                // Update content visibility
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById('tab-' + tabId).classList.add('active');
            }

            // 2. Load Slate Data
            async function loadSlate() {
                try {
                    const response = await fetch('/api/slate');
                    const games = await response.json();
                    
                    const grid = document.getElementById('slate-grid');
                    grid.innerHTML = '';
                    
                    games.forEach(game => {
                        grid.innerHTML += `
                            <div class="glass-panel p-5 rounded-lg hover:border-gold transition cursor-pointer flex flex-col group" onclick="selectGame('${game.id}', '${game.away}', '${game.home}', '${game.spread}', '${game.total}')">
                                <div class="flex justify-between items-center mb-3">
                                    <span class="text-xs font-bold px-2 py-1 bg-gray-800 text-gray-300 rounded mono">${game.signal}</span>
                                    <span class="text-xs font-bold px-2 py-1 bg-gray-800 text-gold rounded mono">RP: ${game.reprice}</span>
                                </div>
                                <div class="text-2xl font-black mb-1 group-hover:text-gold transition">${game.away} @ ${game.home}</div>
                                <div class="text-gray-400 mono text-sm flex justify-between mt-auto pt-4 border-t border-gray-800">
                                    <span>${game.spread}</span>
                                    <span>O/U ${game.total}</span>
                                </div>
                                <button class="mt-4 w-full bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/30 py-2 rounded text-xs font-bold tracking-widest transition">
                                    INITIATE VECTOR SEARCH
                                </button>
                            </div>
                        `;
                    });
                } catch (error) {
                    console.error("Error loading slate:", error);
                }
            }

            // 3. Select Game and Load Vector Match Data
            async function selectGame(id, away, home, spread, total) {
                currentGame = id;
                baseSpread = parseFloat(spread.split(' ')[1]) || -3;
                baseTotal = parseFloat(total);

                // Update Header
                const activeDisp = document.getElementById('active-game-display');
                activeDisp.innerText = `ACTIVE VECTOR: ${away} @ ${home}`;
                activeDisp.classList.remove('hidden');

                // Reset What-If Sliders
                document.getElementById('slider-weather').value = 0;
                document.getElementById('slider-inj').value = 0;
                document.getElementById('slider-to').value = 0;
                updateWhatIf();

                try {
                    const response = await fetch(`/api/analyze/${id}`);
                    const data = await response.json();
                    
                    // Populate Matchup Tab
                    document.getElementById('matchup-empty').classList.add('hidden');
                    document.getElementById('matchup-data').classList.remove('hidden');
                    document.getElementById('mu-title').innerText = `${away} @ ${home}`;
                    document.getElementById('mu-spread').innerText = spread;
                    document.getElementById('mu-total').innerText = `O/U ${total}`;
                    
                    document.getElementById('mu-vectors').innerHTML = `
                        <li class="flex items-start gap-2"><span class="text-gray-500">TRENCH:</span> ${data.trench_adv}</li>
                        <li class="flex items-start gap-2"><span class="text-gray-500">WX:</span> ${data.weather}</li>
                        <li class="flex items-start gap-2"><span class="text-gray-500">TRAVEL:</span> ${data.travel}</li>
                        <li class="flex items-start gap-2"><span class="text-gray-500">INJ:</span> ${data.injuries}</li>
                        <li class="flex items-start gap-2"><span class="text-gray-500">COACH:</span> ${data.coaching}</li>
                    `;

                    // Populate Twins
                    const twinsDiv = document.getElementById('mu-twins');
                    twinsDiv.innerHTML = '';
                    data.twins.forEach(twin => {
                        twinsDiv.innerHTML += `
                            <div class="bg-gray-900/80 p-4 rounded border border-gray-700 border-l-4 border-l-amber-500">
                                <div class="flex justify-between items-center mb-2">
                                    <div class="font-bold text-white">${twin.year} ${twin.week} <span class="mx-2">|</span> ${twin.matchup}</div>
                                    <div class="text-emerald font-bold mono bg-emerald-900/30 px-2 py-1 rounded text-sm">${twin.sim} MATCH</div>
                                </div>
                                <p class="text-sm text-gray-400 italic">"Why it matches: ${twin.reason}"</p>
                            </div>
                        `;
                    });

                    // Populate Gold Script
                    document.getElementById('gs-empty').classList.add('hidden');
                    document.getElementById('gs-content').classList.remove('hidden');
                    document.getElementById('gs-narrative').innerText = data.gold_script;

                    // Automatically jump to Matchup tab
                    switchTab('matchup');

                } catch (error) {
                    console.error("Error loading analysis:", error);
                }
            }

            // 4. What-If Island Physics Engine (Client Side)
            function updateWhatIf() {
                if (!currentGame) return;
                
                let wx = parseInt(document.getElementById('slider-weather').value);
                let inj = parseInt(document.getElementById('slider-inj').value);
                let to = parseInt(document.getElementById('slider-to').value);

                document.getElementById('val-weather').innerText = wx + '%';
                document.getElementById('val-inj').innerText = inj > 50 ? 'SEVERE' : (inj > 20 ? 'MODERATE' : 'BASE');
                document.getElementById('val-to').innerText = (to > 0 ? '+' : '') + to;

                // Basic mock math logic to simulate spread/total movement
                let adjSpread = baseSpread;
                let adjTotal = baseTotal;

                // Weather drops total, brings spread closer to 0
                adjTotal -= (wx / 100) * 8; 
                if (adjSpread < 0) adjSpread += (wx / 100) * 2;
                else adjSpread -= (wx / 100) * 2;

                // Injuries penalize favorite (assume home/fav injury for demo)
                adjSpread += (inj / 100) * 3.5;

                // Turnovers swing spread wildly
                adjSpread -= to * 3;

                document.getElementById('wi-spread').innerText = (adjSpread > 0 ? '+' : '') + adjSpread.toFixed(1);
                document.getElementById('wi-total').innerText = adjTotal.toFixed(1);
            }

            // Initialize
            window.onload = () => {
                loadSlate();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
