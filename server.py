import logging
import os
from eatstreet import EatstreetAPIHandler

from flask import Flask
from flask_ask import Ask, request, session, question, statement, context

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


#-=-=-=-=-=-=-=-=-
#Device Location Code
#-=-=-=-=-=-=-=-=-

def get_alexa_location():
    try:
        URL =  "https://api.amazonalexa.com/v1/devices/{}/settings" \
               "/address".format(context.System.device.deviceId)
        TOKEN =  context.System.user.permissions.consentToken
        HEADER = {'Accept': 'application/json',
                 'Authorization': 'Bearer {}'.format(TOKEN)}
        r = requests.get(URL, headers=HEADER)
        if r.status_code == 200:
            return(r.json())
        else: 
            return None
    except: 
        return None

def construct_address():
    location = get_alexa_location()

    if location is None: 
        return None 

    city = location["city"].encode("utf-8") 
    address = location["addressLine1"].encode("utf-8")
    state = location["stateOrRegion"]
    final_address = address + ', ' + city + ', ' + state 
    return final_address

#-=-=-=-=-=-=-=-=-
#Helper functions!
#-=-=-=-=-=-=-=-=-

def restaurantListToSpeech(restaurantList): 
    lastTerm = restaurantList[-1]['name']
    speech = ''

    for restaurant in restaurantList[:-1]: 
        speech += restaurant['name'] + ', '

    speech += 'and ' + lastTerm + ' all deliver to your location!'
    return speech

#-=-=-=-=-=-=-=-=-
#Alexa Server Code
#-=-=-=-=-=-=-=-=-

@ask.launch
def launch():
    speech_text = 'Ask me for food that delivers nearby! Add a search term for more specific results.'
    return question(speech_text).reprompt(speech_text).simple_card('DeliverableName', speech_text)


@ask.intent('RestaurantSearchIntent')
def initial_interaction(food_type):
    session.attributes['food_type'] = food_type 

    #if the user gave permission for address, should come up here
    #if that doesn't work, ask for address explicitly
    user_address = construct_address() 

    if user_address is not None: 
        return restaurant_index(user_address)

    if food_type is None: 
        speech_text = 'Please tell me your current location.'
    else: 
        speech_text = 'I would love to search for %s in your area! Please tell me your current location.' % food_type 

    return question(speech_text)

@ask.intent('UserAddressIntent')
def restaurant_index(user_address): 

    food_type = session.attributes['food_type']

    #as searchTerm is defaulted to None in class, this works fine whether or not 
    #user supplied a food_type
    eatApi = EatstreetAPIHandler() 
    restaurants = eatApi.requestRestaurants(user_address, searchTerm= food_type, shuffleIndex= 3)
    if len(restaurants) > 0: 
        response_text = restaurantListToSpeech(restaurants)
        return statement(response_text)

    else: 
        response_text = "I'm afraid I couldn't find any results!"
        return statement(response_text).simple_card(title='Restaurants that deliver...', content=response_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Ask me what deliverable food is available near you!'
    return question(speech_text).reprompt(speech_text).simple_card('DeliverableName', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)