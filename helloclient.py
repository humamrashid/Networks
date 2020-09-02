# Humam Rashid
# CISC 7334X, Prof. Chen

# Web Client Program using python.

from http import client as httpclient

def main():
    conn = httpclient.HTTPConnection('127.0.0.1:5000')

    conn.request('GET', '/')
    response = conn.getresponse()
    print(response.status, response.reason)

    received = response.read()
    print(received)

    conn.close()

if __name__ == "__main__":
    main()

# EOF.
