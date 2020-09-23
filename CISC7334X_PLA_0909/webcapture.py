# Humam Rashid
# CISC 7334X, Prof. Chen

from scapy.sendrecv import sniff
from scapy.utils import wrpcap

def main():
    packets = sniff(prn=lambda x: x.summary(), filter="tcp port 5000", count=12)
    wrpcap('hello.pcap', packets)
                
if __name__ == "__main__":
    main()

# EOF.
