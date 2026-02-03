import os
import json
import pickle

META_DIR = "../data/metadata/"
CACHE_FILE = "../output/packet_len_cache.pkl"

with open(CACHE_FILE, "rb") as f:
    cache = pickle.load(f)

errors = 0
files_checked = 0

for meta_file in sorted(os.listdir(META_DIR)):
    if not meta_file.endswith(".json"):
        continue

    file_key = meta_file.replace(".json", "")

    if file_key not in cache:
        print(f"[ERROR] Missing cache entry for {file_key}")
        errors += 1
        continue

    with open(os.path.join(META_DIR, meta_file)) as f:
        meta = json.load(f)

    cache_entries = cache[file_key]
    cache_len = len(cache_entries)
    meta_len = len(meta)

    # Check length consistency
    if cache_len != meta_len:
        print(f"[ERROR] Length mismatch in {file_key}: cache={cache_len}, meta={meta_len}")
        errors += 1
        continue

    # Check PacketCnt alignment
    for record in meta:
        pkt_cnt = record["PacketCnt"]
        cache_idx = pkt_cnt - 1

        if cache_idx not in cache_entries:
            print(f"[ERROR] Index mismatch in {file_key}: PacketCnt={pkt_cnt}")
            errors += 1
            break

    files_checked += 1

print("\n====== SUMMARY ======")
print(f"Files checked: {files_checked}")
print(f"Errors found: {errors}")

if errors == 0:
    print("All metadata & cache indices align")
else:
    print("Index mismatches detected.")

