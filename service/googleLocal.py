import requests
from django.db.models import F, FloatField
from django.db.models.functions import Sqrt, Power
import math

def validate_location(location_name, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
            data = response.json()
            if data["results"]:
                result = data["results"][0]
                #return the formatted address and coordinates
                return result["formatted_address"], result["geometry"]["location"]["lat"], result["geometry"]["location"]["lng"]
    return location_name, None, None  

def haversine(lat1, lon1, lat2, lon2):
  
    #radius of the Earth in kilometers
    R = 6371.0

    #convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    #haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    #distance in kilometers
    distance = R * c
    return distance