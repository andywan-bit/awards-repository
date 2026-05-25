# ============================================================
#  config.py — tweak these values to adjust the model
# ============================================================

# Your Kalshi API key — get it from kalshi.com → Settings → API
# Leave as None to run in demo mode (no live Kalshi data)
KALSHI_API_KEY = None

# Minimum edge (%) before a trade is flagged as worth considering
# e.g. 8 means model must be 8% higher than Kalshi's implied odds
EDGE_THRESHOLD = 8

# How often to refresh data when running in watch mode (seconds)
REFRESH_INTERVAL_SECONDS = 300  # 5 minutes

# ── Signal weights ───────────────────────────────────────────
# These add up to 1.0. Adjust based on how much you trust each source.
# Based on historical Oscar/Emmy precursor correlation data 2000–2025.

SIGNAL_WEIGHTS = {
    "critics_choice": 0.413,
    "sag_win":        0.285,
    "social_volume":  0.091,
    "guild_noms":     0.091,
    "bafta_win":      0.086,
    "rt_score":       0.034,
}

# ── Per-show adjustments ─────────────────────────────────────
# Grammys are less predictable so we dampen confidence
SHOW_CONFIDENCE = {
    "Oscars":        1.0,
    "Emmys":         0.9,
    "Golden Globes": 0.85,
    "Grammys":       0.70,   # High voter surprise rate
}

# ── Award shows to track ─────────────────────────────────────
TRACKED_SHOWS = ["Oscars", "Emmys", "Grammys", "Golden Globes"]

# ── Kalshi market search terms per show ─────────────────────
KALSHI_SEARCH_TERMS = {
    "Oscars":        "oscar",
    "Emmys":         "emmy",
    "Grammys":       "grammy",
    "Golden Globes": "golden globe",
}
