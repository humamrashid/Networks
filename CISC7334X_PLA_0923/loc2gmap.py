# Humam Rashid

# CISC 7334X, Prof. Chen

import sys
from gmplot import GoogleMapPlotter 

def get_ip_locs():
    locs = [line.split() for line in sys.stdin]

    lat_list = [float(loc[1]) for loc in locs]
    lon_list = [float(loc[2]) for loc in locs]
    lbl_list = [loc[0] for loc in locs]

    lat_center = sum(lat_list)/len(lat_list)
    lon_center = sum(lon_list)/len(lon_list)

    return lat_list,lon_list,lbl_list,lat_center,lon_center

def main(map_html_fn):
    lat_list,lon_list,lbl_list,lat_center,lon_center = get_ip_locs()


    gmap = GoogleMapPlotter(lat_center, lon_center, 13)

    gmap.scatter(lat_list, lon_list, '#3B0B39', size=200, marker=False ) 
    for lat,lon,lbl in zip(lat_list,lon_list,lbl_list):
        gmap.text(lat, lon, color='#3B0B39', text=lbl)
  
    gmap.plot(lat_list, lon_list,  'cornflowerblue', edge_width = 2.5)
  
    gmap.draw(map_html_fn) 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: loc2gmap.py YOUR_MAP_NAME.html')
        sys.exit(1)
    main(sys.argv[1])

# EOF.
