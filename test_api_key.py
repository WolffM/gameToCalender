#!/usr/bin/env python3
"""
Test Steam API Key

This script tests if your Steam API key is valid by making a simple API call.
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_api_key():
    """Test if the Steam API key is valid."""
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv('STEAM_API_KEY')
    
    if not api_key:
        print("Error: No Steam API key found in .env file")
        print("Please make sure you have a valid STEAM_API_KEY in your .env file")
        return False
    
    print(f"Found API key: {api_key[:5]}...{api_key[-5:]}")
    
    # Test the API key with a simple API call
    test_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids=76561197990237856"
    
    try:
        print(f"Testing API key with URL: {test_url}")
        response = requests.get(test_url, timeout=10)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("API key is valid! Response:")
            print(json.dumps(data, indent=2))
            return True
        elif response.status_code == 401 or response.status_code == 403:
            print("API key is invalid or has insufficient permissions")
            print("Response content:", response.text)
            return False
        else:
            print(f"Unexpected status code: {response.status_code}")
            print("Response content:", response.text)
            return False
    
    except Exception as e:
        print(f"Error testing API key: {e}")
        return False

if __name__ == "__main__":
    print("Testing Steam API key...")
    test_api_key() 