# Humam Rashid
# CISC 7334X, Prof. Chen

# Web client program using python.

from http import client as httpclient

def main():
    conn = httpclient.HTTPConnection('192.168.1.41:5000')

    conn.request('GET', '/helloworld')
    response = conn.getresponse()
    print(response.status, response.reason)

    received = response.read()
    print(received)

    conn.close()

if __name__ == "__main__":
    main()

# EOF.
