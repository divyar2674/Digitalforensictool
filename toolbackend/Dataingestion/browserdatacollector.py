import shutil
import os
import sqlite3
from datetime import datetime


def get_browser_paths():
    user = os.getlogin()

    chrome = f"C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
    edge = f"C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"

    return {
        "chrome": chrome,
        "edge": edge
    }


def copy_db(src_path, name):
    dst_path = f"temp_{name}.db"

    try:
        shutil.copy2(src_path, dst_path)
        return dst_path
    except Exception as e:
        print(f"[ERROR] Cannot copy {name} DB: {e}")
        return None


# 🔥 NEW: Convert Chrome timestamp
def convert_chrome_time(chrome_time):
    try:
        return datetime.fromtimestamp((chrome_time / 1000000) - 11644473600)
    except:
        return None


# 🔥 NEW: Extract browser data
def extract_browser_data(db_path, browser_name):
    events = []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        SELECT url, title, visit_count, typed_count, last_visit_time
        FROM urls
        ORDER BY last_visit_time DESC
        LIMIT 50
        """

        cursor.execute(query)

        # 🔍 Print column names (for learning/debug)
        columns = [desc[0] for desc in cursor.description]
        print(f"\n[{browser_name.upper()} COLUMNS]:", columns)

        rows = cursor.fetchall()

        for row in rows:
            url, title, visit_count, typed_count, timestamp = row

            visit_time = convert_chrome_time(timestamp)

            events.append({
                "browser": browser_name.upper(),
                "url": url,
                "title": title,
                "visit_count": visit_count,
                "typed_count": typed_count,
                "timestamp": visit_time
            })

        conn.close()

    except Exception as e:
        print(f"[ERROR] Failed to extract {browser_name}: {e}")

    return events


# 🔥 TEST MAIN
if __name__ == "__main__":
    print("[TEST] Running browser collector...")

    paths = get_browser_paths()

    for name, path in paths.items():
        print(f"\n{name.upper()} PATH: {path}")

        db_copy = copy_db(path, name)

        if db_copy:
            print(f"[SUCCESS] {name} copied to {db_copy}")

            # 🔥 Extract data
            data = extract_browser_data(db_copy, name)

            print(f"[INFO] Extracted {len(data)} records")

            # 🔥 Print sample output
            for d in data[:5]:
                print(d)

        else:
            print(f"[FAILED] {name} copy failed")