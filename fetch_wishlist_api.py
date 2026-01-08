#!/usr/bin/env python3
"""
Steam Wishlist API Fetcher

This script uses the Steam Web API to fetch your wishlist data.
It requires a valid Steam API key (stored in .env file) and your Steam ID.
"""

import os
import sys
import json
import time
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fetch_wishlist_api.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fetch_wishlist_api")

def load_api_key():
    """Load the Steam API key from .env file."""
    load_dotenv()
    api_key = os.getenv("STEAM_API_KEY")
    if not api_key:
        logger.error("No Steam API key found in .env file")
        print("Error: No Steam API key found in .env file.")
        print("Please create a .env file with your Steam API key:")
        print("STEAM_API_KEY=your_api_key_here")
        return None
    return api_key

def get_wishlist_from_store(steam_id):
    """
    Get the wishlist directly from the Steam store API.
    This is a different approach that doesn't use the official Steam Web API.
    """
    logger.info(f"Fetching wishlist from Steam store for Steam ID: {steam_id}")
    
    # The store API endpoint for wishlists
    url = "https://store.steampowered.com/api/wishlist/getappwishlist"
    params = {
        "steamid": steam_id,
        "time": int(time.time())
    }
    
    # Use a realistic user agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Referer": f"https://store.steampowered.com/wishlist/profiles/{steam_id}/"
    }
    
    try:
        # First, visit the wishlist page to get cookies
        session = requests.Session()
        wishlist_url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/"
        logger.info(f"Visiting wishlist page: {wishlist_url}")
        session.get(wishlist_url, headers=headers)
        
        # Now try to get the wishlist data
        response = session.get(url, params=params, headers=headers)
        logger.info(f"Wishlist API response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info("Successfully parsed wishlist JSON response")
                return data
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON response")
                logger.debug(f"Response content: {response.text[:200]}...")
                return None
        else:
            logger.error(f"Wishlist API request failed with status code: {response.status_code}")
            logger.debug(f"Response content: {response.text[:200]}...")
            return None
    except Exception as e:
        logger.error(f"Error fetching wishlist from store: {e}")
        return None

def get_wishlist_from_community(api_key, steam_id):
    """
    Try to get the wishlist using the Steam Community API.
    This is yet another approach.
    """
    logger.info(f"Fetching wishlist from Steam Community for Steam ID: {steam_id}")
    
    # First, get the user's profile to ensure they exist
    profile_url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    profile_params = {
        "key": api_key,
        "steamids": steam_id
    }
    
    try:
        profile_response = requests.get(profile_url, params=profile_params)
        logger.info(f"Profile API response status: {profile_response.status_code}")
        
        if profile_response.status_code != 200:
            logger.error("Failed to verify Steam ID")
            return None
        
        # Now try to get the wishlist using the store API
        # This is a different endpoint that sometimes works better
        wishlist_url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/wishlistdata/"
        params = {
            "p": "0",  # Page number
            "v": str(int(time.time()))  # Timestamp to avoid caching
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Referer": f"https://store.steampowered.com/wishlist/profiles/{steam_id}/"
        }
        
        session = requests.Session()
        # First visit the wishlist page to get cookies
        session.get(f"https://store.steampowered.com/wishlist/profiles/{steam_id}/", headers=headers)
        
        # Now try to get the wishlist data
        response = session.get(wishlist_url, params=params, headers=headers)
        logger.info(f"Wishlist data response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info("Successfully parsed wishlist data JSON response")
                return data
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON response")
                logger.debug(f"Response content: {response.text[:200]}...")
                return None
        else:
            logger.error(f"Wishlist data request failed with status code: {response.status_code}")
            logger.debug(f"Response content: {response.text[:200]}...")
            return None
    except Exception as e:
        logger.error(f"Error fetching wishlist from community: {e}")
        return None

def extract_games_from_wishlist_data(wishlist_data):
    """Extract game names from wishlist data."""
    if not wishlist_data:
        return []
    
    games = []
    for _app_id, game_info in wishlist_data.items():
        if isinstance(game_info, dict) and "name" in game_info:
            games.append(game_info["name"])
    
    # Sort alphabetically
    games.sort()
    logger.info(f"Extracted {len(games)} games from wishlist data")
    return games

def save_games_to_file(games, output_file="wishlist.txt"):
    """Save the game names to a file."""
    if not games:
        logger.warning("No games to save.")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Games from your Steam wishlist\n")
            f.write("# One game name per line\n\n")
            for game in games:
                f.write(f"{game}\n")
        logger.info(f"Successfully saved {len(games)} games to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving games to file: {e}")
        return False

def get_wishlist_from_api_service(api_key, steam_id):
    """
    Get the wishlist using the official IWishlistService API.
    This is the most direct and reliable method when it works.
    """
    logger.info(f"Fetching wishlist using IWishlistService API for Steam ID: {steam_id}")
    
    # The official wishlist API endpoint
    url = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/"
    
    params = {
        "key": api_key,
        "steamid": steam_id
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        logger.info(f"IWishlistService API response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info("Successfully parsed IWishlistService API response")
                
                # Save the raw response for debugging
                with open("wishlist_api_response.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                logger.info("Saved raw API response to wishlist_api_response.json")
                
                # Extract games from the response
                if "response" in data and "items" in data["response"]:
                    wishlist_items = data["response"]["items"]
                    logger.info(f"Found {len(wishlist_items)} items in wishlist")
                    
                    # Get the app details for each wishlist item
                    games = []
                    app_ids = []
                    
                    # First, collect all app IDs
                    for item in wishlist_items:
                        if "appid" in item:
                            app_ids.append(item["appid"])
                    
                    # Now get game names in batches to avoid too many API calls
                    logger.info(f"Fetching names for {len(app_ids)} games")
                    
                    # Process in smaller batches
                    batch_size = 20
                    for i in range(0, len(app_ids), batch_size):
                        batch = app_ids[i:i+batch_size]
                        logger.info(f"Processing batch {i//batch_size + 1} of {(len(app_ids) + batch_size - 1)//batch_size}")
                        
                        for app_id in batch:
                            app_name = get_app_name(api_key, app_id)
                            if app_name:
                                games.append(app_name)
                                try:
                                    logger.info(f"Found game: {app_name}")
                                except UnicodeEncodeError:
                                    logger.info(f"Found game with ID: {app_id} (name contains non-ASCII characters)")
                    
                    if games:
                        games.sort()
                        logger.info(f"Successfully extracted {len(games)} game names")
                        return games
                    else:
                        logger.warning("No game names could be extracted from wishlist items")
                else:
                    logger.warning("Unexpected response format from IWishlistService API")
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON response from IWishlistService API")
                logger.debug(f"Response content: {response.text[:200]}...")
        else:
            logger.error(f"IWishlistService API request failed with status code: {response.status_code}")
            logger.debug(f"Response content: {response.text[:200]}...")
    except Exception as e:
        logger.error(f"Error fetching wishlist from IWishlistService API: {e}")
    
    return None

def get_app_name(api_key, app_id):
    """Get the name of an app using the Steam API."""
    logger.info(f"Getting name for app ID: {app_id}")
    
    # Try the store API first (most reliable for game names)
    try:
        store_url = "https://store.steampowered.com/api/appdetails"
        params = {"appids": app_id}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
        
        # Add a delay to avoid rate limiting
        time.sleep(0.5)
        
        response = requests.get(store_url, params=params, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                if str(app_id) in data and data[str(app_id)]["success"] and "data" in data[str(app_id)] and "name" in data[str(app_id)]["data"]:
                    name = data[str(app_id)]["data"]["name"]
                    logger.info(f"Found name for app ID {app_id}: {name}")
                    return name
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse store API response for app ID {app_id}: {e}")
        elif response.status_code == 429:
            logger.warning(f"Rate limited by Steam store API for app ID {app_id}")
            # Add a longer delay before the fallback
            time.sleep(2)
    except Exception as e:
        logger.warning(f"Error fetching app details from store API: {e}")
    
    # Try the ISteamApps API as a fallback
    try:
        # First try the GetAppDetails endpoint if available
        app_details_url = "https://api.steampowered.com/ISteamApps/GetAppDetails/v2/"
        params = {
            "key": api_key,
            "appids": app_id
        }
        
        # Add a delay to avoid rate limiting
        time.sleep(0.5)
        
        response = requests.get(app_details_url, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                if "appdetails" in data and str(app_id) in data["appdetails"] and "name" in data["appdetails"][str(app_id)]:
                    name = data["appdetails"][str(app_id)]["name"]
                    logger.info(f"Found name for app ID {app_id} using GetAppDetails: {name}")
                    return name
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse GetAppDetails response: {e}")
    except Exception as e:
        logger.warning(f"Error fetching from GetAppDetails: {e}")
    
    # Try the GetAppList as a last resort
    try:
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                if "applist" in data and "apps" in data["applist"]:
                    for app in data["applist"]["apps"]:
                        if app.get("appid") == app_id and "name" in app:
                            name = app["name"]
                            logger.info(f"Found name for app ID {app_id} in app list: {name}")
                            return name
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse ISteamApps API response: {e}")
    except Exception as e:
        logger.warning(f"Error fetching app list: {e}")
    
    # If all else fails, return a placeholder
    logger.warning(f"Could not find name for app ID {app_id}")
    return f"Unknown Game (AppID: {app_id})"

def main():
    logger.info("Steam Wishlist API Fetcher started")
    
    if len(sys.argv) < 2:
        logger.error("No Steam ID provided")
        print("Usage: python fetch_wishlist_api.py <steam_id>")
        print("\nExample:")
        print("  python fetch_wishlist_api.py 76561197990237856")
        return 1
    
    steam_id = sys.argv[1]
    logger.info(f"Using Steam ID: {steam_id}")
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        return 1
    
    # Try different methods to get the wishlist
    logger.info("Trying different methods to fetch your wishlist...")
    
    # Method 0: Try the official IWishlistService API (new method)
    games = get_wishlist_from_api_service(api_key, steam_id)
    if games:
        if save_games_to_file(games):
            print(f"\nSuccess! Found {len(games)} games in your wishlist using the official API.")
            print("Next steps:")
            print("Run the main script with: python main.py -f wishlist.txt")
            return 0
    
    # Method 1: Try to get wishlist from community
    wishlist_data = get_wishlist_from_community(api_key, steam_id)
    if wishlist_data and isinstance(wishlist_data, dict) and len(wishlist_data) > 0:
        games = extract_games_from_wishlist_data(wishlist_data)
        if games:
            if save_games_to_file(games):
                print(f"\nSuccess! Found {len(games)} games in your wishlist.")
                print("Next steps:")
                print("Run the main script with: python main.py -f wishlist.txt")
                return 0
    
    # Method 2: Try to get wishlist from store
    wishlist_data = get_wishlist_from_store(steam_id)
    if wishlist_data and isinstance(wishlist_data, list) and len(wishlist_data) > 0:
        games = []
        for item in wishlist_data:
            if "name" in item:
                games.append(item["name"])
        
        if games:
            games.sort()
            if save_games_to_file(games):
                print(f"\nSuccess! Found {len(games)} games in your wishlist.")
                print("Next steps:")
                print("Run the main script with: python main.py -f wishlist.txt")
                return 0
    
    # If we get here, all methods failed
    logger.error("Failed to fetch your wishlist")
    print("\nError: Could not fetch your wishlist.")
    print("Possible reasons:")
    print("1. Your wishlist is private (check your Steam privacy settings)")
    print("2. Steam is rate-limiting your requests (try again later)")
    print("3. You're using a VPN (try without it)")
    print("4. Your Steam ID is incorrect")
    
    print("\nAlternative options:")
    print("1. Create a wishlist.txt file manually with your game names")
    print("2. Try again later when Steam's rate limits may have reset")
    print("3. Use the example wishlist.txt file that's already included")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 