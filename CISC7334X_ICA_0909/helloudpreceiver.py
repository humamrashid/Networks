# Humam Rashid

# CISC 7334X, Prof. Chen

import socket

def main():
    brdipaddr = '192.168.56.101'
    udpport = 50001
    bufsize = 1024

    receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
            proto=0, fileno=None)

    brdaddr = (brdipaddr, udpport)
    receiver.bind(brdaddr)

    buf, senderaddr = receiver.recvfrom(bufsize)
    msg = buf.decode()
    print('Received announcement from ' + str(senderaddr) + ': ' + msg)

    receiver.close()


if __name__=='__main__':
    main()

# EOF
