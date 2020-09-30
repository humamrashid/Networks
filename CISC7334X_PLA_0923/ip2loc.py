# Humam Rashid

# CISC 7334X, Prof. Chen

from http import client as httpclient
import json
import sys

HOST = 'api.ipgeolocation.io'
API_KEY = 'YOUR_API_KEY'

def build_request(ip):
    request = '/ipgeo?apiKey=' + API_KEY + '&ip=' + ip + '&output=json'
    return request
    
def get_geo_loc(ip):  
    request = build_request(ip);
    conn = httpclient.HTTPSConnection(HOST)
    
    conn.request('GET', request)  
    response = conn.getresponse()  
    if response.status != 200:
        location = (False, response.status, json.loads(response.read()))
    else:
        location = (True, response.status, json.loads(response.read()))
    conn.close()  
    return location

def main():
    ips = [line.strip() for line in sys.stdin]
    for ip in ips:
        success,_,location = get_geo_loc(ip)
        if not success:
            print(ip, location['message'])
        else:
            print(ip, location['latitude'], location['longitude'])
            


if __name__ == "__main__":    
    # execute only if run as a script
    main()

# EOF.
