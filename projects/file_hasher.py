#!/usr/bin/python3

import sys
import hashlib

def hash_file(bsize, filename):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        buf = f.read(bsize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(bsize)
    return hasher.hexdigest()

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <blocksize> <filename>")
        sys.exit(1)
    n = int(sys.argv[1])
    if n <= 0:
        print("Usage: block size must be greater than zero!")
        sys.exit(2)
    print(hash_file(n, sys.argv[2]))

if __name__ == '__main__':
    main()

# EOF.
