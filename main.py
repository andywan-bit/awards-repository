# ============================================================
#  main.py — run this file to start the scanner
#
#  Usage:
#    python main.py          # run once and exit
#    python main.py --watch  # refresh every 5 minutes
# ============================================================

import sys
import time
from datetime import datetime
from opportunities import build_opportunities, print_opportunities
from config import REFRESH_INTERVAL_SECONDS


def run_once():
    print(f"\n  [{datetime.now().strftime('%H:%M:%S')}] Running scanner...")
    opportunities = build_opportunities()
    print_opportunities(opportunities)
    return opportunities


def run_watch_mode():
    print("\n  Watch mode ON — refreshing every "
          f"{REFRESH_INTERVAL_SECONDS // 60} minutes. Press Ctrl+C to stop.\n")
    try:
        while True:
            run_once()
            print(f"  Next refresh in {REFRESH_INTERVAL_SECONDS // 60} minutes...")
            time.sleep(REFRESH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n  Stopped.\n")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        run_watch_mode()
    else:
        run_once()
