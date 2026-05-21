# ============================================================
#  kalshi_client.py — fetches live odds from Kalshi's API
# ============================================================

import requests
import time
from config import KALSHI_API_KEY, KALSHI_SEARCH_TERMS

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

DEMO_MARKETS = [
    {"id": "OSCAR-BESTPIC-BRUTALIST",   "show": "Oscars",        "category": "Best Picture",          "nominee": "The Brutalist",              "kalshi_prob": 44},
    {"id": "OSCAR-BESTACT-BRODY",       "show": "Oscars",        "category": "Best Actor",             "nominee": "Adrien Brody",               "kalshi_prob": 58},
    {"id": "OSCAR-BESTDIR-CORBET",      "show": "Oscars",        "category": "Best Director",          "nominee": "Brady Corbet",               "kalshi_prob": 51},
    {"id": "OSCAR-BESTACT-MOORE",       "show": "Oscars",        "category": "Best Actress",           "nominee": "Demi Moore",                 "kalshi_prob": 52},
    {"id": "OSCAR-INTLFILM-EMILIA",     "show": "Oscars",        "category": "Best Intl. Film",        "nominee": "Emilia Pérez",               "kalshi_prob": 49},
    {"id": "EMMY-DRAMA-JACKAL",         "show": "Emmys",         "category": "Best Drama Series",      "nominee": "The Day of the Jackal",      "kalshi_prob": 28},
    {"id": "EMMY-COMEDY-BEAR",          "show": "Emmys",         "category": "Best Comedy Series",     "nominee": "The Bear",                   "kalshi_prob": 61},
    {"id": "EMMY-LIMITED-DISCLAIMER",   "show": "Emmys",         "category": "Best Limited Series",    "nominee": "Disclaimer",                 "kalshi_prob": 31},
    {"id": "GRAMMY-AOTY-BEYONCE",       "show": "Grammys",       "category": "Album of the Year",      "nominee": "Beyoncé – Cowboy Carter",    "kalshi_prob": 47},
    {"id": "GRAMMY-ROTY-KENDRICK",      "show": "Grammys",       "category": "Record of the Year",     "nominee": "Kendrick Lamar – Not Like Us","kalshi_prob": 41},
    {"id": "GLOBE-DRAMA-CONCLAVE",      "show": "Golden Globes", "category": "Best Picture – Drama",   "nominee": "Conclave",                   "kalshi_prob": 35},
    {"id": "GLOBE-TVSERIES-SHOGUN",     "show": "Golden Globes", "category": "Best TV Series – Drama", "nominee": "Shōgun",                     "kalshi_prob": 68},
]


def get_headers():
    return {
        "Authorization": f"Bearer {KALSHI_API_KEY}",
        "Content-Type": "application/json",
    }


def fetch_markets_for_show(show: str) -> list[dict]:
    """
    Search Kalshi for active markets related to a given awards show.
    Returns a list of dicts with keys: id, title, yes_price (0-100 scale).
    """
    if KALSHI_API_KEY is None:
        return []

    search_term = KALSHI_SEARCH_TERMS.get(show, show.lower())
    params = {
        "status": "open",
        "series_ticker": "",
        "limit": 100,
    }

    try:
        resp = requests.get(
            f"{BASE_URL}/markets",
            headers=get_headers(),
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        markets = data.get("markets", [])

        results = []
        for m in markets:
            title = m.get("title", "").lower()
            if search_term in title:
                yes_price = m.get("yes_ask", 50)   # price in cents (1–99)
                results.append({
                    "id":          m["ticker"],
                    "title":       m.get("title", ""),
                    "kalshi_prob": yes_price,       # cents ≈ implied probability %
                })
        return results

    except requests.RequestException as e:
        print(f"  [Kalshi API error for {show}]: {e}")
        return []


def fetch_all_award_markets() -> list[dict]:
    """
    Fetch markets for all tracked shows. Falls back to demo data
    if no API key is set.
    """
    if KALSHI_API_KEY is None:
        print("  ℹ  No API key set — using demo market data.")
        print("     To use live data: set KALSHI_API_KEY in config.py\n")
        return DEMO_MARKETS

    all_markets = []
    for show in KALSHI_SEARCH_TERMS:
        print(f"  Fetching Kalshi markets for {show}...")
        markets = fetch_markets_for_show(show)
        for m in markets:
            m["show"] = show
        all_markets.extend(markets)
        time.sleep(0.3)   # be polite to the API

    if not all_markets:
        print("  ⚠  No live markets found — falling back to demo data.")
        return DEMO_MARKETS

    return all_markets
