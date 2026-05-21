# ============================================================
#  opportunities.py — all scraper + model + edge logic in one file
#  (flattened for simple cloud deployment)
# ============================================================

import requests
from config import SIGNAL_WEIGHTS, SHOW_CONFIDENCE, EDGE_THRESHOLD, KALSHI_API_KEY

# ── Demo market data (used when no API key is set) ───────────
DEMO_MARKETS = [
    {"id": "OSCAR-BESTPIC-BRUTALIST",   "show": "Oscars",        "category": "Best Picture",           "nominee": "The Brutalist",               "kalshi_prob": 44},
    {"id": "OSCAR-BESTACT-BRODY",       "show": "Oscars",        "category": "Best Actor",              "nominee": "Adrien Brody",                "kalshi_prob": 58},
    {"id": "OSCAR-BESTDIR-CORBET",      "show": "Oscars",        "category": "Best Director",           "nominee": "Brady Corbet",                "kalshi_prob": 51},
    {"id": "OSCAR-BESTACT-MOORE",       "show": "Oscars",        "category": "Best Actress",            "nominee": "Demi Moore",                  "kalshi_prob": 52},
    {"id": "OSCAR-INTLFILM-EMILIA",     "show": "Oscars",        "category": "Best Intl. Film",         "nominee": "Emilia Pérez",                "kalshi_prob": 49},
    {"id": "EMMY-DRAMA-JACKAL",         "show": "Emmys",         "category": "Best Drama Series",       "nominee": "The Day of the Jackal",       "kalshi_prob": 28},
    {"id": "EMMY-COMEDY-BEAR",          "show": "Emmys",         "category": "Best Comedy Series",      "nominee": "The Bear",                    "kalshi_prob": 61},
    {"id": "EMMY-LIMITED-DISCLAIMER",   "show": "Emmys",         "category": "Best Limited Series",     "nominee": "Disclaimer",                  "kalshi_prob": 31},
    {"id": "GRAMMY-AOTY-BEYONCE",       "show": "Grammys",       "category": "Album of the Year",       "nominee": "Beyoncé – Cowboy Carter",     "kalshi_prob": 47},
    {"id": "GRAMMY-ROTY-KENDRICK",      "show": "Grammys",       "category": "Record of the Year",      "nominee": "Kendrick Lamar – Not Like Us","kalshi_prob": 41},
    {"id": "GLOBE-DRAMA-CONCLAVE",      "show": "Golden Globes", "category": "Best Picture – Drama",    "nominee": "Conclave",                    "kalshi_prob": 35},
    {"id": "GLOBE-TVSERIES-SHOGUN",     "show": "Golden Globes", "category": "Best TV Series – Drama",  "nominee": "Shōgun",                      "kalshi_prob": 68},
]

# ── Precursor data ────────────────────────────────────────────
PRECURSOR_DATA = {
    "The Brutalist":               {"show": "Oscars",        "category": "Best Picture",           "sag_win": False, "bafta_win": True,  "critics_choice": True,  "guild_noms": 3, "rt_score": 89,   "social_volume": 0.72},
    "Adrien Brody":                {"show": "Oscars",        "category": "Best Actor",              "sag_win": True,  "bafta_win": True,  "critics_choice": True,  "guild_noms": 0, "rt_score": None, "social_volume": 0.65},
    "Brady Corbet":                {"show": "Oscars",        "category": "Best Director",           "sag_win": None,  "bafta_win": False, "critics_choice": False, "guild_noms": 2, "rt_score": 89,   "social_volume": 0.55},
    "Demi Moore":                  {"show": "Oscars",        "category": "Best Actress",            "sag_win": True,  "bafta_win": False, "critics_choice": True,  "guild_noms": 0, "rt_score": None, "social_volume": 0.48},
    "Emilia Pérez":                {"show": "Oscars",        "category": "Best Intl. Film",         "sag_win": None,  "bafta_win": True,  "critics_choice": True,  "guild_noms": 1, "rt_score": 79,   "social_volume": 0.60},
    "The Day of the Jackal":       {"show": "Emmys",         "category": "Best Drama Series",       "sag_win": False, "bafta_win": None,  "critics_choice": False, "guild_noms": 2, "rt_score": 93,   "social_volume": 0.58},
    "The Bear":                    {"show": "Emmys",         "category": "Best Comedy Series",      "sag_win": True,  "bafta_win": None,  "critics_choice": True,  "guild_noms": 3, "rt_score": 98,   "social_volume": 0.80},
    "Disclaimer":                  {"show": "Emmys",         "category": "Best Limited Series",     "sag_win": False, "bafta_win": None,  "critics_choice": False, "guild_noms": 2, "rt_score": 94,   "social_volume": 0.52},
    "Beyoncé – Cowboy Carter":     {"show": "Grammys",       "category": "Album of the Year",       "sag_win": None,  "bafta_win": None,  "critics_choice": None,  "guild_noms": 0, "rt_score": None, "social_volume": 0.88, "metascore": 90},
    "Kendrick Lamar – Not Like Us":{"show": "Grammys",       "category": "Record of the Year",      "sag_win": None,  "bafta_win": None,  "critics_choice": None,  "guild_noms": 0, "rt_score": None, "social_volume": 0.95},
    "Conclave":                    {"show": "Golden Globes", "category": "Best Picture – Drama",    "sag_win": False, "bafta_win": False, "critics_choice": True,  "guild_noms": 2, "rt_score": 92,   "social_volume": 0.62},
    "Shōgun":                      {"show": "Golden Globes", "category": "Best TV Series – Drama",  "sag_win": True,  "bafta_win": None,  "critics_choice": True,  "guild_noms": 3, "rt_score": 99,   "social_volume": 0.75},
}

# ── Signal converters ─────────────────────────────────────────
def bool_to_signal(v):
    if v is True:  return 1.0
    if v is False: return 0.25
    return None

def rt_to_signal(s):
    if s is None: return None
    if s >= 95: return 1.0
    if s >= 90: return 0.85
    if s >= 80: return 0.70
    if s >= 70: return 0.55
    return 0.30

def guild_to_signal(n):
    if n is None: return None
    if n >= 4: return 1.0
    if n >= 3: return 0.85
    if n >= 2: return 0.70
    if n >= 1: return 0.50
    return 0.20

# ── Model ─────────────────────────────────────────────────────
def calculate_model_probability(signals):
    show = signals.get("show", "Oscars")
    conf_mult = SHOW_CONFIDENCE.get(show, 1.0)

    raw = {
        "sag_win":        bool_to_signal(signals.get("sag_win")),
        "bafta_win":      bool_to_signal(signals.get("bafta_win")),
        "critics_choice": bool_to_signal(signals.get("critics_choice")),
        "guild_noms":     guild_to_signal(signals.get("guild_noms")),
        "rt_score":       rt_to_signal(signals.get("rt_score") or signals.get("metascore")),
        "social_volume":  signals.get("social_volume"),
    }

    available = {k: v for k, v in raw.items() if v is not None}
    if not available:
        return {"probability": 50.0, "confidence": "low", "signal_breakdown": {}, "signals_used": 0}

    total_w = sum(SIGNAL_WEIGHTS[k] for k in available)
    breakdown, weighted_sum = {}, 0.0
    for k, strength in available.items():
        w = SIGNAL_WEIGHTS[k] / total_w
        contrib = w * strength
        weighted_sum += contrib
        breakdown[k] = {"raw_signal": round(strength, 2), "weight": round(w, 3), "contribution": round(contrib * 100, 1)}

    squeezed = 0.05 + weighted_sum * 0.90
    dampened = 0.5 + (squeezed - 0.5) * conf_mult
    n = len(available)
    confidence = "high" if n >= 4 else "medium" if n >= 2 else "low"

    return {"probability": round(dampened * 100, 1), "confidence": confidence,
            "signal_breakdown": breakdown, "signals_used": n}

# ── Kalshi fetch ──────────────────────────────────────────────
def fetch_all_award_markets():
    if KALSHI_API_KEY is None:
        return DEMO_MARKETS
    # Live fetch would go here — falls back to demo for now
    return DEMO_MARKETS

# ── Opportunity builder ───────────────────────────────────────
def build_opportunities():
    kalshi_markets = fetch_all_award_markets()

    opps = []
    for name, signals in PRECURSOR_DATA.items():
        result = calculate_model_probability(signals)
        model_prob = result["probability"]

        match = next((m for m in kalshi_markets if m.get("nominee") == name), None)
        if not match:
            continue

        edge = round(model_prob - match["kalshi_prob"], 1)
        opps.append({
            "nominee":          name,
            "show":             signals["show"],
            "category":         signals["category"],
            "model_prob":       model_prob,
            "kalshi_prob":      match["kalshi_prob"],
            "edge":             edge,
            "confidence":       result["confidence"],
            "signals_used":     result["signals_used"],
            "signal_breakdown": result["signal_breakdown"],
            "flagged":          edge >= EDGE_THRESHOLD,
        })

    opps.sort(key=lambda x: (-int(x["flagged"]), -x["edge"]))
    return opps

def format_edge_label(edge):
    sign = "+" if edge >= 0 else ""
    if edge >= 15: return f"{sign}{edge}%  ★ STRONG EDGE"
    if edge >= 8:  return f"{sign}{edge}%  ◆ MODERATE EDGE"
    return f"{sign}{edge}%"

def print_opportunities(opps):
    flagged   = [o for o in opps if o["flagged"]]
    unflagged = [o for o in opps if not o["flagged"]]
    print("\n" + "═" * 72)
    print("  AWARDS MARKET SCANNER")
    print("═" * 72)
    if flagged:
        print(f"\n  🟢  EDGES FOUND ({len(flagged)} markets above {EDGE_THRESHOLD}% threshold)\n")
        for o in flagged:
            print(f"  {'★' if o['edge'] >= 15 else '◆'}  {o['show']} | {o['category']}")
            print(f"     {o['nominee']}")
            print(f"     Model: {o['model_prob']}%  Kalshi: {o['kalshi_prob']}%  Edge: {format_edge_label(o['edge'])}\n")
    else:
        print(f"\n  No edges above {EDGE_THRESHOLD}% found.\n")
    for o in unflagged:
        print(f"  {o['show'][:3].upper()}  {o['category']:<30}  {o['nominee'][:22]:<22}  {format_edge_label(o['edge'])}")
    print("\n" + "═" * 72 + "\n")
