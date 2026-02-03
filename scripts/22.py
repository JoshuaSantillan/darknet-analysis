import os
import matplotlib.pyplot as plt
import json
import pickle
from collections import defaultdict

metadata_dir = "../data/metadata/"
len_cache_file = "../output/packet_len_cache.pkl"
cache_file = "../output/parsed_22.pkl"
as_orgs_file = "../data/20230101.as-org2info.txt"

def hour_dict():
    return defaultdict(int)

def parse_metadata(packet_len_cache):
    '''
    Aggregates:
     - total bytes per country
     - total bytes per ASN
     - bytes per country per hour
    '''
    
    country_bytes = defaultdict(int)
    asn_bytes = defaultdict(int)
    country_hour_bytes = defaultdict(hour_dict)

    meta_files = sorted([
        f for f in os.listdir(metadata_dir)
        if f.endswith(".json")
    ])

    count = 1
    for meta_file in meta_files:
        file_key = meta_file.replace(".json", "")
        timestamp = int(file_key.split(".")[1])
        hour_index = count - 1 #0-167 ordering
        count += 1 

        print(f"Processing [{hour_index}]: {meta_file}")
        
        with open(os.path.join(metadata_dir, meta_file)) as f:
            metadata = json.load(f)

        pkt_len_map = packet_len_cache[file_key]

        for record in metadata:
            pkt_count = record["PacketCnt"]
            pkt_len = pkt_len_map[pkt_count - 1]
            
            # Prefer Netacq, fallback to MaxMind
            country = record["NetacqCountry"] or record ["MaxmindCountry"] or "UNKNOWN"
            asn = record["SrcASN"] or "UNKNOWN"

            country_bytes[country] += pkt_len
            asn_bytes[asn] += pkt_len
            country_hour_bytes[country][hour_index] += pkt_len

    return country_bytes, asn_bytes, country_hour_bytes

def rank_top_n(counter_dict, n = 10):
    return sorted(
        counter_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )[:n]

def print_table(title, rows, label):
    print(f"\n{title}")
    for rank, (key, value) in enumerate(rows, start=1):
        print(f"{rank:2}. {label}: {key:15} {value:12} bytes")

def load_as_org_info(path):
    orgs={}
    with open(path, "r", errors="ignore") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts= line.strip().split("|",4) # | is delimitter in as2org file, at most 4 times
            if len(parts) != 5:
                continue ## invalid line
            
            org_id, _, org_name, country, _ = parts
            orgs[org_id] = (org_name, country)

    return orgs

def print_asn_org_context(top_asns, as_orgs):
    print("\nTop 10 Source ASN by Byte Volume (With Organizations")
    for rank, (asn, bytes_) in enumerate(top_asns, start=1):
        org = as_orgs.get(asn, ("Unknown Org", "??"))
        print(
            f"{rank:2}. ASN: {asn:10} "
            f"{bytes_:12} bytes | "
            f"{org[0]} ({org[1]})"
        )

def plot_time(country_hour_bytes, top_countries):
    plt.figure(figsize=(12,6))

    for country, _ in top_countries:
        hours = sorted(country_hour_bytes[country].keys())
        values = [country_hour_bytes[country].get(h,0)/(1024*1024) for h in hours]
        plt.plot(hours,values, label=country)

        plt.xlabel("Hours(0-167)")
        plt.ylabel("Traffic Volume per Hour (MiBs)")
        plt.title("Darknet Traffic Volume Over Time (top 10 countries)")
   
    plt.xlim(0,171)
    plt.legend()
    plt.tight_layout()
    plt.annotate("~23 MB/hr", xy=(102, 23), xytext=(85, 22),
             arrowprops=dict(arrowstyle="->"))
    plt.show()

def main():
    with open(len_cache_file, "rb") as f:
        packet_len_cache = pickle.load(f)
  
    if os.path.exists(cache_file):
        print(f"Loading caches results in {cache_file}...")
        with open(cache_file, "rb") as f:
            data = pickle.load(f)

        country_bytes = data["country_bytes"]
        asn_bytes = data["asn_bytes"]
        country_hour_bytes = data["country_hour_bytes"]

    else:
        print("No cache found, parsing metadata")
        country_bytes, asn_bytes, country_hour_bytes = parse_metadata(packet_len_cache) 
        
        with open(cache_file, "wb") as f:
            pickle.dump({
                "country_bytes": country_bytes,
                "asn_bytes": asn_bytes,
                "country_hour_bytes": country_hour_bytes
            }, f)

    top_countries = rank_top_n(country_bytes)
    top_asns = rank_top_n(asn_bytes)
    as_orgs_info = load_as_org_info(as_orgs_file)
    # Total Bytes Received by a single unused /24 per hour

    print_table("Top 10 Source Countries by Byte Volume", top_countries, "Country")
    print_table("Top 10 Source ASNs by Byte Volume", top_asns, "ASN") 
    print_asn_org_context(top_asns, as_orgs_info) 
    plot_time(country_hour_bytes, top_countries)

if __name__ == "__main__":
    main()
