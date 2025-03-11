#!/usr/bin/env python3
import sys
import argparse
import webbrowser
import os
from steam_api import get_game_release_info, get_wishlist
from calendar_generator import create_ics_file, create_html_calendar_page

def parse_game_list(game_list_str):
    """
    Parse a comma-separated list of game names.
    
    Args:
        game_list_str (str): Comma-separated list of game names.
        
    Returns:
        list: List of game names.
    """
    if not game_list_str:
        return []
    
    # Split by comma and strip whitespace
    return [game.strip() for game in game_list_str.split(',') if game.strip()]

def read_games_from_file(file_path):
    """
    Read game names from a file, one per line.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        list: List of game names.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read lines, strip whitespace, and filter out empty lines and comments
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Create calendar events for game releases.')
    
    # Add arguments
    parser.add_argument('games', nargs='?', help='Comma-separated list of game names')
    parser.add_argument('-f', '--file', help='File with game names, one per line')
    parser.add_argument('-w', '--wishlist', help='Fetch games from wishlist using Steam ID, vanity URL, or full wishlist URL')
    parser.add_argument('-o', '--output-dir', default='calendar_events', help='Directory to save calendar files')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Get games from wishlist, file, or command line
    games = []
    
    if args.wishlist:
        print(f"Fetching games from Steam wishlist: {args.wishlist}")
        print("First trying the Steam API method...")
        games = get_wishlist(args.wishlist, use_api=True)
        
        if not games:
            print("\nAPI method failed. Trying web scraping method...")
            games = get_wishlist(args.wishlist, use_api=False)
        
        if not games:
            print("\nUnable to fetch games from your wishlist automatically.")
            print("As an alternative, you can create a text file with your wishlist games and use the -f option:")
            print("1. Create a text file (e.g., wishlist.txt)")
            print("2. Add one game name per line")
            print("3. Run: python main.py -f wishlist.txt")
            print("\nExample wishlist.txt content:")
            print("Baldur's Gate 3")
            print("Starfield")
            print("Elden Ring")
            sys.exit(1)
        
        print(f"Found {len(games)} games in your wishlist")
    elif args.games:
        games = parse_game_list(args.games)
    elif args.file:
        games = read_games_from_file(args.file)
    else:
        parser.print_help()
        return 1
    
    if not games:
        print("No games specified. Please provide games using one of the available options.")
        return 1
    
    print(f"Processing {len(games)} games...")
    
    # Get release info for each game
    game_info = []
    for game in games:
        print(f"Looking up release date for: {game}")
        release_info = get_game_release_info(game)
        
        if release_info:
            game_info.append(release_info)
            print(f"Found release date for {release_info['name']}: {release_info['release_date']}")
        else:
            print(f"Could not find release date for: {game}")
    
    if not game_info:
        print("Could not find release dates for any of the specified games.")
        return 1
    
    # Create calendar files
    ics_files = []
    for info in game_info:
        ics_file = create_ics_file(info, args.output_dir)
        if ics_file:
            ics_files.append((info, ics_file))
    
    # Create HTML page
    html_file = create_html_calendar_page(game_info, args.output_dir)
    
    # Open HTML page in browser
    if html_file:
        print(f"Opening calendar page: {html_file}")
        webbrowser.open(f"file://{os.path.abspath(html_file)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 