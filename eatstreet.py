import requests
import json

class EatstreetAPIHandler: 

	def __init__(self): 
		self.endpoint = 'https://api.eatstreet.com/publicapi/v1/restaurant/search'
		
		#load api key from config file 
		with open('config', 'r') as configFile: 
			for line in configFile: 
				lineData = line.split(':') 
				if lineData[0] == 'eatstreet': 
					self.api_key = lineData[1].strip()
					break 

		print self.api_key

		self.responseData = None 

	def request(address, radius= 5, searchTerm= None): 

		#manufacture request 
		params = {
			'street-address': address,
			'pickup-radius': radius, 
			'method': 'delivery',
			'access-token': self.api_key
		} 

		#if user defined search term
		if searchTerm is not None:
			params['search'] = searchTerm

		try:
			req = requests.get(self.endpoint, params)
		except requests.exceptions.RequestException as e: 
		    return None 

		self.responseData = JSON.loads(req.text)
		print self.responseData 

eat = EatstreetAPIHandler() 
#eat.request('3303 Trail Ridge Road', 500)