import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Steam API key from environment variables
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

def search_game(game_name):
    """
    Search for a game on Steam by name.
    
    Args:
        game_name (str): The name of the game to search for.
        
    Returns:
        dict: Information about the game if found, None otherwise.
    """
    # Steam Store API endpoint for searching
    url = "https://store.steampowered.com/api/storesearch"
    
    params = {
        'term': game_name,
        'l': 'english',
        'cc': 'US'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('total') > 0:
            # Return the first result (most relevant)
            return data['items'][0]
        else:
            print(f"No results found for '{game_name}'")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error searching for game '{game_name}': {e}")
        return None

def get_game_details(app_id):
    """
    Get detailed information about a game from Steam API.
    
    Args:
        app_id (int): The Steam app ID of the game.
        
    Returns:
        dict: Detailed information about the game if found, None otherwise.
    """
    # Steam Store API endpoint for app details
    url = "https://store.steampowered.com/api/appdetails"
    
    params = {
        'appids': app_id,
        'cc': 'US',
        'l': 'english'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get(str(app_id), {}).get('success', False):
            return data[str(app_id)]['data']
        else:
            print(f"No details found for app ID {app_id}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting details for app ID {app_id}: {e}")
        return None

def parse_release_date(release_date_info):
    """
    Parse the release date information from Steam API.
    
    Args:
        release_date_info (dict): Release date information from Steam API.
        
    Returns:
        tuple: (release_date as datetime object, is_coming_soon boolean)
    """
    if not release_date_info:
        return None, False
    
    is_coming_soon = release_date_info.get('coming_soon', False)
    date_string = release_date_info.get('date', '')
    
    if not date_string:
        return None, is_coming_soon
    
    # Try different date formats
    date_formats = [
        '%d %b, %Y',  # 25 Dec, 2023
        '%b %d, %Y',  # Dec 25, 2023
        '%B %d, %Y',  # December 25, 2023
        '%d %B, %Y',  # 25 December, 2023
        '%Y-%m-%d',   # 2023-12-25
        '%b %Y',      # Dec 2023
        '%B %Y',      # December 2023
        '%Y'          # 2023
    ]
    
    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format), is_coming_soon
        except ValueError:
            continue
    
    # If we can't parse the date, return the string and coming_soon flag
    print(f"Could not parse date string: '{date_string}'")
    return date_string, is_coming_soon

def get_game_release_info(game_name):
    """
    Get release information for a game.
    
    Args:
        game_name (str): The name of the game to search for.
        
    Returns:
        dict: Information about the game including release date, or None if not found.
    """
    # Search for the game
    game_info = search_game(game_name)
    if not game_info:
        return None
    
    app_id = game_info.get('id')
    if not app_id:
        print(f"No app ID found for '{game_name}'")
        return None
    
    # Get detailed information about the game
    game_details = get_game_details(app_id)
    if not game_details:
        return None
    
    # Extract release date information
    release_date_info = game_details.get('release_date', {})
    release_date, is_coming_soon = parse_release_date(release_date_info)
    
    # Return relevant information
    return {
        'name': game_details.get('name', game_name),
        'app_id': app_id,
        'release_date': release_date,
        'is_coming_soon': is_coming_soon,
        'header_image': game_details.get('header_image', ''),
        'short_description': game_details.get('short_description', '')
    } 