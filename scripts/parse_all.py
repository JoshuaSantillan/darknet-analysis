from scapy.all import rdpcap, IP, TCP, UDP, ICMP
path = "../data/pcaps/ucsd-nt.1660435200.pcap"
packets = rdpcap(path)
print(f"Total Packets: {len(packets)}")


for packet in packets:

    packet.show()
    # Print Packet Size
   # print(packet['IP'].len)


    #Print UDP Destination
   # if 'UDP' in packet:
   #     print(packet['UDP'].dst)
'''
    #Print TCP Destination
    if 'TCP' in packet:
        print(packet['TCP'].dport)

    #Print ICMP Codes
    if 'ICMP' in packet:
        print(packet('ICMP'].code, length)
'''
