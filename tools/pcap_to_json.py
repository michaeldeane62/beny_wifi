import json
import sys
from scapy.all import rdpcap, UDP, IP

PCAP_FILE = "capture.pcap"
OUTPUT_FILE = "output.json"

def extract_udp_pairs(pcap_file):
    packets = rdpcap(pcap_file)
    transactions = []
    last_request = {}

    for pkt in packets:
        if pkt.haslayer(UDP) and pkt.haslayer(IP):
            src = str(pkt[UDP].sport)
            dst = str(pkt[UDP].dport)
            payload = bytes(pkt[UDP].payload).decode(errors="ignore")  # Decode to ASCII

            key = (pkt[IP].src, pkt[IP].dst, src, dst)
            reverse_key = (pkt[IP].dst, pkt[IP].src, dst, src)

            if key in last_request:
                transactions.append((last_request[key], payload))
                del last_request[key]
            else:
                last_request[reverse_key] = payload

    return {req: resp for req, resp in transactions}

def save_to_json(data, output_file):
    with open(output_file, "w") as f:
        json.dump({"responses": data}, f, indent=4)
    print(f"Saved {len(data)} request-response pairs to {output_file}")

if __name__ == "__main__":
    pcap_file = sys.argv[1] if len(sys.argv) > 1 else PCAP_FILE
    output_file = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE

    udp_pairs = extract_udp_pairs(pcap_file)
    save_to_json(udp_pairs, output_file)
