
from scapy.all import sniff, IP, TCP
import logging

# Configure logging
logging.basicConfig(filename='packet.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def packet_handler(packet):
    # Extract relevant information from the packet
    if IP in packet and TCP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport

        # Log packet information
        logging.info(f"Packet: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")

# Start sniffing for packets
print("Start sniffing")
sniff(prn=packet_handler, store=0)
print("Finish sniffing")


