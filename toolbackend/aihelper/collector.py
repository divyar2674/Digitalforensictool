# aihelper/collector.py

from mytool.models import FileEvent, BrowserEvent, WindowsEvent


# =========================
# SAFE TIMESTAMP FORMAT
# =========================
def safe_timestamp(ts):
    try:
        return ts
    except:
        return None


# =========================
# FILE EVENTS (2026 ONLY)
# =========================
def collect_file_events():
    events = []

    for f in FileEvent.objects.filter(timestamp__year=2026):  # 🔥 FILTER ADDED
        events.append({
            "timestamp": safe_timestamp(f.timestamp),
            "event_type": f.event_type,
            "source": f.source,
            "file_name": f.file_name,
            "details": f.path,
            "metadata": {
                "path": f.path,
                "size": f.size,
                "extension": f.extension,
                "created_time": f.created_time,
                "modified_time": f.modified_time,
                "accessed_time": f.accessed_time,
                "deleted_time": f.deleted_time,
                "note": f.note
            }
        })

    return events


# =========================
# BROWSER EVENTS (2026 ONLY)
# =========================
def collect_browser_events():
    events = []

    for b in BrowserEvent.objects.filter(timestamp__year=2026):  # 🔥 FILTER ADDED
        events.append({
            "timestamp": safe_timestamp(b.timestamp),
            "event_type": "BROWSER_VISIT",
            "source": b.browser,
            "file_name": b.browser,
            "details": b.url,
            "metadata": {
                "url": b.url,
                "title": b.title,
                "visit_count": b.visit_count,
                "typed_count": b.typed_count
            }
        })

    return events


# =========================
# WINDOWS EVENTS (2026 ONLY)
# =========================
def collect_windows_events():
    events = []

    for w in WindowsEvent.objects.filter(timestamp__year=2026):  # 🔥 FILTER ADDED
        events.append({
            "timestamp": safe_timestamp(w.timestamp),
            "event_type": w.event_type,
            "source": w.source,
            "file_name": w.username or w.process_name,
            "details": w.process_name or "",
            "metadata": {
                "username": w.username,
                "ip_address": w.ip_address,
                "process": w.process_name,
                "event_id": w.event_id
            }
        })

    return events


# =========================
# MAIN COLLECTOR
# =========================
def collect_all_events():

    file_events = collect_file_events()
    browser_events = collect_browser_events()
    windows_events = collect_windows_events()

    # 🔥 MERGE ALL
    timeline = file_events + browser_events + windows_events

    # 🔥 REMOVE INVALID TIMESTAMPS
    timeline = [e for e in timeline if e["timestamp"]]

    # 🔥 SORT BY TIME
    timeline.sort(key=lambda x: x["timestamp"])

    # 🔥 ADD EVENT IDs
    for i, e in enumerate(timeline):
        e["event_id"] = i + 1

    return timeline