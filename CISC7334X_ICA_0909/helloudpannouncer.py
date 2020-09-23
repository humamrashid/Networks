# Humam Rashid

# CISC 7334X, Prof. Chen

import socket

def main():
    brdipaddr ='192.168.56.255'
    udpport = 50001

    sender = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
            proto=socket.IPPROTO_UDP, fileno=None)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    brdaddr = (brdipaddr, udpport)
    msg = 'The registrar has released the final exam schedule.'
    buf = msg.encode()
    sender.sendto(buf, brdaddr)

    sender.close()

if __name__=='__main__':
    main()

# EOF.
