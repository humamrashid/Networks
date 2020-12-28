# Team BKR

# CISC 7334X, Project 1, UDP SendFile

# UDP SendFile common constants and functions; sizes are in bytes unless
# otherwise noted

import sys
import socket
import struct
import hashlib

# Packet type opcodes
## Filename opcode
FNAME_OP    = '1'
## Data size opcode
DATASIZE_OP = '2'
## Checksum hash opcode
HASH_OP     = '3'
## File content opcode
CONTENT_OP  = '4'
## Feedback opcode
FEEDBACK_OP = '5'

# Feedback indicator opcodes:
## Success opcode
DONE_OP     = 'D'
## Error opcode
ERROR_OP    = 'E'
## Acknowldegement opcode (positive)
ACK_OP      = 'A'
## Acknowledgement opcode (negative)
NAK_OP      = 'N'
## Stop request opcode
STOP_OP     = 'S'

# UDP packet sending delay (in seconds), so as not to overwhelm OS read buffer
# Delays under 100 ms preferred
PACKET_DELAY = 0.005

# Length of file name
FNAME_LEN = 1024

# Max data size is 1-petabyte, represented by a max 16-byte string
DATASIZE_LEN = 16

# Hexadecimal digest for SHA-2 256-bit string length
HASH_LEN = 64

# Block size for reading and transmitting data from a file
BLOCKSIZE = 1024

# Max sequence number; 2^40
MAX_SEQ = 1_099_511_627_776
# Max sequence number for file content packets; string length
SEQ_NUM_LEN = 13

# Waiting time for feedback (in seconds)
BLOCKING_WAIT = 5

# Maximum packet size; this is the size of the file content packet, a sum of the
# file content bytes max size (BLOCKSIZE), the more flag (1 byte), max sequence
# string length (SEQ_NUM_LEN) and the file content opcode (CONTENT_OP, 1 byte)
#
# This value is needed because UDP SendFile does not make assumptions about the
# type of packet received until the opcode is read, hence the receivers must
# always assume the possibility that the largest possible size of any given
# packet defined by the protocol has been sent
MAX_PACKET_SIZE = BLOCKSIZE + 1 + SEQ_NUM_LEN + 1

# Returns a socket for sending data from specified NIC; user is responsible for
# releasing socket resources when appropriate
def prep_sender(hostip):
    # 1. Create a UDP socket
    sender = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
            proto=socket.IPPROTO_UDP, fileno=None)
    # 2. Set up IP_MULTICAST_TTL
    sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    # 3. Set up transmitting NIC for multicast packets
    sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, \
            socket.inet_aton(hostip))
    return sender

# Returns a socket for receiving data from specified NIC at given endpoint; user
# is responsible for releasing resources when appropriate
def prep_receiver(fromnicip, mcgrpip, mcport):
    # 1. Create a UDP socket
    receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
           proto=socket.IPPROTO_UDP, fileno=None)
    receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 2. Configure the socket to receive datagrams sent to the desired
    # multicast end point
    endpoint = (mcgrpip, mcport)
    receiver.bind(endpoint)
    # 3. Join a NIC to the intended multicast group
    if fromnicip == '0.0.0.0':
        mreq = struct.pack("=4sl", socket.inet_aton(mcgrpip), socket.INADDR_ANY)
    else:
        mreq = struct.pack("=4s4s", socket.inet_aton(mcgrpip), \
                socket.inet_aton(fromnicip))
    receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return receiver

# Get the SHA-2 256-bit checksum hexadecimal digest for given file
def hash_file(bsize, filename):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        buf = f.read(bsize)
        while buf:
            hasher.update(buf)
            buf = f.read(bsize)
    return hasher.hexdigest()

# Get tuple of (decoded packet, opcode, timed_out) with given receiver socket,
# packet size limit and time out wait period
#
# Time out wait period accepts 3 value ranges:
# 
# 0     -> non-blocking
# None  -> blocking
# n     -> wait for n seconds, where n is a positive integer
def get_packet(receiver, packet_size, timeout_wait):
    decoded = None
    receiver.settimeout(timeout_wait)
    try:
        packet, _ = receiver.recvfrom(packet_size)
        decoded = packet.decode()
    except socket.timeout:
        return (None, None, True)
    return (decoded, decoded[0], False)

# Convenience function for exiting with error
def exit_err(msg, err):
    print(msg, file=sys.stderr)
    sys.exit(err)

# Convenience function for closing sockets
def release_rsrcs(rsrcs_arr):
    for r in rsrcs_arr:
        r.close()

# Convenience function for making a clean exit
def make_clean_exit(sender, receiver, feedback, endpoint, err_msg, err_code):
    sender.sendto(feedback, endpoint)
    release_rsrcs([sender, receiver])
    exit_err(err_msg, err_code)

# EOF.
