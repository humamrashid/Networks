import sys
import socket

def get_netnum_brdaddr(addr, mask):
    netl = []
    brdl = []
    for a,m in zip(addr,mask):
      netl.append(a & m)
      brdl.append(a | (~m & 0xff))

    netnum = bytes(netl)
    brdaddr = bytes(brdl)

    return netnum,brdaddr

def usage(prog):
    print('Usage: ' + prog + ' ipv4address ipv4netmask', file=sys.stderr)

def main(argv):
    if len(argv) < 3:
        usage(argv[0])
        sys.exit(1)
    addr = socket.inet_pton(socket.AF_INET, argv[1])
    mask = socket.inet_pton(socket.AF_INET, argv[2])
    netnum,brdaddr =  get_netnum_brdaddr(addr, mask)
    print(netnum, socket.inet_ntop(socket.AF_INET, netnum))
    print(brdaddr, socket.inet_ntop(socket.AF_INET, brdaddr))

# to run as a script
if __name__ == '__main__':
    main(sys.argv)
