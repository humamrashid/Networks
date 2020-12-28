# Team BKR

# CISC 7334X, Project 1, UDP SendFile, Fail-Fast version

# Sending program for UDPSendFile, common constants and functions are imported
# from udpsendfile_common.py

import os
import sys
import time
import udpsendfile_common as common

# Counts the number of blocks in a file (indicates number of packets that need
# to be sent)
def count_blocks(blocksize, datasize, filename):
    num_blocks = 1
    while datasize > blocksize:
        num_blocks += 1
        datasize -= blocksize
    return num_blocks

# Sends metadata for the file being sent (i.e., file name, data size, and file
# checksum), waits for feedback for each of the 3 types of metadata mentioned
# from receiver(s) before continuing on; the filename and checksum are only
# confirmed for being sent, the data size feedback may cause termination if the
# receiver(s) are unwilling to continue
def send_metadata(sender, endpoint, receiver, filename, datasize):
    # Transmit the filename in a packet
    # The filename is a byte string of FNAME_LEN length; the single-byte prefix
    # for filename is FNAME_OP
    fname_bytes = (common.FNAME_OP + filename[:common.FNAME_LEN]).encode()
    print('Filename sent:', fname_bytes)
    sender.sendto(fname_bytes, endpoint)
    packet, opcode, timedout = \
            common.get_packet(receiver, common.MAX_PACKET_SIZE, \
            common.BLOCKING_WAIT)
    if timedout:
        common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                + common.STOP_OP).encode(), endpoint, \
                'Timed out, aborting...', 1)
    if opcode != common.FEEDBACK_OP:
        common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                + common.STOP_OP).encode(), endpoint, \
                'Feedback invalid, aborting', 1)
    print('Filename feedback:', packet[1])

    # Transmit the data size in a packet
    # The data size is a byte string of DATASIZE_LEN length; the single-byte
    # prefix for data size is DATASIZE_OP
    datasize_bytes = (common.DATASIZE_OP \
            + str(datasize)[:common.DATASIZE_LEN]).encode()
    print('Data size sent:', datasize_bytes)
    sender.sendto(datasize_bytes, endpoint)
    packet, opcode, timedout = \
            common.get_packet(receiver, common.MAX_PACKET_SIZE, \
            common.BLOCKING_WAIT)
    if timedout:
        common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                + common.STOP_OP).encode(), endpoint, \
                'Timed out, aborting...', 1)
    if opcode != common.FEEDBACK_OP:
        common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                + common.STOP_OP).encode(), endpoint, \
                'Feedback invalid, aborting', 1)
    print('Data size feedback:', packet[1])
    if packet[1] == common.STOP_OP:
        common.release_rsrcs([sender, receiver])
        common.exit_err('Aborting due to receiver request...', 0)

    # Generate and transmit SHA-2 256-bit checksum for file being
    # transmitted in a packet, the hexadecimal digest transmitted is a
    # 64-byte string; the single-byte prefix for checksum is HASH_OP, the
    # string length of the digest is also found as HASH_LEN
    hexdigest = common.hash_file(common.BLOCKSIZE, filename)
    hexdigest_bytes = (common.HASH_OP + hexdigest).encode()
    print('Checksum sent:', hexdigest_bytes)
    sender.sendto(hexdigest_bytes, endpoint)
    packet, opcode, timedout = \
            common.get_packet(receiver, common.MAX_PACKET_SIZE, \
            common.BLOCKING_WAIT)
    if timedout:
        common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                + common.STOP_OP).encode(), endpoint, \
                'Timed out, aborting...', 1)
    if opcode != common.FEEDBACK_OP:
        common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                + common.STOP_OP).encode(), endpoint, \
                'Feedback invalid, aborting', 1)
    print('Checksum feedback:', packet[1])

# Sends a file
def mc_send_file(hostip, mcgrpip, mcport_send, mcport_recv, filename):
    datasize = os.stat(filename).st_size
    print(f'Sending file: {filename}\n')
    if datasize > (common.MAX_SEQ * common.BLOCKSIZE):
        print('WARNING: data size exceeds 1-petabyte, transmitted data will be'\
                + ' truncated!', file=sys.stderr)
    # 1. Get a socket to send data with and a socket to receive data with
    endpoint = (mcgrpip, mcport_send)
    sender = common.prep_sender(hostip)
    receiver = common.prep_receiver(hostip, mcgrpip, mcport_recv)
    # 2. Send metadata
    send_metadata(sender, endpoint, receiver, filename, datasize)

    # 3. Read the file and the transmit the file content in packets of BLOCKSIZE
    # data length; the single-byte prefix for file content is CONTENT_OP
    with open(filename, 'rb') as f:
       seq_num = 1
       more = '0'
       packets_left = count_blocks(common.BLOCKSIZE, datasize, filename)
       content_bytes = f.read(common.BLOCKSIZE)
       while content_bytes and seq_num <= common.MAX_SEQ:
           more = '1' if packets_left > 1 else '0'
           packet = common.CONTENT_OP.encode() \
                   + str(seq_num).zfill(common.SEQ_NUM_LEN).encode() \
                   + more.encode() \
                   + content_bytes
           sender.sendto(packet, endpoint)
           seq_num += 1
           packets_left -= 1
           content_bytes = f.read(common.BLOCKSIZE)
           time.sleep(common.PACKET_DELAY)

    # 4. Handle final feedback if any and release socket resources
    packet, opcode, timedout = \
            common.get_packet(receiver, common.MAX_PACKET_SIZE, \
            common.BLOCKING_WAIT)
    common.release_rsrcs([sender, receiver])
    if not timedout and opcode == common.FEEDBACK_OP:
        print('Final feedback:', packet[1])
        if packet[1] == common.ERROR_OP:
            common.exit_err(f'Error: could not properly send {filename}, ' \
                    + 'aborting...\n', 1)
        print(f'\nCompleted: sent {filename}', file=sys.stderr)
    else:
        print('Unable to confirm final transmission status')

# Runs the program, parameters are as follows:
# 
# 1. host ip address
# 2. multicast group ip address
# 3. sending port
# 4. receiving port
# 5. name of file to send
def main(argv):
    if len(argv) != 6:
        common.exit_err('Usage: ' + argv[0] + ' host_ip mcast_group_ip ' \
                + 'mcast_port_send mcast_port_recv file_to_send', 1)
    hostipaddr = argv[1]
    mcgrpipaddr = argv[2]
    mcport_send = int(argv[3])
    mcport_recv = int(argv[4])
    filename = argv[5]
    if not os.path.isfile(filename):
        common.exit_err(f'File: {filename} not found!', 1)
    mc_send_file(hostipaddr, mcgrpipaddr, mcport_send, mcport_recv, filename)

if __name__=='__main__':
    main(sys.argv)

# EOF.
