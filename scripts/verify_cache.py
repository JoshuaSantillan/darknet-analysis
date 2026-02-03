import pickle

with open("../output/packet_len_cache.pkl", "rb") as f:
    cache = pickle.load(f)

print(len(cache))                           # should be ~168
first_key = list(cache.keys())[0]
print(len(cache[first_key]))                # large number
print(cache[first_key][0])                  # e.g., 74

