from scapy.all import rdpcap, IP, TCP, UDP, ICMP, PcapReader
import os
import pickle
from collections import defaultdict

pcap_dir = "../data/pcaps/"
cache_file = "../output/parsed_21.pkl"

def populate_dicts(packet_counts, byte_counts):
    #2.1.3 Iterate PCAPS
    
    total_packets = 0
    total_bytes = 0

    pcap_files = sorted([
        file for file in os.listdir(pcap_dir)
        if file.endswith(".pcap")
    ])
   
    count = 1
    for filename in pcap_files:
        path = os.path.join(pcap_dir, filename) # ../data/filename
        print(f"Currently opening [{count}]: ", filename)
        count +=1
        #Populate 
        with PcapReader(path) as packets:
            for pkt in packets:

                if IP not in pkt:
                    continue ## no IP tag on packet frame

                total_packets += 1
                pkt_len = pkt[IP].len # cur pkt size
                total_bytes += pkt_len # bytes in entire dataset regardless of category

                if TCP in pkt:
                    key = ("TCP", pkt[TCP].dport)
                elif UDP in pkt:
                    key = ("UDP", pkt[UDP].dport)
                elif ICMP in pkt:
                    key = ("ICMP", (pkt[ICMP].type, pkt[ICMP].code))
                # Different Protocol
                else:
                    key = ("Other", pkt[IP].proto)

                packet_counts[key] += 1 # How many of this packet type
                byte_counts[key] += pkt_len # How many bytes per category

    return total_packets, total_bytes

def get_top_N(byte_counts, n=5):
    #Change N as needed
    top = sorted(
            byte_counts.items(),
            key=lambda x: x[1],
            reverse=True
    )[:n]
    return top

def rank_by_volume(top_N, packet_counts, byte_counts, total_packets, total_bytes):
    print("\nPerforming Rank By Volune")
    for rank, (key, bytes_) in enumerate(top_N, start = 1):
        packets_ = packet_counts[key]

        if total_bytes == 0 or total_packets == 0:
            print(f"Total Bytes or Total Packets is Zero: ({total_bytes},{total_packets})")
            return
        byte_pct = (bytes_ / total_bytes) * 100
        pkt_pct = (packets_ / total_packets) * 100

        proto, detail = key

        if proto in ("TCP", "UDP"):
            label = f"{proto} ({detail})"
        elif proto == "ICMP":
            label = f"ICMP (type {detail[0]}, code {detail[1]})"
        else:
            label = f"OTHER ({detail})"

        print(
            f"{rank}. {label:25} "
            f"{bytes_:12} bytes ({byte_pct:6.2f}%) | "
            f"{packets_:10} pkts ({pkt_pct:6.2f}%)"
            )


def main():
    # Counters For Chart
    packet_counts = defaultdict(int)
    byte_counts = defaultdict(int)
  
   ## pickle cache ##
    if os.path.exists(cache_file):
        print("Loading cached results...")
        with open(cache_file, "rb") as f:
            data = pickle.load(f)

        packet_counts = data["packet_counts"]
        byte_counts = data["byte_counts"]
        total_packets = data["total_packets"]
        total_bytes = data["total_bytes"]

    else:
        print("No cache found. Parsing PCAPs...")
        total_packets, total_bytes = populate_dicts(packet_counts, byte_counts)
        print("\nDone With Files\n")

        # SAVE CACHE
        with open(cache_file, "wb") as f:
            pickle.dump({
                "packet_counts": packet_counts,
                "byte_counts": byte_counts,
                "total_packets": total_packets,
                "total_bytes": total_bytes
            }, f)

        print("Cache saved to", cache_file)

    top_N = get_top_N(byte_counts)
    rank_by_volume(top_N, packet_counts, byte_counts, total_packets, total_bytes)

    
if __name__ == "__main__":
    main()

