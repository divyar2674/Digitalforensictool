from datetime import datetime


# =========================
# HELPER: BUILD EVENT CHAIN
# =========================
def build_event_chain(events):
    return " → ".join([e["event_type"] for e in events])


# =========================
# HELPER: TIME DIFFERENCE
# =========================
def time_diff_seconds(t1, t2):
    try:
        return abs((t2 - t1).total_seconds())
    except:
        return 999999


# =========================
# 🔥 RULE: ACCESS → DELETE
# =========================
def detect_access_delete(events):
    alerts = []
    suspicious_ids = set()

    for i in range(len(events) - 1):
        curr = events[i]
        nxt = events[i + 1]

        if (
            curr["event_type"] == "FILE_ACCESSED" and
            nxt["event_type"] == "FILE_DELETED"
        ):
            seconds = time_diff_seconds(curr["timestamp"], nxt["timestamp"])

            if seconds <= 10:
                sequence = [curr, nxt]

                alerts.append({
                    "type": "ACCESS_DELETE",
                    "risk": "HIGH",
                    "risk_score": 90,
                    "message": "File accessed and then deleted",

                    "chain": build_event_chain(sequence),
                    "sequence": sequence,

                    "explanation": f"File '{curr.get('file_name')}' was accessed and deleted within {int(seconds)} seconds"
                })

                suspicious_ids.update([curr["event_id"], nxt["event_id"]])

    return alerts, suspicious_ids


# =========================
# 🔥 RULE: MASS DELETE
# =========================
def detect_mass_delete(events):
    alerts = []
    suspicious_ids = set()

    delete_events = [e for e in events if e["event_type"] == "FILE_DELETED"]

    if len(delete_events) >= 3:
        alerts.append({
            "type": "MASS_DELETE",
            "risk": "HIGH",
            "risk_score": 95,
            "message": f"{len(delete_events)} files deleted",

            "chain": build_event_chain(delete_events),
            "sequence": delete_events,

            "explanation": "Multiple files deleted in short time → possible data wiping"
        })

        for e in delete_events:
            suspicious_ids.add(e["event_id"])

    return alerts, suspicious_ids


# =========================
# 🔥 RULE: INTERNAL ACCESS
# =========================
def detect_internal_access(events):
    alerts = []
    suspicious_ids = set()

    for e in events:
        if e["event_type"] == "BROWSER_VISIT":
            url = e.get("metadata", {}).get("url", "")

            if url.startswith("http://10.") or url.startswith("http://192.168"):
                alerts.append({
                    "type": "INTERNAL_ACCESS",
                    "risk": "MEDIUM",
                    "risk_score": 60,
                    "message": f"Internal access: {url}",

                    "chain": build_event_chain([e]),
                    "sequence": [e],

                    "explanation": "Access to internal/private network detected"
                })

                suspicious_ids.add(e["event_id"])

    return alerts, suspicious_ids


# =========================
# 🔥 RULE: BRUTE FORCE LOGIN
# =========================
def detect_bruteforce_login(events):
    alerts = []
    suspicious_ids = set()

    fail_events = [e for e in events if e["event_type"] == "LOGIN_FAILED"]

    if len(fail_events) >= 3:
        alerts.append({
            "type": "BRUTE_FORCE_LOGIN",
            "risk": "HIGH",
            "risk_score": 90,
            "message": f"{len(fail_events)} failed login attempts",

            "chain": build_event_chain(fail_events),
            "sequence": fail_events,

            "explanation": "Multiple failed logins → possible brute-force attack"
        })

        for e in fail_events:
            suspicious_ids.add(e["event_id"])

    return alerts, suspicious_ids


# =========================
# 🔥 RULE: FAILED → SUCCESS LOGIN
# =========================
def detect_suspicious_login(events):
    alerts = []
    suspicious_ids = set()

    for i in range(len(events) - 1):
        curr = events[i]
        nxt = events[i + 1]

        if (
            curr["event_type"] == "LOGIN_FAILED" and
            nxt["event_type"] == "LOGIN_SUCCESS"
        ):
            alerts.append({
                "type": "SUSPICIOUS_LOGIN",
                "risk": "HIGH",
                "risk_score": 95,
                "message": "Login success after failures",

                "chain": build_event_chain([curr, nxt]),
                "sequence": [curr, nxt],

                "explanation": "Successful login after failures → possible compromise"
            })

            suspicious_ids.update([curr["event_id"], nxt["event_id"]])

    return alerts, suspicious_ids


# =========================
# 🔥 RULE: SUSPICIOUS PROCESS
# =========================
def detect_suspicious_process(events):
    alerts = []
    suspicious_ids = set()

    suspicious_keywords = ["powershell", "cmd.exe", "mimikatz", "net user"]

    for e in events:
        if e["event_type"] == "PROCESS_CREATED":
            process = str(e.get("metadata", {}).get("process", "")).lower()

            for keyword in suspicious_keywords:
                if keyword in process:
                    alerts.append({
                        "type": "SUSPICIOUS_PROCESS",
                        "risk": "HIGH",
                        "risk_score": 85,
                        "message": f"Suspicious process: {process}",

                        "chain": build_event_chain([e]),
                        "sequence": [e],

                        "explanation": f"{keyword} execution may indicate malicious activity"
                    })

                    suspicious_ids.add(e["event_id"])
                    break

    return alerts, suspicious_ids


# =========================
# 🔥 APPLY RULES (CORE ENGINE)
# =========================
def analyze_events(events):

    # ALWAYS SORT
    events.sort(key=lambda x: x["timestamp"])

    all_alerts = []
    all_suspicious_ids = set()

    rules = [
        detect_access_delete,
        detect_mass_delete,
        detect_internal_access,

        # 🔥 WINDOWS RULES
        detect_bruteforce_login,
        detect_suspicious_login,
        detect_suspicious_process
    ]

    for rule in rules:
        alerts, ids = rule(events)
        all_alerts.extend(alerts)
        all_suspicious_ids.update(ids)

    # MARK EVENTS
    for e in events:
        if e["event_id"] in all_suspicious_ids:
            e["suspicious"] = True
            e["severity"] = "HIGH"
        else:
            e["suspicious"] = False
            e["severity"] = "NORMAL"

    return {
        "alerts": all_alerts,
        "events": events
    }


# =========================
# 🔥 APPLY RULES ON TIMEFRAMES
# =========================
def analyze_timeframes(timeframes):

    final_alerts = []
    seen = set()

    for tf in timeframes:
        result = analyze_events(tf["events"])

        for alert in result["alerts"]:
            alert["timeframe"] = tf["timeframe_start"]

            key = (alert["type"], alert["timeframe"])

            if key not in seen:
                seen.add(key)
                final_alerts.append(alert)

    return final_alerts