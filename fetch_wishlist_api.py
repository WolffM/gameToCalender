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

def get_owned_games(api_key, steam_id):
    """Get the list of games owned by the user."""
    logger.info(f"Fetching owned games for Steam ID: {steam_id}")
    
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1
    }
    
    try:
        response = requests.get(url, params=params)
        logger.info(f"GetOwnedGames API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "games" in data["response"]:
                games = data["response"]["games"]
                logger.info(f"Found {len(games)} owned games")
                return games
            else:
                logger.warning("No games found in the response")
                return []
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
            logger.debug(f"Response content: {response.text[:200]}...")
            return None
    except Exception as e:
        logger.error(f"Error fetching owned games: {e}")
        return None

def get_wishlist_from_store(steam_id):
    """
    Get the wishlist directly from the Steam store API.
    This is a different approach that doesn't use the official Steam Web API.
    """
    logger.info(f"Fetching wishlist from Steam store for Steam ID: {steam_id}")
    
    # The store API endpoint for wishlists
    url = f"https://store.steampowered.com/api/wishlist/getappwishlist"
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
                logger.info(f"Successfully parsed wishlist JSON response")
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
    profile_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
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
                logger.info(f"Successfully parsed wishlist data JSON response")
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
    for app_id, game_info in wishlist_data.items():
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
    
    # Method 3: Try to get owned games as a fallback
    logger.info("Trying to get owned games as a fallback...")
    owned_games = get_owned_games(api_key, steam_id)
    if owned_games:
        games = []
        for game in owned_games:
            if "name" in game:
                games.append(game["name"])
        
        if games:
            games.sort()
            if save_games_to_file(games):
                print(f"\nNote: Could not fetch your wishlist, but found {len(games)} owned games instead.")
                print("These have been saved to wishlist.txt as a fallback.")
                print("Next steps:")
                print("Run the main script with: python main.py -f wishlist.txt")
                return 0
    
    logger.error("All methods failed to fetch your wishlist")
    print("\nError: Could not fetch your wishlist using any method.")
    print("Possible reasons:")
    print("1. Your wishlist is private (check your Steam privacy settings)")
    print("2. Steam is rate-limiting your requests (try again later)")
    print("3. You're using a VPN (try without it)")
    print("4. Your Steam ID is incorrect")
    
    print("\nAlternative options:")
    print("1. Use the extract_wishlist_json.py script to manually extract your wishlist")
    print("2. Create a wishlist.txt file manually with your game names")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 