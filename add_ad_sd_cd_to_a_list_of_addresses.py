#!/usr/bin/python
# This code takes a list of street addresses, runs them through the 
# state address management system geocoder, then joins them against 
# shapefiles that you supply to add the Assembly, Senate, Congressional Districts

import requests,sys,json,os,csv

import pandas as pd
import geopandas as gpd

lines=[]

# read list of addresses
with open(sys.argv[-1], newline='') as csvfile:	
	for line in csv.DictReader(csvfile):
		lines.append(line)
		
# build address query
query = '{"records": ['
i=0
for line in lines:
	query += '{ "attributes": { "OBJECTID":'+str(i)+', "SINGLELINE": "'+line['Address'].rstrip()+'"} },'+"\n"
	i+=1	
query += ']}'

post = { 'f':'pjson', 'outSR': 4326, 'addresses': query }
url = 'https://gisservices.its.ny.gov/arcgis/rest/services/Locators/Street_and_Address_Composite/GeocodeServer/geocodeAddresses'

# send request to state geocoder
req = requests.post(url, data = post)
locations = json.loads(req.text)['locations']

# parse response
for loc in locations:
	i = loc['attributes']['ResultID']
	lines[i]['y'] = loc['location']['y']
	lines[i]['x'] = loc['location']['x']
	lines[i]['Match_addr'] = loc['attributes']['Match_addr']
	
	# hackish, might cause problems but keeps joins from NaN errors
	if (lines[i]['x'] == 'NaN'):
		lines[i]['x'] = 0
		lines[i]['y'] = 0

# convert to pandas
locPd = pd.DataFrame(lines,columns=lines[0].keys())
locPd = gpd.GeoDataFrame(locPd,  geometry=gpd.points_from_xy(locPd.x.astype('float32'), locPd.y.astype('float32')))

# add county municipality column
cosub = gpd.read_file(r'/home/andy/Documents/GIS.Data/geocode/cosub.gpkg')
locPd = gpd.sjoin(locPd, cosub, op="within")

del locPd['index_right']

# add ads column
ad = gpd.read_file(r'/home/andy/Documents/GIS.Data/geocode/ad.gpkg')
locPd = gpd.sjoin(locPd, ad, op="within")

del locPd['index_right']

# add sd column
sd = gpd.read_file(r'/home/andy/Documents/GIS.Data/geocode/sd.gpkg')
locPd = gpd.sjoin(locPd, sd, op="within")

del locPd['index_right']

# add cd column
sd = gpd.read_file(r'/home/andy/Documents/GIS.Data/geocode/cd.gpkg')
locPd = gpd.sjoin(locPd, sd, op="within")


# remove added geometery and index columns
del locPd['geometry']
del locPd['index_right']

# write pandas back to out csv
locPd.to_csv (os.path.splitext(sys.argv[-1])[0]+'-output.csv', index = False, header=True)
