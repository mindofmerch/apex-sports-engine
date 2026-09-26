import os
import time
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="Y.E.S. Sports Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HARDCODED FULL SLATE DATA (WEEK SNAPSHOT) ---
# This ensures your specific 16 games and insights load perfectly 
# even if the live odds API fails or hasn't updated yet.
FALLBACK_SLATE = [
    {"signal": 15, "matchup": "DET vs BUF", "spread": "DET +5.5", "total": "54.5", "open": "DET +4.5", "tickets": "Not loaded", "type": "RP1.0", "insight": "DET vs BUF: a 1.0-point reprice from open now sits at DET +5.5. The move needs a football explanation; first test RT vs EDGE."},
    {"signal": 26, "matchup": "PHI vs TEN", "spread": "PHI -7", "total": "39.5", "open": "PHI -7", "tickets": "Not loaded", "type": "BASE", "insight": "PHI vs TEN: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 20, "matchup": "PIT vs NE", "spread": "PIT +5.5", "total": "41.5", "open": "PIT +5.5", "tickets": "Not loaded", "type": "BASE", "insight": "PIT vs NE: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 15, "matchup": "MIN vs CHI", "spread": "MIN +4.5", "total": "48.5", "open": "MIN +5.5", "tickets": "Not loaded", "type": "RP1.0", "insight": "MIN vs CHI: a 1.0-point reprice from open now sits at MIN +4.5. The move needs a football explanation; first test RT vs EDGE."},
    {"signal": 26, "matchup": "CAR vs ATL", "spread": "CAR -2.5", "total": "43.5", "open": "CAR -1.5", "tickets": "Not loaded", "type": "RP1.0", "insight": "CAR vs ATL: a 1.0-point reprice from open now sits at CAR -2.5. The move needs a football explanation; first test RT vs EDGE."},
    {"signal": 26, "matchup": "GB vs NYJ", "spread": "GB -3.5", "total": "44.5", "open": "GB -4.5", "tickets": "Not loaded", "type": "RP1.0", "insight": "GB vs NYJ: a 1.0-point reprice from open now sits at GB -3.5. The move needs a football explanation; first test RT vs EDGE."},
    {"signal": 15, "matchup": "NO vs BAL", "spread": "NO +8.5", "total": "46.5", "open": "NO +8.5", "tickets": "Not loaded", "type": "BASE", "insight": "NO vs BAL: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 21, "matchup": "CIN vs HOU", "spread": "CIN +2.5", "total": "46.5", "open": "CIN +3", "tickets": "Not loaded", "type": "BASE", "insight": "CIN vs HOU: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 20, "matchup": "CLE vs TB", "spread": "CLE +8.5", "total": "41.5", "open": "CLE +8.5", "tickets": "Not loaded", "type": "BASE", "insight": "CLE vs TB: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 21, "matchup": "JAX vs DEN", "spread": "JAX +2.5", "total": "45.5", "open": "JAX +2.5", "tickets": "Not loaded", "type": "BASE", "insight": "JAX vs DEN: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 26, "matchup": "LV vs LAC", "spread": "LV +6.5", "total": "43.5", "open": "LV +7", "tickets": "Not loaded", "type": "BASE", "insight": "LV vs LAC: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 26, "matchup": "SEA vs ARI", "spread": "SEA -3.5", "total": "41.5", "open": "SEA -4.5", "tickets": "Not loaded", "type": "RP1.0", "insight": "SEA vs ARI: a 1.0-point reprice from open now sits at SEA -3.5. The move needs a football explanation; first test RT vs EDGE."},
    {"signal": 20, "matchup": "MIA vs SF", "spread": "MIA +13.5", "total": "44.5", "open": "MIA +13.5", "tickets": "Not loaded", "type": "BASE", "insight": "MIA vs SF: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 15, "matchup": "WAS vs DAL", "spread": "WAS +4.5", "total": "50.5", "open": "WAS +3.5", "tickets": "Not loaded", "type": "RP1.0", "insight": "WAS vs DAL: a 1.0-point reprice from open now sits at WAS +4.5. The move needs a football explanation; first test RT vs EDGE."},
    {"signal": 21, "matchup": "IND vs KC", "spread": "IND +6.5", "total": "46.5", "open": "IND +6.5", "tickets": "Not loaded", "type": "BASE", "insight": "IND vs KC: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."},
    {"signal": 21, "matchup": "NYG vs LAR", "spread": "NYG +7", "total": "48.5", "open": "NYG +7", "tickets": "Not loaded", "type": "BASE", "insight": "NYG vs LAR: no clean market contradiction. Let Y vs MIKE (green) and RT vs EDGE (red) decide whether the saved price deserves trust."}
]

@app.get("/api/nfl/slate")
def get_slate():
    # In a live scenario, you would fetch from odds api here. 
    # For this week, we return the precise requested analytical snapshot.
    return {"success": True, "slate": FALLBACK_SLATE}

# --- WORLD-CLASS ANALYTICS TERMINAL FRONTEND ---
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Y.E.S. SPORTS | Terminal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #050505;
            --bg-panel: #111111;
            --bg-card: #18181b;
            --border-dim: #27272a;
            --accent: #f59e0b; /* Amber */
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
        }
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: var(--bg-base); 
            color: var(--text-main); 
        }
        .mono { font-family: 'JetBrains Mono', monospace; }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-base); }
        ::-webkit-scrollbar-thumb { background: var(--border-dim); border-radius: 4px; }
        
        .terminal-nav-btn {
            color: var(--text-dim);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            padding: 0.5rem 1rem;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        .terminal-nav-btn:hover { color: white; }
        .terminal-nav-btn.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }
        
        .data-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-dim);
            border-radius: 6px;
            transition: border-color 0.2s ease;
        }
        .data-card:hover { border-color: #3f3f46; }
        
        .stat-box { background-color: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); }
        
        .text-hl-green { color: #10b981; font-weight: 600; }
        .text-hl-red { color: #ef4444; font-weight: 600; }
    </style>
</head>
<body class="min-h-screen flex flex-col antialiased">

    <!-- TOP BAR -->
    <header class="w-full border-b border-zinc-800 bg-zinc-950/95 sticky top-0 z-50">
        <div class="px-4 py-3 flex flex-col md:flex-row md:items-end justify-between gap-2">
            <div>
                <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                    Y.E.S. SPORTS
                </h1>
                <p class="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mt-1">
                    See the game &middot; read the price &middot; test the story
                </p>
            </div>
            
            <!-- NAVIGATION -->
            <div class="flex items-center overflow-x-auto scrollbar-none gap-1 mt-2 md:mt-0 pb-1">
                <button class="terminal-nav-btn">MATCHUP</button>
                <button class="terminal-nav-btn">11V11 FIELD</button>
                <button class="terminal-nav-btn">VEGAS INSIDER</button>
                <button class="terminal-nav-btn">WHAT-IF ISLAND</button>
                <button class="terminal-nav-btn">PARLAY LAB</button>
                <button class="terminal-nav-btn active">FULL SLATE</button>
                <button class="terminal-nav-btn">POST GAME</button>
                <button class="terminal-nav-btn">GOLD SCRIPT</button>
                <button class="terminal-nav-btn text-zinc-600 ml-4 hover:text-white flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path></svg>
                    SHARE
                </button>
            </div>
        </div>
    </header>

    <!-- MAIN DASHBOARD CONTENT -->
    <main class="flex-grow p-4 md:p-6 lg:p-8 w-full max-w-[1600px] mx-auto">
        
        <!-- FULL SLATE HEADER -->
        <div class="mb-8 border-l-2 border-amber-500 pl-4">
            <h2 class="text-xl md:text-2xl font-black text-white uppercase tracking-tight">Full Slate</h2>
            <p class="text-sm text-zinc-400 mt-1 font-medium">All 16 games. One research board.</p>
            <p class="text-xs text-zinc-500 mt-1">Open any matchup and it carries into the field, Vegas Insider, What‑If Island and Parlay Lab.</p>
        </div>

        <!-- SLATE GRID (INJECTED VIA JS) -->
        <div id="slate-container" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
            <!-- Loading State -->
            <div class="text-zinc-500 text-sm mono animate-pulse">Initializing market data...</div>
        </div>

    </main>

    <script>
        // Formats insight text to highlight key tactical metrics
        function formatInsight(text) {
            let formatted = text.replace(/Y vs MIKE \(green\)/g, '<span class="text-hl-green">Y vs MIKE (green)</span>');
            formatted = formatted.replace(/RT vs EDGE \(red\)/g, '<span class="text-hl-red">RT vs EDGE (red)</span>');
            return formatted;
        }

        async function loadSlate() {
            const container = document.getElementById('slate-container');
            try {
                const res = await fetch('/api/nfl/slate');
                const data = await res.json();
                
                container.innerHTML = data.slate.map(g => `
                    <div class="data-card flex flex-col relative overflow-hidden group">
                        
                        <!-- Top Bar: Signal & Teams -->
                        <div class="flex justify-between items-start p-4 border-b border-zinc-800">
                            <div>
                                <div class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Signal ${g.signal}</div>
                                <h3 class="text-xl font-black text-white tracking-tight">${g.matchup}</h3>
                            </div>
                            <button class="opacity-0 group-hover:opacity-100 transition text-zinc-500 hover:text-white">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                            </button>
                        </div>

                        <!-- Main Odds Grid -->
                        <div class="grid grid-cols-2 gap-px bg-zinc-800 border-b border-zinc-800">
                            <div class="p-3 bg-zinc-900/80 hover:bg-zinc-800 transition">
                                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Spread &middot; Snapshot</div>
                                <div class="text-base font-bold text-white mono mt-0.5">${g.spread}</div>
                            </div>
                            <div class="p-3 bg-zinc-900/80 hover:bg-zinc-800 transition">
                                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Total</div>
                                <div class="text-base font-bold text-white mono mt-0.5">${g.total}</div>
                            </div>
                            <div class="p-3 bg-zinc-900/80 hover:bg-zinc-800 transition">
                                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Open</div>
                                <div class="text-sm font-semibold text-zinc-300 mono mt-0.5">${g.open}</div>
                            </div>
                            <div class="p-3 bg-zinc-900/80 hover:bg-zinc-800 transition">
                                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Public Tickets</div>
                                <div class="text-sm font-semibold text-zinc-500 mono mt-0.5">${g.tickets}</div>
                            </div>
                        </div>

                        <!-- Insight Footer -->
                        <div class="p-4 bg-zinc-900/30 flex-grow">
                            <p class="text-xs text-zinc-400 leading-relaxed font-medium">
                                <span class="text-white font-bold">${g.type}</span> &middot; ${formatInsight(g.insight)}
                            </p>
                        </div>
                    </div>
                `).join('');
            } catch(e) { 
                container.innerHTML = '<div class="text-red-500 text-sm p-4 border border-red-500/20 bg-red-500/10 rounded">SYSTEM ERROR: Failed to load market snapshot. Check backend connectivity.</div>'; 
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', loadSlate);
    </script>
</body>
</html>
"""
