# Humam Rashid

# CISC 7334X, Prof. Chen

import sys
from scapy.layers.inet import IP
from scapy.layers.inet import ICMP
from scapy.sendrecv import sr1
from socket import gethostbyname

def print_route(hops, reply):
    nonemsg = '*****None******'
    unreachmsg = '*****None******'
    hopmsg = 'hops'
    typemsg = 'ICMP msg type '
    if hops == 1:
        hopmsg = 'hop'
    if reply is None:
        src = '*****None******'
        rtype = 'OOPS'
        typemsg = ''
    elif reply.type == 3:
        src = '**Unreachable**'
        rtype = reply.type
    else:
        src = reply.src
        rtype = reply.type

    print(f'{hops:2d} {hopmsg:4} away from {src:15} [{typemsg}{rtype:2}]')

    if not reply is None and reply.type == 0:
        print ('Desitnation reached')
        
def icmp_trace_route(dst):
    dstaddr = gethostbyname(dst)
    noops = 0
    print(f'Traceroute to {dst} at {dstaddr}:')
    for i in range(1, 65): # try 1 hops to 64 hops
        # prepare a ICMP packet (what type of ICMP message is it)?
        pkt = IP(dst=dstaddr, ttl=i) / ICMP()
        # Send the packet and get a reply
        reply = sr1(pkt, verbose=0, timeout=5)
        if reply is None:
            noops = noops + 1
            print_route(i, reply)
            if noops >= 5:
                break
        elif reply.type == 0:
            print_route(i, reply)
            break
        elif reply.type == 3:  # Destination Unreachable  (RFC 792)
            print_route(i, reply)
        elif reply.type == 11: # Time Exceeded (RFC 792)
            print_route(i, reply)
        else:  # Hi friend, How are you configured? Why am I getting this?
            print_route(i, reply)
        

def main(argv):
    if len(argv) < 2:
        print('Usage: ' + argv[0] + ' destination')
        sys.exit(1)
    dst = sys.argv[1]
    nodes = icmp_trace_route(dst)

if __name__=='__main__':
    main(sys.argv)

# EOF.
