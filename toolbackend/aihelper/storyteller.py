from datetime import datetime


def generate_story(events, chains, start=None, end=None):

    # 🔥 FILTER EVENTS BY TIME
    filtered = []

    for e in events:
        ts = e.get("timestamp")

        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)

        if start and end:
            if start <= ts <= end:
                filtered.append(e)
        else:
            filtered.append(e)

    if not filtered:
        return "No activity found in selected timeframe."

    story = "🧠 Investigation Narrative\n\n"

    # =====================================
    # 🔥 1. HIGH LEVEL SUMMARY
    # =====================================

    event_types = [e["event_type"] for e in filtered]

    total = len(filtered)
    logins = event_types.count("LOGIN_SUCCESS")
    fails = event_types.count("LOGIN_FAILURE")
    deletes = event_types.count("FILE_DELETED")

    story += f"Total Events: {total}\n"
    story += f"Successful Logins: {logins}\n"
    story += f"Failed Logins: {fails}\n"
    story += f"File Deletions: {deletes}\n\n"

    # =====================================
    # 🔥 2. CHAIN-BASED ANALYSIS
    # =====================================

    if chains:
        story += "🔗 Correlated Activity Detected:\n\n"

        for chain in chains:
            story += f"{chain['chain_id']} ({chain['risk']} risk)\n"
            story += f"Time: {chain['start_time']} → {chain['end_time']}\n"

            # 🔥 compress events (no spam)
            types = list(set([e["event_type"] for e in chain["events"]]))
            story += f"Events: {', '.join(types)}\n"

            # 🔥 reasons
            for r in chain["reasons"]:
                story += f"⚠️ {r}\n"

            story += "\n"
    else:
        story += "No suspicious correlated activity detected.\n\n"

    # =====================================
    # 🔥 3. BEHAVIOR SUMMARY
    # =====================================

    visited_domains = set()
    accessed_files = set()

    for e in filtered:
        if e["event_type"] == "BROWSER_VISIT":
            url = e.get("metadata", {}).get("url", "")
            if url:
                try:
                    domain = url.split("/")[2]
                    visited_domains.add(domain)
                except:
                    pass

        if e["event_type"].startswith("FILE"):
            accessed_files.add(e.get("file_name"))

    if visited_domains:
        story += "🌐 Websites Accessed:\n"
        for d in list(visited_domains)[:5]:
            story += f"- {d}\n"
        story += "\n"

    if accessed_files:
        story += "📁 Files Touched:\n"
        for f in list(accessed_files)[:5]:
            story += f"- {f}\n"
        story += "\n"

    # =====================================
    # 🔥 4. FINAL VERDICT
    # =====================================

    if chains:
        high_risk = any(c["risk"] == "HIGH" for c in chains)

        if high_risk:
            story += "🚨 Risk Level: HIGH\n"
            story += "Potential malicious sequence detected.\n"
        else:
            story += "⚠️ Risk Level: MEDIUM\n"
            story += "Suspicious patterns observed.\n"
    else:
        story += "🟢 Risk Level: LOW\n"
        story += "Activity appears normal.\n"

    return story