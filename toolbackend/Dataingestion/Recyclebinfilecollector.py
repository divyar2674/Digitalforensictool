import os
from parser.recyclebin_parser import parse_recycle_bin_file
from normalizer import normalize_recycle_events
def collect_recycle_bin_files(bin_path):
    recycle_files = []

    if not os.path.exists(bin_path):
        print(f"[ERROR] Path does not exist: {bin_path}")
        return recycle_files

    print(f"[INFO] Scanning Recycle Bin: {bin_path}")

    for root, dirs, files in os.walk(bin_path):
        for file in files:
            if file.startswith("$I"):
                full_path = os.path.join(root, file)
                recycle_files.append(full_path)

    print(f"[RESULT] Total $I files found: {len(recycle_files)}")

    return recycle_files

if __name__ == "__main__":
    test_path = "D:\\$RECYCLE.BIN"
    files = collect_recycle_bin_files(test_path)
    for file in files:
        metadata = parse_recycle_bin_file(file)
        if metadata:
            normalized = normalize_recycle_events(metadata)
            print(f"Normalized event: {normalized}")

    print(f"Test found {len(files)} recycle bin files.")