import sys
import socket

def get_netnum_brdaddr(addr, plen):
    netnumi = int.from_bytes(addr, byteorder='big') >> (32 - plen) << (32 - plen)
    nmaski = 0xffffffff >> plen
    brdaddri = netnumi | nmaski
    netnum = netnumi.to_bytes(4, byteorder='big')
    brdaddr = brdaddri.to_bytes(4, byteorder='big')
    return netnum,brdaddr

def usage(prog):
    print('Usage: ' + prog + ' ipv4address/prefix', file=sys.stderr)
    
def main(argv):
    if len(argv) < 2:
        usage(argv[0])
        sys.exit(1)
    addrp,plenp = sys.argv[1].split('/')
    addr = socket.inet_pton(socket.AF_INET, addrp)
    plen = int(plenp)
    netnum,brdaddr =  get_netnum_brdaddr(addr, plen)
    print(netnum, socket.inet_ntop(socket.AF_INET, netnum))
    print(brdaddr, socket.inet_ntop(socket.AF_INET, brdaddr))

# to run as a script
if __name__ == '__main__':
    main(sys.argv)
