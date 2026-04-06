import os
from datetime import datetime


def collect_files(root_path, limit=1000):
    files_data = []
    count = 0

    for root, dirs, files in os.walk(root_path):
        for file in files:
            full_path = os.path.join(root, file)

            try:
                stat = os.stat(full_path)

                file_info = {
                    "path": full_path,
                    "size": stat.st_size,  # 🔥 size in bytes
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "accessed": datetime.fromtimestamp(stat.st_atime),
                }

                files_data.append(file_info)
                count += 1

                if count >= limit:
                    return files_data

            except Exception as e:
                # skip inaccessible files
                continue

    return files_data

if __name__ == "__main__":
    test_path = "D:\personal\CSS"
    files = collect_files(test_path, limit=5000)
    for f in files:
        print(f)