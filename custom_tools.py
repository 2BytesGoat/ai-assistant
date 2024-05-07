import time
import json
import requests

import pyttsx3
engine = pyttsx3.init()


def get_location():
    url = 'http://ipinfo.io/json'
    response = requests.get(url).json()
    IP=response['ip']
    response = requests.get(f"https://geolocation-db.com/json/{IP}.79&position=true").json()
    return response

def get_nearby_store(query="seach for nearby shops"):
    location = get_location()
    engine.say(f"Searching nearby stores for location {location['state']}")
    engine.runAndWait()    
    coordinates = f"{location['latitude']}, {location['longitude']}"
    business_info = search_for_business(query, "store", coordinates)
    business = [{"name": b["name"], "rating": b["rating"], "reviews": b["reviews"]} for b in business_info]
    return business

def search_for_business(query, business_type, coordinates):
    # URL of the API
    url = "http://localhost:3000/api/tasks/submit-async"

    # Data payload to be sent with POST request, formatted as a Python dictionary
    data = {
        "queries": [
            query
        ],
        "country": None,
        "business_type": business_type,
        "max_cities": 1,
        "randomize_cities": False,
        "api_key": "",
        "enable_reviews_extraction": False,
        "max_reviews": 20,
        "reviews_sort": "newest",
        "lang": None,
        "max_results": 5,
        "coordinates": coordinates,
        "zoom_level": 10,
    }

    payload = {
        "data": data,
        "scraper_name": "get_places"
    }

    # Headers for the API request
    headers = {
        'Content-Type': 'application/json',
    }

    while True:
        # Sending POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers).json()

        if response[1]['result'] != None:
            return response[1]['result']

        time.sleep(20)
        engine.say(f"Sorry for the delay. This motherfucker wrote his code using ChatGPT.")
        engine.runAndWait()
        time.sleep(10)
