import os
import requests
import re
import json
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Get Steam API key from environment variables
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

def get_steam_id_from_vanity_url(vanity_url):
    """
    Convert a Steam vanity URL (custom URL) to a Steam ID.
    
    Args:
        vanity_url (str): The vanity URL name (the custom part of the profile URL).
        
    Returns:
        str: The Steam ID or None if not found.
    """
    if not STEAM_API_KEY:
        print("Error: Steam API key not found. Please set it in the .env file.")
        return None
    
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {
        'key': STEAM_API_KEY,
        'vanityurl': vanity_url
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('response', {}).get('success') == 1:
            return data['response']['steamid']
        else:
            print(f"Could not find Steam ID for vanity URL: {vanity_url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error resolving vanity URL: {e}")
        return None

def extract_steam_id_from_url(url):
    """
    Extract Steam ID from a Steam profile or wishlist URL.
    
    Args:
        url (str): The Steam profile or wishlist URL.
        
    Returns:
        str: The Steam ID or None if not found.
    """
    # Try to match the Steam ID in various URL formats
    patterns = [
        r'profiles/(\d+)',  # Match profiles/76561197990237856
        r'id/([^/]+)',      # Match id/username
        r'wishlist/id/([^/]+)',  # Match wishlist/id/username
        r'wishlist/profiles/(\d+)'  # Match wishlist/profiles/76561197990237856
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            result = match.group(1)
            # If it's a numeric ID, return it directly
            if result.isdigit():
                return result
            # If it's a username, resolve it to a Steam ID
            else:
                return get_steam_id_from_vanity_url(result)
    
    return None

def scrape_wishlist_page(url):
    """
    Scrape the wishlist page directly to get game names when the API fails.
    
    Args:
        url (str): The wishlist URL.
        
    Returns:
        list: List of game names from the wishlist.
    """
    # Make sure we have a valid wishlist URL
    if 'wishlist' not in url:
        if url.isdigit():
            # It's a Steam ID
            url = f"https://store.steampowered.com/wishlist/profiles/{url}/"
        else:
            # It's a username
            url = f"https://store.steampowered.com/wishlist/id/{url}/"
    
    # Remove any query parameters
    url = url.split('?')[0]
    if not url.endswith('/'):
        url += '/'
    
    print(f"Scraping wishlist page: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Add cookies to help bypass rate limiting
    cookies = {
        'birthtime': '786344401',  # Set to a date that's over 18 years ago
        'mature_content': '1',
        'lastagecheckage': '1-0-1995',
        'wants_mature_content': '1',
    }
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}...")
            
            # Add a delay between retries to avoid rate limiting
            if attempt > 0:
                delay = retry_delay * (attempt + random.random())
                print(f"Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)
            
            response = requests.get(url, headers=headers, cookies=cookies)
            
            # Check for rate limiting
            if response.status_code == 429:
                print("Rate limited by Steam. Waiting before retry...")
                time.sleep(5 + random.random() * 5)  # Wait 5-10 seconds
                continue
                
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find the wishlist data in the page
            games = []
            
            # Method 1: Look for the g_rgWishlistData variable in the page script
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'g_rgWishlistData' in script.string:
                    # Extract the JSON data
                    match = re.search(r'g_rgWishlistData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                    if match:
                        try:
                            wishlist_data = json.loads(match.group(1))
                            for game in wishlist_data:
                                if 'name' in game:
                                    games.append(game['name'])
                            print(f"Found {len(games)} games in wishlist using script data")
                            return games
                        except json.JSONDecodeError:
                            print("Failed to parse wishlist data from script")
            
            # Method 2: Look for game titles in the HTML
            if not games:
                game_elements = soup.select('.wishlist_row')
                for element in game_elements:
                    title_element = element.select_one('.title')
                    if title_element:
                        games.append(title_element.text.strip())
                
                if games:
                    print(f"Found {len(games)} games in wishlist using HTML parsing")
                    return games
            
            # Method 3: Look for app IDs and then fetch game details
            if not games:
                app_id_matches = re.findall(r'data-app-id="(\d+)"', response.text)
                if app_id_matches:
                    unique_app_ids = list(set(app_id_matches))
                    print(f"Found {len(unique_app_ids)} app IDs in wishlist, fetching game details...")
                    
                    for app_id in unique_app_ids:
                        # Add delay between requests to avoid rate limiting
                        time.sleep(0.5 + random.random())
                        game_details = get_game_details(app_id)
                        if game_details and 'name' in game_details:
                            games.append(game_details['name'])
                    
                    if games:
                        print(f"Retrieved {len(games)} game names from app IDs")
                        return games
            
            # Method 4: Try to extract wishlist data from another script variable
            if not games:
                for script in scripts:
                    if script.string and 'g_rgAppInfo' in script.string:
                        match = re.search(r'g_rgAppInfo\s*=\s*({.*?});', script.string, re.DOTALL)
                        if match:
                            try:
                                app_info = json.loads(match.group(1))
                                for app_id, info in app_info.items():
                                    if 'name' in info:
                                        games.append(info['name'])
                                
                                if games:
                                    print(f"Found {len(games)} games in wishlist using app info data")
                                    return games
                            except json.JSONDecodeError:
                                print("Failed to parse app info data from script")
            
            # If we still don't have games, check if the page indicates the wishlist is private
            if 'profile is private' in response.text.lower() or 'wishlist is private' in response.text.lower():
                print("The Steam profile or wishlist appears to be private.")
                print("Please make sure your wishlist is public in your Steam privacy settings.")
                return []
            
            if not games:
                # If this is the last attempt and we still have no games
                if attempt == max_retries - 1:
                    print("Could not find any games in the wishlist page")
                    print("Please make sure your wishlist is public and contains games")
                    
                    # Save the HTML for debugging
                    with open('wishlist_debug.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print("Saved wishlist page HTML to 'wishlist_debug.html' for debugging")
                    
                    return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error scraping wishlist page: {e}")
            
            # If this is the last attempt
            if attempt == max_retries - 1:
                return []
            
            # Wait before retrying
            time.sleep(retry_delay * (attempt + 1))

def get_wishlist(steam_id_or_url, use_api=True):
    """
    Get a user's Steam wishlist.
    
    Args:
        steam_id_or_url (str): Steam ID, vanity URL name, or full wishlist URL.
        use_api (bool): Whether to use the Steam API (True) or web scraping (False).
        
    Returns:
        list: List of game names from the wishlist.
    """
    # Check if input is a URL
    if '/' in steam_id_or_url or '\\' in steam_id_or_url:
        steam_id = extract_steam_id_from_url(steam_id_or_url)
        if not steam_id:
            print(f"Could not extract Steam ID from URL: {steam_id_or_url}")
            # Try scraping the page directly
            return scrape_wishlist_page(steam_id_or_url)
    else:
        # Check if input is a vanity URL or Steam ID
        steam_id = steam_id_or_url
        if not steam_id_or_url.isdigit():
            # If not all digits, assume it's a vanity URL
            steam_id = get_steam_id_from_vanity_url(steam_id_or_url)
            if not steam_id:
                # Try scraping the page directly
                return scrape_wishlist_page(steam_id_or_url)
    
    # If use_api is False, go straight to web scraping
    if not use_api:
        print(f"Using web scraping method for wishlist: {steam_id}")
        wishlist_url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/"
        return scrape_wishlist_page(wishlist_url)
    
    # Steam wishlist API endpoint
    url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/wishlistdata/"
    
    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f'https://store.steampowered.com/wishlist/profiles/{steam_id}/'
    }
    
    try:
        print(f"Fetching wishlist from API: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Check if the response is valid JSON
        try:
            data = response.json()
            
            # Extract game names from wishlist
            games = []
            for game_id, game_data in data.items():
                game_name = game_data.get('name')
                if game_name:
                    games.append(game_name)
            
            print(f"Found {len(games)} games in wishlist for Steam ID: {steam_id}")
            return games
        except ValueError:
            print(f"Error: Received invalid JSON response from API.")
            print("Response content (first 100 chars):", response.text[:100])
            
            if use_api:
                print("API method failed. You can try again with web scraping.")
                return []
            else:
                print("Falling back to scraping the wishlist page...")
                wishlist_url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/"
                return scrape_wishlist_page(wishlist_url)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching wishlist from API: {e}")
        
        if use_api:
            print("API method failed. You can try again with web scraping.")
            return []
        else:
            print("Falling back to scraping the wishlist page...")
            wishlist_url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/"
            return scrape_wishlist_page(wishlist_url)

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