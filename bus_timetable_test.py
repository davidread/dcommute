#!/usr/bin/env python3
"""
Oxford to London Bus Timetable Analysis Script

This script analyzes the Oxford to London bus timetable and predicts arrival times 
using the Google Directions API. It compares scheduled times with current traffic 
conditions to predict actual arrival times.

Requirements:
- Google Directions API key (set as environment variable GOOGLE_MAPS_API_KEY)
- pip install googlemaps pandas tabulate

Usage:
1. Set your Google Maps API key: export GOOGLE_MAPS_API_KEY="your_api_key_here"
2. Run: python bus_timetable_test.py
"""

import os
import googlemaps
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
import time

# All stops on the Oxford to London route
STOPS = [
    "Oxford Gloucester Green, Oxford, UK",
    "Headington Brookes University, Oxford, UK", 
    "Thornhill Park & Ride, Oxford, UK",
    "Lewknor Turn M40 Junction 6, UK",
    "North Hillingdon Station, Hillingdon, UK",
    "White City, London, UK",
    "Lisson Grove Marylebone Town Hall, London, UK",
    "Shepherd's Bush Holland Park, London, UK",
    "Marble Arch Park Lane, London, UK",
    "London Victoria Coach Station, London, UK"
]

# Timetable ('x' means bus doesn't stop here)
TIMETABLE = [
    "07:00",  # Oxford Gloucester Green
    "07:15",  # Headington Brookes University
    "07:30",  # Thornhill Park & Ride
    "07:45",  # Lewknor Turn M40 Junction 6
    "08:20",  # North Hillingdon Station
    "x",      # White City (no stop)
    "09:21",  # Lisson Grove Marylebone Town Hall
    "x",      # Shepherd's Bush Holland Park (no stop)
    "09:29",  # Marble Arch Park Lane
    "09:39"   # London Victoria Coach Station
]

class BusTimetableAnalyzer:
    def __init__(self, api_key):
        """Initialize with Google Maps API key."""
        self.gmaps = googlemaps.Client(key=api_key)
        
    def get_travel_time(self, origin, destination, departure_time=None):
        """
        Get travel time between two stops using Google Directions API.
        
        Args:
            origin: Starting location
            destination: Ending location  
            departure_time: When to calculate travel time for (default: now)
            
        Returns:
            Travel time in minutes
        """
        try:
            if departure_time is None:
                departure_time = datetime.now()
                
            result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode="driving",  # Bus follows driving routes
                departure_time=departure_time,
                traffic_model="best_guess"
            )
            
            if result:
                duration = result[0]['legs'][0]['duration_in_traffic']['value']
                return duration / 60  # Convert seconds to minutes
            else:
                print(f"No route found from {origin} to {destination}")
                return None
                
        except Exception as e:
            print(f"Error getting directions from {origin} to {destination}: {e}")
            return None
    
    def parse_time(self, time_str):
        """Parse time string to datetime object."""
        return datetime.strptime(time_str, "%H:%M").time()
    
    def time_to_minutes(self, time_obj):
        """Convert time object to minutes since midnight."""
        return time_obj.hour * 60 + time_obj.minute
    
    def minutes_to_time_str(self, minutes):
        """Convert minutes since midnight to time string."""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours:02d}:{mins:02d}"
    
    def predict_route_times(self, stops, timetable):
        """
        Analyze the bus timetable and predict arrival times.
        
        Args:
            stops: List of all stop names
            timetable: List of scheduled times ('x' for no stop)
            
        Returns:
            DataFrame with analysis results
        """
        results = []
        
        # Track the last stop where bus actually stopped
        last_used_stop = stops[0]
        last_used_time = self.time_to_minutes(self.parse_time(timetable[0]))
        
        # Start with the first stop
        results.append({
            'Stop': stops[0],
            'Timetable': timetable[0],
            'Extra Traffic (min)': 0,
            'Predicted Arrival': timetable[0]
        })
        
        print("Calculating travel times between stops...")
        
        # Process all remaining stops
        for i in range(1, len(stops)):
            current_stop = stops[i]
            scheduled_time = timetable[i]
            
            if scheduled_time != "x":
                # Bus stops here - calculate proper analysis
                print(f"Analyzing: {current_stop}")
                
                # Get travel time from last used stop to current stop
                travel_time = self.get_travel_time(last_used_stop, current_stop)
                
                if travel_time is None:
                    print(f"Skipping {current_stop} due to API error")
                    continue
                
                # Calculate predicted arrival time
                predicted_time = last_used_time + travel_time
                
                scheduled_time_obj = self.parse_time(scheduled_time)
                scheduled_time_minutes = self.time_to_minutes(scheduled_time_obj)
                
                # If bus arrives early, it waits until scheduled time
                actual_arrival = max(predicted_time, scheduled_time_minutes)
                
                # Calculate extra traffic delay
                # Find the last scheduled stop to compare travel times
                last_scheduled_time = None
                for j in range(i-1, -1, -1):
                    if timetable[j] != "x":
                        last_scheduled_time = self.time_to_minutes(self.parse_time(timetable[j]))
                        break
                
                if last_scheduled_time is not None:
                    scheduled_travel = scheduled_time_minutes - last_scheduled_time
                    actual_travel = actual_arrival - last_used_time
                    extra_traffic = max(0, actual_travel - scheduled_travel)
                else:
                    extra_traffic = 0
                
                results.append({
                    'Stop': current_stop,
                    'Timetable': scheduled_time,
                    'Extra Traffic (min)': round(extra_traffic, 1),
                    'Predicted Arrival': self.minutes_to_time_str(actual_arrival)
                })
                
                # Update last used stop since bus stopped here
                last_used_stop = current_stop
                last_used_time = actual_arrival
                
                # Small delay to avoid hitting API rate limits
                time.sleep(0.2)
                
            else:
                # Bus doesn't stop here - show dashes
                results.append({
                    'Stop': current_stop,
                    'Timetable': "-",
                    'Extra Traffic (min)': "-",
                    'Predicted Arrival': "-"
                })
                
                # Don't update last_used_stop since bus didn't stop
        
        return pd.DataFrame(results)

def main():
    """Main function to run the bus timetable analysis."""
    
    # Read API key from file
    key_file_path = os.path.expanduser("~/.gcloud/dcommute-service-account-key.json")
    try:
        with open(key_file_path, 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print(f"ERROR: API key file not found at {key_file_path}")
        print("Please create this file with your Google Maps API key")
        print("\nTo get an API key:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable the Directions API")
        print("3. Create credentials and copy your API key")
        return
    except Exception as e:
        print(f"ERROR: Could not read API key file: {e}")
        return
    
    print("Oxford to London Bus Timetable Analysis")
    print("=" * 50)
    print(f"Analyzing {len(STOPS)} stops with current traffic conditions...")
    print("Note: 'x' means bus doesn't stop at that location")
    print()
    
    # Initialize analyzer
    analyzer = BusTimetableAnalyzer(api_key)
    
    # Run analysis
    try:
        results = analyzer.predict_route_times(STOPS, TIMETABLE)
        
        # Display results
        print("\nResults:")
        print("=" * 80)
        print(tabulate(results, headers='keys', tablefmt='grid', floatfmt='.1f'))
        
        # Summary statistics (only for stops where bus actually stops)
        scheduled_stops = results[results['Timetable'] != '-']
        if len(scheduled_stops) > 0:
            total_extra_traffic = scheduled_stops['Extra Traffic (min)'].sum()
            max_delay = scheduled_stops['Extra Traffic (min)'].max()
            
            print(f"\nSummary:")
            print(f"Total extra traffic delay: {total_extra_traffic:.1f} minutes")
            print(f"Maximum delay at single stop: {max_delay:.1f} minutes")
            
            # Journey analysis
            first_time = scheduled_stops.iloc[0]['Timetable']
            last_time = scheduled_stops.iloc[-1]['Predicted Arrival']
            print(f"Journey: {first_time} → {last_time}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()