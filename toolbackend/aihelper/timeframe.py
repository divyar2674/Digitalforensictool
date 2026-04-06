# aihelper/timeframe.py

from datetime import datetime


# =========================
# SAFE TIMESTAMP PARSER
# =========================
def parse_timestamp(ts):
    if isinstance(ts, datetime):
        return ts

    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts)
        except:
            return None

    return None


# =========================
# GROUP INTO 1-HOUR WINDOWS
# =========================
def group_by_hour(timeline):
    grouped = {}

    for event in timeline:
        ts = parse_timestamp(event.get("timestamp"))

        if not ts:
            continue

        # normalize to hour
        hour_key = ts.replace(minute=0, second=0, microsecond=0)

        if hour_key not in grouped:
            grouped[hour_key] = []

        grouped[hour_key].append(event)

    return grouped


# =========================
# CONVERT GROUPED → LIST FORMAT
# =========================
def format_timeframes(grouped_data):
    formatted = []

    for hour, events in grouped_data.items():
        formatted.append({
            "timeframe_start": str(hour),
            "timeframe_end": str(hour.replace(minute=59, second=59)),
            "event_count": len(events),
            "events": events
        })

    # sort by time
    formatted.sort(key=lambda x: x["timeframe_start"])

    return formatted


# =========================
# MAIN FUNCTION
# =========================
def build_timeframes(timeline):

    grouped = group_by_hour(timeline)

    formatted = format_timeframes(grouped)

    return formatted