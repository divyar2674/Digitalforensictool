# =========================
# IMPORTS
# =========================
from datetime import datetime
from django.utils import timezone
from mytool.models import WindowsEvent, FileEvent, BrowserEvent
from Dataingestion.mftcollector import parse_mft_fallback


# =========================
# HELPERS
# =========================
def make_aware_safe(dt):
    if not dt:
        return None
    if isinstance(dt, datetime):
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
    return None


def parse_timestamp(ts):
    if not ts:
        return None

    if isinstance(ts, datetime):
        return make_aware_safe(ts)

    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts)
        except:
            try:
                dt = datetime.strptime(ts, "%m/%d/%Y %H:%M:%S")
            except:
                return None
        return make_aware_safe(dt)

    return None


def ensure_list(data):
    return data if isinstance(data, list) else [data]


def get_value(data, index):
    return data[index] if len(data) > index and data[index] else None


# =========================
# 🪟 WINDOWS EVENTS
# =========================
def normalize_windows_events(events, case=None):
    events = ensure_list(events)

    normalized = []
    saved_count = 0

    for e in events:
        try:
            event_id = e.get("event_id")
            timestamp = parse_timestamp(e.get("timestamp"))
            data = e.get("data", [])
            source = e.get("source", "Windows")

            if not timestamp:
                continue

            username = None
            ip = None
            process = None
            event_type = "WINDOWS_EVENT"

            if event_id in [4624, 4625]:
                username = get_value(data, 5) or "UNKNOWN"
                raw_ip = get_value(data, 18)
                ip = raw_ip if raw_ip not in [None, "-", ""] else "LOCAL"
                status = "SUCCESS" if event_id == 4624 else "FAILED"
                event_type = f"LOGIN_{status}"

            elif event_id == 4688:
                process = get_value(data, 5) or "UNKNOWN"
                event_type = "PROCESS_CREATED"

            else:
                process = str(data)[:200] if data else "SYSTEM"

            # DB SAVE (optional)
            try:
                WindowsEvent.objects.get_or_create(
                    timestamp=timestamp,
                    event_id=event_id,
                    source=source,
                    case=case,
                    defaults={
                        "username": username,
                        "ip_address": ip,
                        "process_name": process,
                        "event_type": event_type
                    }
                )
                saved_count += 1
            except Exception as db_err:
                print("[WARNING] Windows DB failed:", db_err)

            # ALWAYS APPEND
            normalized.append({
                "timestamp": timestamp,
                "event_type": event_type,
                "source": source,
                "file_name": username or process or "SYSTEM",
                "details": process or "",
                "metadata": {
                    "event_id": event_id,
                    "username": username,
                    "ip_address": ip,
                    "process": process
                }
            })

        except Exception as ex:
            print("[ERROR] Windows:", ex)

    print(f"[INFO] Windows events sent: {len(normalized)}")
    return normalized


# =========================
# 📁 FILE EVENTS
# =========================
def normalize_file_events(files, case=None):
    files = ensure_list(files)

    normalized = []

    for f in files:
        try:
            path = f.get("path") or "unknown_path"
            size = f.get("size", 0)

            file_name = path.split("\\")[-1]
            extension = file_name.split(".")[-1].upper() if "." in file_name else "UNKNOWN"

            created = make_aware_safe(parse_timestamp(f.get("created")))
            modified = make_aware_safe(parse_timestamp(f.get("modified")))
            accessed = make_aware_safe(parse_timestamp(f.get("accessed")))

            for ts, event_type in [
                (created, "FILE_CREATED"),
                (modified, "FILE_MODIFIED"),
                (accessed, "FILE_ACCESSED")
            ]:
                timestamp = ts or timezone.now()

                # DB SAVE (optional)
                try:
                    FileEvent.objects.create(
                        timestamp=timestamp,
                        file_name=file_name,
                        source="FileSystem",
                        event_type=event_type,
                        path=path,
                        size=size,
                        extension=extension,
                        created_time=created,
                        modified_time=modified,
                        accessed_time=accessed,
                        case=case
                    )
                except Exception as db_err:
                    print("[WARNING] File DB failed:", db_err)

                # ALWAYS APPEND
                normalized.append({
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "source": "FileSystem",
                    "file_name": file_name,
                    "details": path,
                    "metadata": {
                        "size": size,
                        "extension": extension,
                        "created": created,
                        "modified": modified,
                        "accessed": accessed
                    }
                })

        except Exception as e:
            print("[ERROR] File:", e)

    print(f"[INFO] File events sent: {len(normalized)}")
    return normalized


# =========================
# 🌐 BROWSER EVENTS
# =========================
def normalize_browser_events(events, case=None):
    events = ensure_list(events)

    normalized = []

    for e in events:
        try:
            timestamp = parse_timestamp(e.get("timestamp")) or timezone.now()

            # DB SAVE (optional)
            try:
                BrowserEvent.objects.create(
                    timestamp=timestamp,
                    url=e.get("url"),
                    title=e.get("title"),
                    browser=e.get("browser"),
                    visit_count=e.get("visit_count", 0),
                    typed_count=e.get("typed_count", 0),
                    case=case
                )
            except Exception as db_err:
                print("[WARNING] Browser DB failed:", db_err)

            # ALWAYS APPEND
            normalized.append({
                "timestamp": timestamp,
                "event_type": "BROWSER_VISIT",
                "source": e.get("browser"),
                "file_name": e.get("browser"),
                "details": e.get("url"),
                "metadata": {
                    "title": e.get("title"),
                    "visit_count": e.get("visit_count"),
                    "typed_count": e.get("typed_count")
                }
            })

        except Exception as err:
            print("[ERROR] Browser:", err)

    print(f"[INFO] Browser events sent: {len(normalized)}")
    return normalized


# =========================
# 🗑️ RECYCLE BIN EVENTS
# =========================
def normalize_recycle_events(events, case=None):
    events = ensure_list(events)

    normalized = []

    for e in events:
        try:
            path = e.get("file_path") or e.get("original_path") or e.get("details") or "recycle_unknown"
            size = e.get("size", 0)

            file_name = path.split("\\")[-1]
            extension = file_name.split(".")[-1].upper() if "." in file_name else "UNKNOWN"

            ts = e.get("timestamp") or e.get("deleted_time")
            timestamp = make_aware_safe(parse_timestamp(ts)) or timezone.now()

            # =========================
            # 🔥 PREVIOUS STATE (FAST DB ONLY)
            # =========================
            created = modified = accessed = None

            try:
                records = FileEvent.objects.filter(
                    case=case,
                    file_name=file_name,
                    timestamp__lt=timestamp
                ).order_by("timestamp")

                for r in records:
                    if r.event_type == "FILE_CREATED" and not created:
                        created = r.timestamp
                    elif r.event_type == "FILE_MODIFIED":
                        modified = r.timestamp
                    elif r.event_type == "FILE_ACCESSED":
                        accessed = r.timestamp
            except Exception as db_err:
                print("[WARNING] DB lookup failed:", db_err)

            # =========================
            # ❌ DISABLED MFT (CAUSE OF FREEZE)
            # =========================
            # if not created and not modified:
            #     try:
            #         mft = parse_mft_fallback(file_name)
            #     except:
            #         pass

            # =========================
            # 🔥 FINAL SAFETY
            # =========================
            created = created or timestamp
            modified = modified or timestamp
            accessed = accessed or timestamp

            # =========================
            # DB SAVE (OPTIONAL)
            # =========================
            try:
                FileEvent.objects.create(
                    timestamp=timestamp,
                    file_name=file_name,
                    source="RecycleBin",
                    event_type="FILE_DELETED",
                    path=path,
                    size=size,
                    extension=extension,
                    deleted_time=timestamp,
                    created_time=created,
                    modified_time=modified,
                    accessed_time=accessed,
                    case=case
                )
            except Exception as db_err:
                print("[WARNING] Recycle DB failed:", db_err)

            # =========================
            # 🔥 ALWAYS APPEND (FRONTEND SAFE)
            # =========================
            normalized.append({
                "timestamp": timestamp,
                "event_type": "FILE_DELETED",
                "source": "RecycleBin",
                "file_name": file_name,
                "details": path,
                "metadata": {
                    "size": size,
                    "extension": extension,
                    "deleted_time": timestamp,
                    "previous_state": {
                        "created_time": created,
                        "modified_time": modified,
                        "accessed_time": accessed
                    }
                }
            })

        except Exception as err:
            print("[ERROR] Recycle:", err)

    print(f"[INFO] Recycle events sent: {len(normalized)}")
    return normalized