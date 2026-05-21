# ============================================================
#  model.py — calculates model probability for each nominee
# ============================================================

from config import SIGNAL_WEIGHTS, SHOW_CONFIDENCE


def bool_to_signal(value) -> float:
    """
    Convert a True/False/None precursor result to a 0.0–1.0 signal.
      True  = won        → strong positive
      False = nominated  → mild negative (being nominated is still good)
      None  = n/a        → neutral (skip this signal)
    """
    if value is True:  return 1.0
    if value is False: return 0.25   # nominated but lost
    return None                      # not applicable, skip


def rt_to_signal(score) -> float | None:
    if score is None: return None
    if score >= 95:   return 1.0
    if score >= 90:   return 0.85
    if score >= 80:   return 0.70
    if score >= 70:   return 0.55
    return 0.30


def guild_to_signal(count) -> float | None:
    if count is None: return None
    if count >= 4:    return 1.0
    if count >= 3:    return 0.85
    if count >= 2:    return 0.70
    if count >= 1:    return 0.50
    return 0.20


def calculate_model_probability(signals: dict) -> dict:
    """
    Given a signals dict (from precursors.py), compute a weighted
    probability estimate. Returns a dict with:
      - 'probability': float 0–100
      - 'confidence':  'high' | 'medium' | 'low'
      - 'signal_breakdown': dict of each signal's contribution
      - 'signals_used': int (how many signals were available)
    """
    show = signals.get("show", "Oscars")
    show_confidence_mult = SHOW_CONFIDENCE.get(show, 1.0)

    # Map raw signal values to 0.0–1.0 strengths
    raw = {
        "sag_win":        bool_to_signal(signals.get("sag_win")),
        "bafta_win":      bool_to_signal(signals.get("bafta_win")),
        "critics_choice": bool_to_signal(signals.get("critics_choice")),
        "guild_noms":     guild_to_signal(signals.get("guild_noms")),
        "rt_score":       rt_to_signal(signals.get("rt_score") or signals.get("metascore")),
        "social_volume":  signals.get("social_volume"),   # already 0.0–1.0
    }

    # Only use signals that are actually available (not None)
    available = {k: v for k, v in raw.items() if v is not None}
    signals_used = len(available)

    if signals_used == 0:
        return {
            "probability":        50.0,
            "confidence":         "low",
            "signal_breakdown":   {},
            "signals_used":       0,
        }

    # Re-normalize weights to only the available signals
    total_weight = sum(SIGNAL_WEIGHTS[k] for k in available)
    breakdown = {}
    weighted_sum = 0.0

    for key, strength in available.items():
        w = SIGNAL_WEIGHTS[key] / total_weight   # normalized weight
        contribution = w * strength
        weighted_sum += contribution
        breakdown[key] = {
            "raw_signal":    round(strength, 2),
            "weight":        round(w, 3),
            "contribution":  round(contribution * 100, 1),
        }

    # weighted_sum is now 0.0–1.0; convert to probability %
    # Apply a slight sigmoid squeeze so we never output 0% or 100%
    raw_prob = weighted_sum
    squeezed = 0.05 + raw_prob * 0.90   # clamp to 5%–95%

    # Apply show-level confidence dampening (pulls toward 50%)
    dampened = 0.5 + (squeezed - 0.5) * show_confidence_mult

    probability = round(dampened * 100, 1)

    # Confidence tier based on how many signals we had
    if signals_used >= 4:   confidence = "high"
    elif signals_used >= 2: confidence = "medium"
    else:                   confidence = "low"

    return {
        "probability":      probability,
        "confidence":       confidence,
        "signal_breakdown": breakdown,
        "signals_used":     signals_used,
    }
