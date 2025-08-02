#!/usr/bin/env python3

import requests
import json
import os

def test_google_directions_api():
    # Read API key from file
    key_file_path = os.path.expanduser("~/.gcloud/dcommute-service-account-key.json")
    try:
        with open(key_file_path, 'r') as f:
            API_KEY = f.read().strip()
    except FileNotFoundError:
        print(f"API key file not found: {key_file_path}")
        return False
    except Exception as e:
        print(f"Error reading API key: {e}")
        return False
    
    # Victoria Coach Station to Marylebone Town Hall
    origin = "Victoria Coach Station, London, UK"
    destination = "Marylebone Town Hall, London, UK"
    
    # Google Directions API endpoint
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    params = {
        'origin': origin,
        'destination': destination,
        'mode': 'driving',
        'departure_time': 'now',
        'traffic_model': 'best_guess',
        'key': API_KEY
    }
    
    try:
        print(f"Making API call from '{origin}' to '{destination}'...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK':
                route = data['routes'][0]
                leg = route['legs'][0]
                
                print(f"\nRoute found!")
                print(f"Distance: {leg['distance']['text']}")
                print(f"Duration: {leg['duration']['text']}")
                
                if 'duration_in_traffic' in leg:
                    print(f"Duration in traffic: {leg['duration_in_traffic']['text']}")
                
                print(f"Start address: {leg['start_address']}")
                print(f"End address: {leg['end_address']}")
                
                return True
            else:
                print(f"API Error: {data['status']}")
                if 'error_message' in data:
                    print(f"Error message: {data['error_message']}")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error making API call: {e}")
        return False

if __name__ == "__main__":
    test_google_directions_api()