import sqlite3
from datetime import datetime


def parse_browser_history(db_path, source_name):
    events = []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        SELECT url, title, visit_count, typed_count, last_visit_time
        FROM urls
        ORDER BY last_visit_time DESC
        LIMIT 100
        """

        print(f"\n[INFO] Parsing {source_name.upper()} browser logs")
        print("====================================================")

        cursor.execute(query)

        # 🔍 Print column names (for debugging/learning)
        columns = [desc[0] for desc in cursor.description]
        print("COLUMNS:", columns)

        rows = cursor.fetchall()

        for row in rows:
            url, title, visit_count, typed_count, timestamp = row

            visit_time = convert_chrome_time(timestamp)

            # 🔥 Skip invalid timestamps
            if visit_time is None:
                continue

            events.append({
                "timestamp": visit_time,
                "url": url,
                "title": title,
                "visit_count": visit_count,
                "typed_count": typed_count,
                "source": source_name
            })

        conn.close()

    except Exception as e:
        print(f"[ERROR] {source_name} parsing failed: {e}")

    return events


# 🔥 Chrome/Edge timestamp converter
def convert_chrome_time(chrome_time):
    try:
        return datetime.fromtimestamp((chrome_time / 1000000) - 11644473600)
    except:
        return None


# 🔥 TEST BLOCK (VERY USEFUL)
if __name__ == "__main__":
    print("[TEST] Browser parser test")

    test_db = "temp_chrome.db"  # make sure file exists

    data = parse_browser_history(test_db, "chrome")

    print(f"\n[INFO] Extracted {len(data)} events\n")

    for d in data[:5]:
        print(d)