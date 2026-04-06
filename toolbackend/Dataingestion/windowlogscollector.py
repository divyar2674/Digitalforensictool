import win32evtlog

# Event IDs you care about
IMPORTANT_EVENT_IDS = {4624, 4625, 4648, 4688, 4663}


def collect_windows_logs(limit=200, log_type="Security"):
    server = "localhost"
    handle = win32evtlog.OpenEventLog(server, log_type)

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    events = []
    count = 0

    try:
        while count < limit:
            records = win32evtlog.ReadEventLog(handle, flags, 0)

            if not records:
                break

            for event in records:
                event_id = event.EventID & 0xFFFF

                if event_id not in IMPORTANT_EVENT_IDS:
                    continue

                try:
                    timestamp = str(event.TimeGenerated)

                    # THIS is what your normalizer expects
                    data = event.StringInserts if event.StringInserts else []

                    parsed_event = {
                        "event_id": event_id,
                        "timestamp": timestamp,
                        "source": log_type,
                        "data": data
                    }

                    events.append(parsed_event)
                    count += 1

                    if count >= limit:
                        break

                except Exception as e:
                    print(f"[ERROR] Event parsing failed: {e}")

    except Exception as e:
        print(f"[ERROR] Log read failed: {e}")

    finally:
        win32evtlog.CloseEventLog(handle)

    print(f"[INFO] Collected {len(events)} Windows events")
    return events


if __name__ == "__main__":
    logs = collect_windows_logs(limit=50)
    logs=normalize_windows_events(logs)
    for log in logs:
        print(log)