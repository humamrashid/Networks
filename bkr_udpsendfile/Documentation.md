# UDP SendFile App Documentation

---

## GENERAL INFORMATION

## 1. Implementations

There are two separate implementations: A "Fail-Fast" version under
UDPSendFileApp and a lightweight "ARQ" version under UDPSendFileApp/ARQ_version.
Both versions make use of timers and feedback but the method and nature of use
is significantly different.

In the Fail-Fast version, the sender is meant to make minimal use of feedback
within a protocol-defined time limit and otherwise prefer to terminate. Neither
sender nor receiver uses any feedback for file content transmission and its use
is reserved for metadata transmission and a final file content integrity check.

In the lightweight ARQ version, both the sender and receivers communicate with
each other through the feedback mechanism for metadata, file content
transmission and the final content integrity check. A positive acknowledgment
feedback is expected by the sender and sent by receivers for each segment of
data transmitted and received in order, whereas a negative acknowledgment from
receiver to sender or simply the lack of positive feedback induces repeated
transmission of the same segment.

**Note**: Both of the implementations coded are intended to be compliant with
the protocol and all of the following apply to both implementations unless
otherwise stated.

## 2. File structure

- **mcastsendfile.py**: This is the file run by the "sender" host.

- **mcastrecvfile.py**: This is the file run by "receiver" hosts(s).

- **udpsendfile_common.py**: This file includes constants and functions used by
both of the above files.

In any given run, there is only one sender host but there could be more than one
receiver host. The application has been designed to run on Python 3.7.x based on
what is available on the VMs. The sender and receiver(s) could be on the same
machine or different ones. Manual testing has been performed in both scenarios.

## 3. Brief descriptions of major functions by file
(Descriptions are based on the source code comments)

### udpsendfile_common.py:
(Imported by mcastsendfile.py and mcastrecvfile.py as "common")

1. **prep_sender()**: Returns a socket for sending data from specified NIC; user
is responsible for releasing socket resources when appropriate.

2. **prep_receiver()**: Returns a socket for receiving data from specified NIC at
given endpoint; user is responsible for releasing resources when appropriate.

3. **hash_file()**: Get the SHA-2 256-bit checksum hexadecimal digest for given
file.

4. **get_packet()**: Get tuple of (decoded packet, opcode, timedout) with given
receiver and packet size. Final argument (timedout) indicates whether a timer
that was selectively set upon using the receiver has run out.

(Various constants are present in this file and a few very important ones are
discussed in this document)

### mcastsendfile.py:
(Parameter discussion given for **main()** only)

1. **main()**: Runs the program, parameters are as follows:
    1. host IP address
    2. multicast group IP address
    3. sending port
    4. receiving port
    5. name of file to send

(**main()** is run automatically when the program is run)

2. **mc_send_file()**: Sends a file, the primary work-horse of the sender.

3. **send_metadata()**: Sends metadata for the file being sent (i.e., file name,
data size, and file checksum), waits for feedback for each of the 3 types of
metadata mentioned from receiver(s) before continuing on; the filename and
checksum are only confirmed for being sent, the data size feedback may cause
termination if the receiver(s) are unwilling to continue.

4. **count_blocks()**: Counts the number of blocks in a file (indicates number of
packets that need to be sent)

### mcastrecvfile.py:
(Parameter discussion given for **main()** only)

1. **main()**: Runs the program, parameters are as follows:
    1. incremental (-i) or buffered file writing (-b)
    2. host IP address
    3. multicast group IP address
    4. receiving port
    5. sending port

(**main()** is run automatically when the program is run)

3. **mc_recv_file()**: Receives a file, the primary work-horse of the receiver(s)

4. **recv_metadata()**: Receives metadata for the file being sent (i.e., file
name data size, and file checksum), sends feedback for each of the 3 types of
metadata mentioned to sender before continuing on; the filename and checksum
feedback only indicates reception but the data size feedback asks for
termination if there is not enough free space for the file

5. **write_bytes()**: Write the given bytes to given filename based on the given
sequence number (uses less memory but many calls)

6. **write_buffer()**: Write the give buffer to given filename (uses more memory
but can write the entire file in a single call)

---

## PACKET / FEEDBACK TYPES

### Packet type indicators (leftmost byte):

- <**'1'**> -> Filename packet

- <**'2'**> -> Data size packet

- <**'3'**> -> Checksum packet

- <**'4'**> -> File content packet

- <**'5'**> -> Feedback packet

### Feedback type indicators (after leading byte in feedback packet):

- <**'D'**> -> Done (post-transmission data integrity check passed)

- <**'E'**> -> Error (post-transmission data integrity check failed)

- <**'A'**> -> Acknowledgment (positive, used for other than file content in ARQ
version)

- <**'N'**> -> Acknowledgment (negative, only used in ARQ version)

- <**'S'**> -> Stop request

Note that all of the above and more have appropriately named constants in the
udpsendfile_common.py modules for each implementation.

There is one more ARQ-version specific feedback, the segment-specific positive
acknowledgment feedback:

- <**seq_num**> -> This is a zero-padded, 13 digit integer between 1 and 2^40,
inclusive.

---

## FRAGMENTATION & REASSEMBLY

Files larger than BLOCKSIZE (=1024) bytes are split into fragments, sequentially
numbered and sent in presumably sequential order. The delay packet delay
constant (described below) plays the most important role in attempting to
properly sequence transmission of segmented packets in the fail-fast
implementation.

In the ARQ implementation, the packet delay works together with the automatic
repeats in order to improve proper sequencing. Both implementations being
compliant with the protocol, use a more flag to signal ongoing or ending
transmission of packets.

---

## PRESET TIMERS & DELAYS

The following constants are of special importance and play a major role in
managing successful transmission.

- **BLOCKING_WAIT**: A constant indicating the number of seconds to wait for
feedback or any other type of response subject to a timer.

- **PACKET_DELAY**: A constant indicating the number of seconds to wait between
transmitting a packet from sender to receiver(s). In practice, this is a value
in milliseconds (e.g., 0.005 seconds).

---

## DATA INTEGRITY

We chose the Secure Hash Algorithm version 2 (SHA-2), 256-bit cryptographic hash
function to introduce data integrity checking to our protocol and in both
implementations. As of this writing, no publicly known successful attack has yet
taken place against SHA-2. The hashlib module from the Python standard library
is used to generate the 64-byte hexadecimal digests.

---

## TRANSMISSION PROCEDURE

The receiver(s) are started followed by the sender. New to this update is the
choice of the user to use either incremental file writing or  a buffered
(all-at-once) method. The '-i' or '-b' option is given to the receiver as first
argument to indicate incremental or buffered respectively.

The sending of data (file content) and metadata (filename, data size, checksum)
is separated. The metadata is sent first and the sender does not continue until
it receives feedback (indicating reception) for each type of metadata. The
receiver(s) also wait until all of the metadata has been received before
continuing on. Feedback for data size requests termination if there is not
enough disk space on the receiver(s); in this case the receiver(s) exit with
error condition (1) and sender is expected to do the same.

In the incremental file writing method, the sender sends the file contents in a
sequence of packets of 1024 bytes size and the receiver writes each of the
packets received into a file with the position calculated according to the
sequence number (using seek() from python file I/O library).

In the buffered file writing method, the sender also sends the file contents in
a sequence of packets of 1024 bytes size but the receiver writes them to a file
at once after receiving all file content packets.

For the case of the Fail-Fast implementation, if the BLOCKING_WAIT time period
is lapsed whenever the sender is waiting for acknowledgment or response
regarding metadata reception, the sender terminates immediately and asks the
receiver to do the same. For the final data integrity check, the sender waits
for the same period and unless an error response is heard from the receiver(s),
it assumes success and quits.

For the case of the lightweight ARQ implementation, the sender repeatedly sends
metadata and file content unless a positive acknowledgment is received from a
receiver. The sender also waits without a timer for feedback regarding the final
data integrity check. The positive acknowledgment for file content in particular
consists of a feedback-type packet followed by the same segment number (i.e.,
sequence number) the acknowledgment is a response to. Duplicate transmissions of
the same segment are ignored by the receiver and the same acknowledgment is sent
to reconfirm reception.

In case the final data integrity check fails and sender receives appropriate
response, both sender and receiver terminate with an appropriate error message
with error condition (1).

---

## LIMITATIONS ADDRESSED

Relative to the limitations we set out to tackle, the following is our current
assessment:

1. Along with other metadata, the data size is sent to the receiver(s) before
   transmission of file content and the receiver(s) ask to stop transmission if
   enough free space is not available on their host system. Furthermore, larger
   files than 1024 bytes are segmented and sent ordered and with sufficient
   metadata for reassembly at the receiving hosts.

2. The separation of metadata and file content transmission and their forced
   transmission in consecutive order takes care of the any potential issues
   regarding the reception of metadata and content out-of-sync.

3. Rigorous data integrity checking is performed before and after data
   transmission through the use of the SHA-2 256-bit hashing algorithm.

---

## ISSUES (addressed or otherwise)

## 1. Communication and feedback
The major outstanding issue is that there is no guarantee for successfully
sending or receiving a packet with UDP, hence sometimes waiting for feedback
causes hangups. UDP sends packets in a connectionless, "best-effort" manner,
hence there is no way to check if something sent by the sender was received by a
receiver unless the receiver sends feedback indicating so (and of course this
feedback packet may itself never arrive, continuing the chain of
feedback-awaiting). This  issue was reduced significantly through packet delays
and repeats.

## 2. Receivers unknown and indeterminate feedback
Related to above is that the sender has no idea who the receivers are. We can
get the IP address of the receivers by means of feedback but as above the
reception of feedback is not guaranteed and hence there is no reliable way for
the sender to check who the receivers are or how many there are. The other major
problem arising from this is that when feedback is actually received, the sender
cannot ascertain if this feedback was given by only one or all of the receivers.
For example, it may be that only one receiver sent the feedback for filename
received whereas the other did not, or only one receiver asked to terminate
because of low disk space. In these cases, the sender can only assume feedback
received, not from whom or how many.

## 3. Packet loss and unordered transmission/reception
Packets are sometimes dropped or transmitted out of order; no complete
workaround is present for dropped packets. Packet dropping was reduced
significantly (almost completely in the case of "small" to "medium-sized" files)
and ordering almost guaranteed through the use of packet delays and repeats. For
larger files (over 1 GB), occasional packet drop is sometimes found, though
tweaking packet delay time and transmission block size helps reduce or eliminate
this too.

## Afterword

Some of the above problems are endemic to UDP and are part of the reason TCP
exists (to facilitate robust 2-way communication between 2 parties, at the
expense of broadcast, multicast and single-packet speed). To take some relevant
excerpts from Wikipedia (on UDP):

"It [UDP] has no handshaking dialogues, and thus exposes the user's program to
any unreliability of the underlying network; there is no guarantee of delivery,
ordering, or duplicate protection"

"Lacking reliability, UDP applications must be willing to accept some packet
loss, reordering, errors or duplication."

Having faced all of the above issues over the course of the development time, we
have tried to reduce the issues as much as possible, short of a complete
heavyweight ARQ system or unicast-only TCP-like implementation.

---

## Revisions

**Current (Revision 2):**

Made on 10/28/2020.

Relative to revision 1:

- ACK feedback for file content is now segment-specific.
- Previous versions of documentation now considered obsolete.

Relative to original documentation:

- Two separate versions of the implementation concurrent (Fail-Fast, ARQ).
- Several issues mentioned in previous version partially or fully addressed.

---

CISC 7334X

Team BKR

Fall 2020

Brooklyn College
