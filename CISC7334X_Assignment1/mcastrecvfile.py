# Humam Rashid

# CISC 7334X, Prof. Chen

import sys
import socket
import struct

BUFSIZE = 1024 # Feel free make this bigger, but how big can it be? 

def help_and_exit(prog):
    print('Usage: ' + prog + ' from_nic_by_host_ip mcast_group_ip mcast_port')
    sys.exit(1)

def write_file(filename, buf):
    with open(filename, 'wb') as f:
        f.write(buf)

def mc_recv_file(fromnicip, mcgrpip, mcport):
    # 1. create a UDP socket
    receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
            proto=socket.IPPROTO_UDP, fileno=None)
    # 2. configure the socket to receive datagrams sent to the desired 
    #    multicast end point 
    bindaddr = (mcgrpip, mcport)
    receiver.bind(bindaddr)
    # 3. join a NIC to the intended multicast group
    if fromnicip == '0.0.0.0':
        mreq = struct.pack("=4sl", socket.inet_aton(mcgrpip), socket.INADDR_ANY)
    else:
        mreq = struct.pack("=4s4s", \
                socket.inet_aton(mcgrpip), socket.inet_aton(fromnicip))
    receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    # 4. Receive the filename
    filename = mc_recv_msg(fromnicip, mcgrpip, mcport + 1)
    # 5. Receive file content of the file and write it to file
    (buf, _) = receiver.recvfrom(BUFSIZE)
    write_file(filename, buf)
    # 6. Release socket resources
    receiver.close()
    print(f'Completed: received {filename}')

def mc_recv_msg(fromnicip, mcgrpip, mcport):
    bufsize = 1024

    # This creates a UDP socket
    receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
            proto=socket.IPPROTO_UDP, fileno=None)

    # This configure the socket to receive datagrams sent to this multicast
    # end point, i.e., the pair of 
    #   (multicast group ip address, mulcast port number)
    # that must match that of the sender
    bindaddr = (mcgrpip, mcport)
    receiver.bind(bindaddr)

    # This joins the socket to the intended multicast group. The implications
    # are two. It specifies the intended multicast group identified by the
    # multicast IP address.  This also specifies from which network interface
    # (NIC) the socket receives the datagrams for the intended multicast group.
    # It is important to note that socket.INADDR_ANY means the default network
    # interface in the system (ifindex = 1 if loopback interface present). To
    # receive multicast datagrams from multiple NICs, we ought to create a
    # socket for each NIC. Also note that we identify a NIC by its assigned IP
    # address. 
    if fromnicip == '0.0.0.0':
        mreq = struct.pack("=4sl", socket.inet_aton(mcgrpip), socket.INADDR_ANY)
    else:
        mreq = struct.pack("=4s4s", \
            socket.inet_aton(mcgrpip), socket.inet_aton(fromnicip))
    receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Receive the mssage
    buf, senderaddr = receiver.recvfrom(BUFSIZE)
    msg = buf.decode()

    return msg

def main(argv):
    if len(argv) < 4:
        help_and_exit(argv[0])

    fromnicip = argv[1] 
    mcgrpip = argv[2]
    mcport = int(argv[3])

    mc_recv_file(fromnicip, mcgrpip, mcport)
    
if __name__=='__main__':
    main(sys.argv)

# EOF.
