import struct
import os
import re
from datetime import datetime


def clean_path(path):
    if not path:
        return None

    match = re.search(r"[a-zA-Z]:\\.*", path)
    if match:
        path = match.group(0)

    return os.path.normcase(os.path.normpath(path))


def filetime_to_datetime(filetime):
    try:
        return datetime.fromtimestamp((filetime - 116444736000000000) / 10000000)
    except:
        return None


def parse_recycle_bin_file(file_path):
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        if len(content) < 24:
            return None

        # SIZE
        size = struct.unpack("<Q", content[8:16])[0]

        # DELETION TIME
        raw_time = struct.unpack("<Q", content[16:24])[0]
        deleted_time = filetime_to_datetime(raw_time)

        # 🔥 FIXED ENCODING (CRITICAL)
        raw_path = content[24:].decode("utf-16le", errors="ignore").rstrip("\x00")

        path = clean_path(raw_path)

        if not path:
            return None

        # 🔥 RETURN CORRECT STRUCTURE
        return {
            "file_path": path,
            "file_name": os.path.basename(path),
            "timestamp": deleted_time,
            "event_type": "FILE_DELETED",
            "source": "RecycleBin",
            "details": path,
            "size": size
        }

    except Exception as e:
        print("[ERROR] Recycle parse failed:", e)
        return None