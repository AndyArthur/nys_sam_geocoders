#!/usr/bin/python
 
import requests,sys,json,csv,os

out_csv = csv.writer(open(os.path.splitext(sys.argv[-1])[0]+'-geocode.csv', "w"))

i=0
with open(sys.argv[-1], 'r+') as cr:
	for line in csv.DictReader(cr):

		post = { 'distance': 3000, 'f':'pjson', 
				'outSR': 4326, 'location':
					json.dumps( 
					{	"x": float(line['lng']), 
						"y": float(line['lat']), 
						"spatialReference": 
							{ "wkid": 4326 } 
					})
				 }

		url = 'https://gisservices.its.ny.gov/arcgis/rest/services/CompositePointLocator/GeocodeServer/reverseGeocode'
		
		req = requests.post(url, data = post)
		address = json.loads(req.text)

		if not i:
			head = ['search_lat','search_lng', 
					'found_lat','found_lng']
			
			head.extend(address['address'].keys())
			
			out_csv.writerow(head)
			
			i=1
		
		row = [	float(line['lat']),
				float(line['lng']),
				float(address['location']['y']),
				float(address['location']['x'])
				]
		row.extend(address['address'].values())
		
		out_csv.writerow(row)


