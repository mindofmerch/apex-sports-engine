tion>`: `<div class="card"><div class="empty">No verified player opportunity or touchdown prop data released for this game yet.<br><small class="muted">Props remain gated until official starting rosters and inactives freeze.</small></div></div>`);
}

async function loadPostgame(id){
  const g=GAMES.find(x=>x.id===id);
  if(!g) return null;
  if(state.postgame[id]) return state.postgame[id];
  try {
    const data = await fetchJSON(POSTGAME, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({away:g.a, home:g.h, season:YEAR, week:state.week})
    });
    state.postgame[id] = data;
    return data;
  } catch(e) {
    return null;
  }
}

async function pageLearning(b){
  const g=game(), pg=await loadPostgame(state.game);
  const p=projection(b);
  return hero('LEARNING LAB',g.a+' at '+g.h,'Postgame review, model calibration, Brier score verification and feedback loops.') +
  `<div class="two-col">
    <div class="stack">
      <section class="card blueline">
        <h3>Model Calibration & Postgame Review</h3>
        <p>${esc(pg?.summary || 'Postgame review becomes active after game completion and official stat lock. Evaluates score variance, closing line value (CLV), and structural accuracy.')}</p>
        <div class="grid g3" style="margin-top:10px">
          ${metric('MODEL PROJECTION', fx(p.away_score,1)+' - '+fx(p.home_score,1))}
          ${metric('ACTUAL SCORE', pg?.actual_score ? pg.actual_score.away+' - '+pg.actual_score.home : 'PENDING')}
          ${metric('ERROR / DELTA', pg?.delta ? fx(pg.delta,1)+' pts' : '—')}
        </div>
      </section>
      <section class="card">
        <h3>Structural Insights & Feedback Loop</h3>
        <p>${esc(pg?.feedback || 'The Learning Lab automatically updates state weights and neighbor distances when final box scores are ingested.')}</p>
      </section>
    </div>
    <div class="stack">
      <section class="card">
        <h3>Accuracy Metrics</h3>
        <div class="kv"><span>CLV Differential</span><b>${fx(pg?.clv_diff,2) || '—'}</b></div>
        <div class="kv"><span>Spread Accuracy</span><b>${pg?.spread_hit ? 'HIT' : 'PENDING'}</b></div>
        <div class="kv"><span>Total Accuracy</span><b>${pg?.total_hit ? 'HIT' : 'PENDING'}</b></div>
        <div class="kv"><span>Brier Score</span><b>${fx(pg?.brier_score,4) || '—'}</b></div>
      </section>
    </div>
  </div>`;
}

function pageSources(b){
  const g=game(), r=b.readiness||{}, cg=b.canonical_game||{}, meta=cg.meta||{};
  const sources = b.sources || b.data_sources || [
    { name: 'Official NFL Feed / NextGen Stats', status: 'ACTIVE', type: 'Play-by-play, EPA, personnel tracking' },
    { name: 'Market Odds Consolidation', status: 'ACTIVE', type: 'Spreads, totals, consensus odds' },
    { name: 'Weather & Stadium Environment', status: 'VERIFIED', type: 'Temperature, wind, roof status, precipitation' },
    { name: 'Injury & Inactives Monitor', status: r.checks?.final_inactives ? 'LOCKED' : 'MONITORING', type: 'Game-day inactives, starter designations' }
  ];
  return hero('SOURCES & VERIFICATION', g.a+' at '+g.h, 'Data lineage, freeze cutoff times, and primary verification feeds.') +
  `<div class="grid g2">
    <section class="card blueline">
      <h3>Active Ingestion Feeds</h3>
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>SOURCE</th><th>STATUS</th><th>TYPE</th></tr></thead>
          <tbody>
            ${sources.map(s=>`<tr><td><b>${esc(s.name)}</b></td><td><span class="pill ${s.status==='LOCKED'?'green':s.status==='VERIFIED'?'blue':'yellow'}">${esc(s.status)}</span></td><td>${esc(s.type)}</td></tr>`).join('')}
          </tbody>
        </table>
      </div>
    </section>
    <section class="card yellowline">
      <h3>Verification Audit Trail</h3>
      <div class="kv"><span>Source Cutoff Time</span><b>${esc(r.source_cutoff || 'T-60m Pregame Lock')}</b></div>
      <div class="kv"><span>Readiness Score</span><b>${esc(r.score ?? '—')}/100</b></div>
      <div class="kv"><span>State Hash</span><b class="code">${esc(b.stateHash || meta.state_hash || '—')}</b></div>
      <div class="kv"><span>Pregame Lock Hash</span><b class="code">${esc(meta.pregame_lock_hash || 'UNLOCKED')}</b></div>
      <div class="kv"><span>Public Endpoint</span><b class="code">${esc(ONE)}</b></div>
    </section>
  </div>`;
}

async function render(){
  const app = $('#app');
  nav();
  try {
    if (state.page === 'market') {
      app.innerHTML = '<div class="empty"><div class="spinner"></div>Loading Market Board…</div>';
      app.innerHTML = await pageMarket();
      app.querySelectorAll('.click-row').forEach(row => {
        row.onclick = () => {
          const gid = row.dataset.game;
          if (gid) {
            state.game = gid;
            localStorage.setItem('yes-game', gid);
            $('#gameSelect').value = gid;
            state.page = 'decision';
            localStorage.setItem('yes-page', state.page);
            render();
          }
        };
      });
      return;
    }

    if (state.page === 'parlay') {
      app.innerHTML = '<div class="empty"><div class="spinner"></div>Loading Parlay Lab…</div>';
      const [b, pd] = await Promise.all([
        loadOne(state.game),
        loadParlay()
      ]);
      app.innerHTML = pageParlay(b, pd);
      
      const mix = $('#mixBtn');
      if (mix) {
        mix.onclick = () => {
          state.parlayNonce++;
          state.parlay = null;
          toast('Refreshing parlay combinations...');
          render();
        };
      }
      
      app.querySelectorAll('[data-ptab]').forEach(btn => {
        btn.onclick = () => {
          state.parlayTab = btn.dataset.ptab;
          render();
        };
      });
      
      const stakeInput = $('#stake');
      if (stakeInput) {
        stakeInput.oninput = (e) => {
          state.stake = Number(e.target.value) || 0;
          const pBox = $('#payoutBox');
          if (pBox) {
            const legs = Array.isArray(pd?.tickets?.[state.parlayTab]) ? pd.tickets[state.parlayTab] : [];
            pBox.innerHTML = payoutHTML(legs, state.stake);
          }
        };
      }
      return;
    }

    app.innerHTML = '<div class="empty"><div class="spinner"></div>Loading One Brain data for ' + state.game + '…</div>';
    const b = await loadOne(state.game);
    
    if (state.page === 'decision') app.innerHTML = pageDecision(b);
    else if (state.page === 'match') app.innerHTML = pageMatch(b);
    else if (state.page === 'gold') app.innerHTML = pageGold(b);
    else if (state.page === 'props') app.innerHTML = pageProps(b);
    else if (state.page === 'play') app.innerHTML = pagePlay(b);
    else if (state.page === 'matrix') app.innerHTML = pageMatrix(b);
    else if (state.page === 'learning') app.innerHTML = await pageLearning(b);
    else if (state.page === 'sources') app.innerHTML = pageSources(b);
    else app.innerHTML = pageDecision(b);

  } catch(err) {
    console.error(err);
    app.innerHTML = `<div class="card redline"><h3>Error Loading Data</h3><p class="bad">${esc(err.message)}</p><button class="btn" onclick="state.cache={};render()">Retry</button></div>`;
  }
}

setup();
loadOne(state.game, true).then(render).catch(() => render());
})();
</script>
</body>
</html>
