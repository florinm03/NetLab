from scapy.all import rdpcap
import json
import sys
import os

def parse_pcap(file_path):
    packets = rdpcap(file_path)
    connections = {}

    for pkt in packets:
        if pkt.haslayer('IP'):
            src = pkt['IP'].src
            dst = pkt['IP'].dst
            key = (src, dst)
            if key not in connections:
                connections[key] = 0
            connections[key] += 1

    result = []
    for (src, dst), count in connections.items():
        result.append({
            "source": src,
            "destination": dst,
            "packets": count
        })

    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_pcap.py <file.pcap>")
        sys.exit(1)

    file_path = sys.argv[1]
    connection_data = parse_pcap(file_path)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}_connections.json"

    with open(output_file, "w") as f:
        json.dump(connection_data, f, indent=2)

    print(f"{output_file} created!")
