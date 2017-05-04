import requests
import json
import random 
import pprint

class EatstreetAPIHandler: 

	def __init__(self): 
		self.endpoint = 'https://api.eatstreet.com/publicapi/v1/restaurant/search'
		self.currentRestaurantData = {}

		#load api key from config file 
		with open('config', 'r') as configFile: 
			for line in configFile: 
				lineData = line.split(':') 
				if lineData[0] == 'eatstreet': 
					self.api_key = lineData[1].strip()
					break 

	#@DESC: perform request given parameters 
	#@param searchTerm: optional query term
	#@param shuffleIndex: return n random restaurants
	#RETURN: corresponding restaurant list
	def requestRestaurants(self, address, searchTerm= None, shuffleIndex= None): 

		#set request parameters 
		params = {
			'street-address': address,
			'method': 'delivery',
			'access-token': self.api_key
		} 

		#if user defined search term, include in params
		if searchTerm is not None:
			params['search'] = searchTerm

		#handle request failure
		try:
			req = requests.get(self.endpoint, params)
		except requests.exceptions.RequestException as e: 
		    return None 

		responseData = json.loads(req.text)
		restaurants = responseData['restaurants'] 

		#optional restaurant shuffle
		if shuffleIndex is not None: 
			if len(restaurants) > 3: 
				return random.sample(restaurants, shuffleIndex)
			else: 
				return restaurants

		return restaurants

	#@DESC: request additional information for already loaded restaurant
	def requestAdditionalInformation(restaurantName): 
		pass