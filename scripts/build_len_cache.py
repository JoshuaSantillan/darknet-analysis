from scapy.all import IP, PcapReader
import os
import pickle
from collections import defaultdict

pcap_dir = "../data/pcaps/"
cache_file = "../output/packet_len_cache.pkl"

def build_packet_len_cache():
    packet_len_cache = defaultdict(dict)

    pcap_files = sorted([
        f for f in os.listdir(pcap_dir)
        if f.endswith(".pcap")
    ])

    count = 1
    for filename in pcap_files:
        path = os.path.join(pcap_dir, filename)
        file_key = filename.replace(".pcap", "")

        print(f"Reading [{count}]: {filename}")
        count += 1

        pkt_index = 0
        with PcapReader(path) as packets:
            for pkt in packets:
                if IP not in pkt:
                    continue

                packet_len_cache[file_key][pkt_index] = pkt[IP].len
                pkt_index += 1

    return packet_len_cache

def main():
    if os.path.exists(cache_file):
        print(f"{cache_file} exists already.")
        return

    print("Building cache")
    packet_len_cache = build_packet_len_cache()

    with open(cache_file, "wb") as f:
        pickle.dump(packet_len_cache, f)
    print(f"Saved to {cache_file}")


if __name__ == "__main__":
    main()
