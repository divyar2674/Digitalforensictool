# aihelper/summary.py


# =========================
# OVERVIEW STATS
# =========================
def build_overview(timeline, alerts):

    total_events = len(timeline)
    suspicious_events = sum(1 for e in timeline if e.get("suspicious"))
    total_alerts = len(alerts)
    high_risk = sum(1 for a in alerts if a.get("risk") == "HIGH")

    return {
        "total_events": total_events,
        "suspicious_events": suspicious_events,
        "total_alerts": total_alerts,
        "high_risk_alerts": high_risk
    }


# =========================
# CLEAN ALERTS FOR UI
# =========================
def format_alerts(alerts):

    formatted = []

    for a in alerts:
        formatted.append({
            "type": a.get("type"),
            "risk": a.get("risk"),
            "timeframe": a.get("timeframe"),
            "chain": a.get("chain"),
            "explanation": a.get("explanation"),

            # 🔥 important for UI click
            "sequence": a.get("sequence")
        })

    return formatted


# =========================
# CLEAN PREDICTIONS FOR UI
# =========================
def format_predictions(predictions):

    formatted = []

    for p in predictions:
        formatted.append({
            "timeframe": p.get("timeframe"),
            "prediction": p.get("prediction"),
            "risk_level": p.get("risk_level"),

            # 🔥 KEY FEATURE
            "evidence": p.get("evidence"),

            # optional (if needed in UI)
            "alerts": p.get("alerts")
        })

    return formatted


# =========================
# TIMELINE EVENTS (OPTIONAL)
# =========================
def format_timeline(timeline):

    formatted = []

    for e in timeline:
        formatted.append({
            "event_id": e.get("event_id"),
            "timestamp": str(e.get("timestamp")),
            "event_type": e.get("event_type"),
            "file_name": e.get("file_name"),
            "source": e.get("source"),
            "details": e.get("details"),

            "suspicious": e.get("suspicious"),
            "severity": e.get("severity"),

            "metadata": e.get("metadata")
        })

    return formatted


# =========================
# MAIN SUMMARY FUNCTION
# =========================
def generate_summary(timeline, alerts, predictions):

    return {
        "overview": build_overview(timeline, alerts),

        # 🔥 MAIN DATA FOR FRONTEND
        "alerts": format_alerts(alerts),
        "predictions": format_predictions(predictions),

        # optional (used in timeline page)
        "timeline": format_timeline(timeline)
    }