# Team BKR

# CISC 7334X, Project 1, UDP SendFile, Fail-Fast version

# Receiving program for UDP SendFile, common constants and functions are
# imported from udpsendfile_common.py

import os
import shutil
import sys
import udpsendfile_common as common

def help_and_exit(argv):
    common.exit_err('Usage: ' + argv[0] + ' -i|-b from_nic_by_host_ip ' \
            + 'mcast_group_ip mcast_port_recv mcast_port_send', 1)

# Write the given bytes to given filename based on the given sequence number,
# uses less memory but requires the function to be called for every packet
def write_bytes(filename, bsize, seq_num, content_bytes):
    mode = 'wb' if not os.path.isfile(filename) else 'r+b'
    with open(filename, mode) as f:
        f.seek((seq_num - 1) * bsize, 0)
        f.write(content_bytes)

# Write the given buffer to given filename by appending (if the file does not
# already exist), uses more memory but can write the entire file with one call
def write_buffer(filename, content_buffer):
    mode = 'wb' if os.path.isfile(filename) else 'ab'
    with open(filename, mode) as f:
        for i in range(1, len(content_buffer) + 1):
            f.write(content_buffer[i])

# Receives metadata for the file being sent (i.e., file name, data size, and
# file checksum), sends feedback for each of the 3 types of metadata mentioned
# to sender before continuing on; the filename and checksum feedback only
# indicates reception but the data size feedback asks for termination if there
# is not enough free space for the file
def recv_metadata(receiver, sender, endpoint):
    filename_rcvd = False
    datasize_rcvd = False
    checksum_rcvd = False
    # Check free space on current working directory
    _, _, free = shutil.disk_usage(__file__)
    # Wait for metadata
    while not filename_rcvd or not datasize_rcvd or not checksum_rcvd:
        packet, opcode, _ = \
                common.get_packet(receiver, common.MAX_PACKET_SIZE, None)
        if opcode == common.FEEDBACK_OP and packet[1] == common.STOP_OP:
            common.release_rsrcs([sender, receiver])
            common.exit_err('Aborting due to sender request...', 0)
        # Receive the filename packet
        # The filename is a byte string of FNAME_LEN length; the single-byte
        # prefix for filename is FNAME_OP
        if opcode == common.FNAME_OP:
            filename = packet[1:common.FNAME_LEN + 1]
            filename_rcvd = True
            print("Filename received:", filename)
            sender.sendto((common.FEEDBACK_OP + common.ACK_OP).encode(), \
                    endpoint)
        # Receive the data size packet
        # The data size is a byte string of DATASIZE_LEN length; the single-byte
        # prefix for data size is DATASIZE_OP
        if opcode == common.DATASIZE_OP:
            datasize = int(packet[1:common.DATASIZE_LEN + 1])
            datasize_rcvd = True
            print("Data size received:", datasize)
            if free < datasize:
                # Tell sender to stop sending anything and exit.
                common.make_clean_exit(sender, receiver, (common.FEEDBACK_OP \
                        + common.STOP_OP).encode(), endpoint, f'Not enough ' \
                        + 'free space available for file, aborting...', 1)
            sender.sendto((common.FEEDBACK_OP + common.ACK_OP).encode(), \
                    endpoint)
        # Receive the remote checksum packet
        # The checksum is a 64-byte string hexadecimal digest; the single-byte
        # prefix for checksum is HASH_OP, the string length of the digest is
        # also found as HASH_LEN
        if opcode == common.HASH_OP:
            checksum = packet[1:common.HASH_LEN + 1]
            checksum_rcvd = True
            print("Checksum received:", checksum)
            sender.sendto((common.FEEDBACK_OP + common.ACK_OP).encode(), \
                    endpoint)
    return (filename, datasize, checksum)

# Receives a file
def mc_recv_file(fromnicip, mcgrpip, mcport_recv, mcport_send, use_buffer):
    # 1. Get a socket to receive data with and a socket to send data with
    receiver = common.prep_receiver(fromnicip, mcgrpip, mcport_recv)
    endpoint = (mcgrpip, mcport_send)
    sender = common.prep_sender(fromnicip)
    # 2. Receive metadata
    filename, datasize, remote_checksum = recv_metadata(receiver, sender, \
            endpoint)

    # The buffer is just a hash table, where each key is a sequence number and
    # each value is the file content in bytes; this is only used if the option
    # is chosen by user
    content_buffer = {}

    # 3. Receive file content
    more = '1'
    while True:
       if more == '1':
           packet, opcode, _ = \
                   common.get_packet(receiver, common.MAX_PACKET_SIZE, None)
           if opcode != common.CONTENT_OP:
               continue
       else:
           break
       seq_num = int(packet[1:common.SEQ_NUM_LEN + 1])
       print("Received file packet number:", seq_num)
       more = packet[common.SEQ_NUM_LEN + 1:common.SEQ_NUM_LEN + 2]
       content = packet[common.SEQ_NUM_LEN + 2:common.BLOCKSIZE \
               + common.SEQ_NUM_LEN + 2]
       if not use_buffer:
           write_bytes(filename, common.BLOCKSIZE, seq_num, content.encode())
       else:
           content_buffer[seq_num] = content.encode()

    # Write the buffer to the file if user picked this option
    if use_buffer:
        write_buffer(filename, content_buffer)

    # 4. Check if local data matches remote and send feedback
    error = None
    local_checksum = common.hash_file(common.BLOCKSIZE, filename)
    if local_checksum != remote_checksum:
       sender.sendto((common.FEEDBACK_OP + common.ERROR_OP).encode(), endpoint)
       error = True
    else:
        sender.sendto((common.FEEDBACK_OP + common.DONE_OP).encode(), endpoint)
        error = False
    print("Checksum of local data:", local_checksum)

    # 5. Release socket resources and indicate success/error to user
    common.release_rsrcs([sender, receiver])
    if error:
        common.exit_err(f'Error: could not properly receive {filename}, ' \
                + 'aborting...\n', 1)
    else:
        print(f'Completed: received {filename}\n', file=sys.stderr)

# Runs the program, parameters are as follows:
# 
# 1. incremental or buffered file writing
# 2. host ip address
# 3. multicast group ip address
# 4. receiving port
# 5. sending port
def main(argv):
    if len(argv) != 6:
        help_and_exit(argv)
    use_buffer = None
    if argv[1] == '-b':
        use_buffer = True
    elif argv[1] == '-i':
        use_buffer = False
    else:
        help_and_exit(argv)
    fromnicip = argv[2]
    mcgrpip = argv[3]
    mcport_recv = int(argv[4])
    mcport_send = int(argv[5])
    mc_recv_file(fromnicip, mcgrpip, mcport_recv, mcport_send, use_buffer)
    
if __name__=='__main__':
    main(sys.argv)

# EOF.
