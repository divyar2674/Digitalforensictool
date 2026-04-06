# aihelper/predictor.py


# =========================
# PREDICT BEHAVIOR
# =========================
def predict_from_alerts(alerts):

    if not alerts:
        return {
            "prediction": "Normal system activity",
            "risk_level": "LOW"
        }

    types = [a["type"] for a in alerts]

    if "MASS_DELETE" in types:
        return {
            "prediction": "Possible data wiping or bulk deletion activity",
            "risk_level": "HIGH"
        }

    if "ACCESS_DELETE" in types:
        return {
            "prediction": "User may be accessing and deleting files to hide activity",
            "risk_level": "HIGH"
        }

    if "INTERNAL_ACCESS" in types:
        return {
            "prediction": "Access to internal system detected",
            "risk_level": "MEDIUM"
        }

    return {
        "prediction": "Unusual activity detected",
        "risk_level": "MEDIUM"
    }


# =========================
# MAIN PREDICTION ENGINE
# =========================
def generate_predictions(timeframes, alerts):

    predictions = []

    for tf in timeframes:
        tf_start = tf["timeframe_start"]

        tf_alerts = [a for a in alerts if a["timeframe"] == tf_start]

        result = predict_from_alerts(tf_alerts)

        # 🔥 COLLECT FULL EVENT DETAILS
        evidence = []
        seen_ids = set()

        for alert in tf_alerts:
            for e in alert.get("sequence", []):
                if e["event_id"] not in seen_ids:
                    seen_ids.add(e["event_id"])

                    evidence.append({
                        "event_id": e.get("event_id"),
                        "event_type": e.get("event_type"),
                        "file_name": e.get("file_name"),
                        "source": e.get("source"),
                        "timestamp": e.get("timestamp"),
                        "details": e.get("details"),
                        "metadata": e.get("metadata"),
                        "severity": e.get("severity"),
                        "suspicious": e.get("suspicious"),
                    })

        predictions.append({
            "timeframe": tf_start,
            "prediction": result["prediction"],
            "risk_level": result["risk_level"],

            # 🔥 FULL FORENSIC DATA
            "evidence": evidence,
            "alerts": tf_alerts,
            "events": tf["events"]
        })

    return predictions