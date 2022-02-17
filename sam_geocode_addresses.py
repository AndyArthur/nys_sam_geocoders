#!/usr/bin/python
# This script geocodes addresses using the state geocoder.

import requests,sys,json,csv,os
 
query = '{"records": ['
f = open(sys.argv[-1], 'r+')
with open(sys.argv[-1]) as f:
    i = 0
    for line in f:
        query += '{ "attributes": { "OBJECTID":'+str(i)+', "SINGLELINE": "'+line.rstrip()+'"} },'+"n"
        i+=1   
query += ']}'
 
post = { 'f':'pjson', 'outSR': 4326, 'addresses': query }
url = 'https://gisservices.its.ny.gov/arcgis/rest/services/Locators/Street_and_Address_Composite/GeocodeServer/geocodeAddresses'
 
req = requests.post(url, data = post)
addresses = json.loads(req.text)['locations']
 
csv = open(os.path.splitext(sys.argv[-1])[0]+'-geocode.csv', "w")
 
for place in addresses:
    csv.write('"'+place['address'].replace('"', '\"')+'",'+str(place['location']['y'])+','+str(place['location']['x'])+"n")
     
csv.close()
