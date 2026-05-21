# ============================================================
#  web.py — run this to open the dashboard in your browser
#
#  Usage:
#    python3 web.py
#  Then open: http://localhost:5000
# ============================================================

from flask import Flask, render_template_string
from opportunities import build_opportunities
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Awards Market Scanner</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #0e0f11;
    --surface:  #16181c;
    --border:   #2a2d33;
    --text:     #e8e9eb;
    --muted:    #6b7280;
    --green:    #4ade80;
    --green-bg: #052e16;
    --amber:    #fbbf24;
    --amber-bg: #1c1007;
    --blue:     #60a5fa;
    --blue-bg:  #0c1a2e;
    --red:      #f87171;
    --red-bg:   #1f0a0a;
  }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }

  header h1 {
    font-size: 1.25rem;
    font-weight: 500;
    letter-spacing: -0.01em;
  }

  header h1 span {
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--muted);
    display: block;
    margin-top: 3px;
    font-family: 'DM Mono', monospace;
  }

  .synced {
    font-size: 0.75rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
  }

  .stat-label {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 1.75rem;
    font-weight: 300;
    font-family: 'DM Mono', monospace;
  }

  .stat-value.green { color: var(--green); }
  .stat-value.amber { color: var(--amber); }
  .stat-value.blue  { color: var(--blue);  }

  .section-label {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
  }

  .cards {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
    margin-bottom: 2.5rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 1.5rem;
    transition: border-color 0.15s;
  }

  .card:hover { border-color: #3a3d45; }

  .card.strong { border-left: 3px solid var(--green); }
  .card.moderate { border-left: 3px solid var(--amber); }

  .card-show {
    font-size: 0.7rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    margin-bottom: 3px;
  }

  .card-title {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .card-nominee {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 2px;
  }

  .bars {
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 180px;
  }

  .bar-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
  }

  .bar-label {
    color: var(--muted);
    width: 42px;
    text-align: right;
  }

  .bar-track {
    flex: 1;
    height: 4px;
    background: #2a2d33;
    border-radius: 2px;
    overflow: hidden;
  }

  .bar-fill { height: 100%; border-radius: 2px; }
  .bar-fill.model  { background: var(--blue); }
  .bar-fill.kalshi { background: #4b5563; }

  .bar-pct {
    width: 32px;
    text-align: right;
    color: var(--text);
  }

  .badge {
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 6px;
    white-space: nowrap;
  }

  .badge.strong   { background: var(--green-bg); color: var(--green); }
  .badge.moderate { background: var(--amber-bg); color: var(--amber); }
  .badge.none     { background: #1a1c20;         color: var(--muted); }
  .badge.negative { background: var(--red-bg);   color: var(--red);   }

  .filters {
    display: flex;
    gap: 6px;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .filter {
    font-size: 0.75rem;
    padding: 5px 14px;
    border: 1px solid var(--border);
    border-radius: 20px;
    background: none;
    color: var(--muted);
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.15s;
  }

  .filter:hover, .filter.active {
    border-color: var(--text);
    color: var(--text);
  }

  .legend {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1rem;
    font-size: 0.7rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    align-items: center;
  }

  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-dot  { width: 8px; height: 8px; border-radius: 2px; }

  .refresh-btn {
    font-size: 0.75rem;
    padding: 6px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: none;
    color: var(--muted);
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.15s;
  }

  .refresh-btn:hover { color: var(--text); border-color: #3a3d45; }

  .no-edge {
    text-align: center;
    padding: 3rem;
    color: var(--muted);
    font-size: 0.85rem;
    border: 1px dashed var(--border);
    border-radius: 10px;
  }

  .conf-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    margin-right: 4px;
    vertical-align: middle;
  }
  .conf-dot.high   { background: var(--green); }
  .conf-dot.medium { background: var(--amber); }
  .conf-dot.low    { background: var(--muted); }

  @media (max-width: 700px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
    .card  { grid-template-columns: 1fr; }
    .bars  { min-width: unset; }
  }
</style>
</head>
<body>

<header>
  <h1>
    Awards market scanner
    <span>Kalshi arbitrage · Oscars · Emmys · Grammys · Golden Globes</span>
  </h1>
  <div style="display:flex;align-items:center;gap:1rem;">
    <span class="synced">synced {{ synced }}</span>
    <button class="refresh-btn" onclick="location.reload()">↻ Refresh</button>
  </div>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-label">Markets tracked</div>
    <div class="stat-value blue">{{ total }}</div>
  </div>
  <div class="stat">
    <div class="stat-label">Strong edges (≥15%)</div>
    <div class="stat-value green">{{ strong }}</div>
  </div>
  <div class="stat">
    <div class="stat-label">Moderate edges (8–14%)</div>
    <div class="stat-value amber">{{ moderate }}</div>
  </div>
  <div class="stat">
    <div class="stat-label">Avg edge (flagged)</div>
    <div class="stat-value {% if avg_edge > 0 %}green{% else %}amber{% endif %}">
      {% if avg_edge > 0 %}+{% endif %}{{ avg_edge }}%
    </div>
  </div>
</div>

<div class="filters">
  <button class="filter active" onclick="filterCards('all', this)">All shows</button>
  <button class="filter" onclick="filterCards('Oscars', this)">Oscars</button>
  <button class="filter" onclick="filterCards('Emmys', this)">Emmys</button>
  <button class="filter" onclick="filterCards('Grammys', this)">Grammys</button>
  <button class="filter" onclick="filterCards('Golden Globes', this)">Golden Globes</button>
  <button class="filter" onclick="filterCards('flagged', this)">Edges only</button>
</div>

<div class="legend">
  <span class="legend-item"><span class="legend-dot" style="background:var(--blue)"></span>Model prob</span>
  <span class="legend-item"><span class="legend-dot" style="background:#4b5563"></span>Kalshi odds</span>
  <span class="legend-item"><span class="conf-dot high"></span>High confidence</span>
  <span class="legend-item"><span class="conf-dot medium"></span>Medium confidence</span>
  <span class="legend-item"><span class="conf-dot low"></span>Low confidence</span>
</div>

<div class="section-label">All tracked markets — click a card to see signal breakdown</div>

<div class="cards" id="cards">
  {% for o in opportunities %}
  {% set edge = o.edge %}
  {% if edge >= 15 %}{% set tier = "strong" %}
  {% elif edge >= 8 %}{% set tier = "moderate" %}
  {% elif edge < 0 %}{% set tier = "negative" %}
  {% else %}{% set tier = "none" %}{% endif %}

  <div class="card {{ tier if edge >= 8 else '' }}"
       data-show="{{ o.show }}"
       data-flagged="{{ 'true' if o.flagged else 'false' }}"
       onclick="toggleDetail(this, {{ loop.index0 }})">

    <div>
      <div class="card-show">{{ o.show }} · {{ o.category }}</div>
      <div class="card-title">{{ o.nominee }}</div>
      <div class="card-nominee">
        <span class="conf-dot {{ o.confidence }}"></span>
        {{ o.confidence }} confidence · {{ o.signals_used }} signals
      </div>
    </div>

    <div class="bars">
      <div class="bar-row">
        <span class="bar-label">model</span>
        <div class="bar-track"><div class="bar-fill model" style="width:{{ o.model_prob }}%"></div></div>
        <span class="bar-pct">{{ o.model_prob }}%</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">kalshi</span>
        <div class="bar-track"><div class="bar-fill kalshi" style="width:{{ o.kalshi_prob }}%"></div></div>
        <span class="bar-pct">{{ o.kalshi_prob }}%</span>
      </div>
    </div>

    <span class="badge {{ tier }}">
      {% if edge >= 0 %}+{% endif %}{{ edge }}%
      {% if edge >= 15 %} ★{% elif edge >= 8 %} ◆{% endif %}
    </span>
  </div>

  <!-- Detail drawer -->
  <div id="detail-{{ loop.index0 }}" style="display:none;background:#12141a;border:1px solid var(--border);border-radius:10px;padding:1.25rem;margin-top:-8px;margin-bottom:4px;">
    <div style="font-size:0.7rem;color:var(--muted);margin-bottom:0.75rem;text-transform:uppercase;letter-spacing:0.08em;">Signal breakdown</div>
    <table style="width:100%;font-size:0.8rem;border-collapse:collapse;">
      {% for key, s in o.signal_breakdown.items() %}
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:7px 0;color:var(--muted);font-family:'DM Mono',monospace;">{{ key }}</td>
        <td style="padding:7px 0;text-align:center;">
          <div style="width:80px;height:4px;background:#2a2d33;border-radius:2px;display:inline-block;vertical-align:middle;">
            <div style="width:{{ (s.raw_signal * 100)|int }}%;height:100%;background:var(--blue);border-radius:2px;"></div>
          </div>
        </td>
        <td style="padding:7px 0;text-align:right;font-family:'DM Mono',monospace;">{{ s.raw_signal }}</td>
        <td style="padding:7px 0;text-align:right;color:var(--muted);font-size:0.7rem;padding-left:12px;">wt {{ "%.0f"|format(s.weight * 100) }}%</td>
        <td style="padding:7px 0;text-align:right;font-family:'DM Mono',monospace;color:var(--green);">+{{ s.contribution }}pp</td>
      </tr>
      {% endfor %}
    </table>
    <div style="margin-top:1rem;padding:0.75rem 1rem;background:var(--surface);border-radius:8px;font-size:0.8rem;">
      <span style="color:var(--muted);">Recommendation: </span>
      {% if o.edge >= 15 %}
        Buy YES at {{ o.kalshi_prob }}¢ — strong edge, {{ o.confidence }} confidence.
      {% elif o.edge >= 8 %}
        Consider YES at {{ o.kalshi_prob }}¢ — moderate edge. Watch for more signals.
      {% elif o.edge < 0 %}
        No edge — Kalshi may be overpriced. Avoid or consider NO.
      {% else %}
        Edge below threshold — skip after fees.
      {% endif %}
    </div>
  </div>
  {% endfor %}
</div>

<script>
function toggleDetail(card, idx) {
  const d = document.getElementById('detail-' + idx);
  d.style.display = d.style.display === 'none' ? 'block' : 'none';
}

function filterCards(show, btn) {
  document.querySelectorAll('.filter').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.querySelectorAll('.card, [id^="detail-"]').forEach(el => {
    el.style.display = '';
  });

  if (show === 'all') return;

  document.querySelectorAll('.card').forEach((card, i) => {
    const cardShow    = card.dataset.show;
    const cardFlagged = card.dataset.flagged === 'true';
    const detail      = document.getElementById('detail-' + i);

    const visible = show === 'flagged' ? cardFlagged : cardShow === show;
    card.style.display   = visible ? '' : 'none';
    if (detail) detail.style.display = 'none';
  });
}
</script>

</body>
</html>
"""


@app.route("/")
def index():
    opportunities = build_opportunities()

    flagged  = [o for o in opportunities if o["flagged"]]
    strong   = sum(1 for o in opportunities if o["edge"] >= 15)
    moderate = sum(1 for o in opportunities if 8 <= o["edge"] < 15)
    avg_edge = round(
        sum(o["edge"] for o in flagged) / len(flagged), 1
    ) if flagged else 0

    return render_template_string(
        HTML,
        opportunities=opportunities,
        total=len(opportunities),
        strong=strong,
        moderate=moderate,
        avg_edge=avg_edge,
        synced=datetime.now().strftime("%H:%M:%S"),
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        print("\n  Awards Market Scanner")
        print("  ─────────────────────────────────────────")
        print("  Open your browser and go to:")
        print("  http://localhost:5000")
        print("\n  Press Ctrl+C to stop the server.\n")
    app.run(debug=False, host="0.0.0.0", port=port)
