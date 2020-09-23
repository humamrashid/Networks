# Humam Rashid
# CISC 7334X, Prof. Chen.

from http import client as httpclient
import time

def main():
    conn = httpclient.HTTPConnection('192.168.56.101:5000')
    conn.request('GET', '/')
    time.sleep(10)
    response = conn.getresponse()
    print(response.status, response.reason)
    received = response.read()
    print(received)
    conn.close()

if __name__ == "__main__":
    main()

# EOF.
