import os
from datetime import datetime
from django.utils import timezone


def parse_file_metadata(file_path):
    try:
        stats = os.stat(file_path)

        _, ext = os.path.splitext(file_path)

        metadata = {
            "path": file_path,

            # ✅ timestamps (timezone aware)
            "created": safe_time(stats.st_ctime),
            "modified": safe_time(stats.st_mtime),
            "accessed": safe_time(stats.st_atime),

            "size": stats.st_size,
            "extension": ext.replace(".", "").upper() if ext else "UNKNOWN",
        }

        return metadata

    except Exception as e:
        print(f"[ERROR] Parser failed: {file_path} | {e}")
        return None


def safe_time(timestamp):
    """
    Convert timestamp → timezone aware datetime
    """
    try:
        dt = datetime.fromtimestamp(timestamp)

        # 🔥 MAKE TIMEZONE AWARE HERE (IMPORTANT)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

    except Exception as e:
        print("[ERROR] Time conversion failed:", timestamp, e)
        return None