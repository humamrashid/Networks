# Humam Rashid

# CISC 7334X, Prof. Chen

import socket

def main():
    serveripaddr = '127.0.0.1'
    serverport = 50001
    bufsize = 1024

    client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, \
            proto=0, fileno=None)
    serveraddr = (serveripaddr, serverport)
    client.connect(serveraddr)

    buf = client.recv(bufsize)
    msg = buf.decode()
    print('Server says: \'' + msg + '\'')

    msg = 'Hey, I am the client. Not much, server.' 
    buf = msg.encode()
    client.send(buf)

    client.close()

if __name__ == '__main__':
    main()

# EOF.
