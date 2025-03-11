#!/usr/bin/env python3
import sys
import argparse
import webbrowser
import os
from steam_api import get_game_release_info
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

def main():
    """
    Main function to process game list and create calendar events.
    """
    parser = argparse.ArgumentParser(description='Create calendar events for upcoming game releases.')
    parser.add_argument('games', nargs='?', help='Comma-separated list of game names')
    parser.add_argument('-f', '--file', help='File containing game names, one per line')
    parser.add_argument('-o', '--output-dir', default='calendar_events', help='Directory to save calendar files')
    
    args = parser.parse_args()
    
    # Get game list from command line or file
    games = []
    if args.games:
        games = parse_game_list(args.games)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                games = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading game list file: {e}")
            return 1
    else:
        parser.print_help()
        return 1
    
    if not games:
        print("No games specified.")
        return 1
    
    print(f"Processing {len(games)} games...")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Process each game
    successful_events = 0
    game_events = []
    
    for game_name in games:
        print(f"\nProcessing game: {game_name}")
        
        # Get game release information
        game_info = get_game_release_info(game_name)
        if not game_info:
            print(f"Could not find release information for '{game_name}'. Skipping.")
            continue
        
        # Print game information
        print(f"Found game: {game_info.get('name')}")
        if isinstance(game_info.get('release_date'), str):
            print(f"Release date: {game_info.get('release_date')} (unparsed)")
        elif game_info.get('release_date'):
            print(f"Release date: {game_info.get('release_date').strftime('%Y-%m-%d')}")
        else:
            print("Release date: Unknown")
        
        print(f"Coming soon: {'Yes' if game_info.get('is_coming_soon') else 'No'}")
        
        # Create calendar event file
        file_path = create_ics_file(game_info, args.output_dir)
        if file_path:
            successful_events += 1
            game_events.append({
                'game_info': game_info,
                'file_path': file_path
            })
    
    # Create HTML page with links to all events
    if game_events:
        html_file = create_html_calendar_page(game_events)
        if html_file:
            print(f"\nCreated HTML page with calendar events: {html_file}")
            # Open the HTML file in the default browser
            webbrowser.open('file://' + os.path.abspath(html_file))
    
    # Print summary
    print(f"\nSummary: Created {successful_events} calendar event files out of {len(games)} games.")
    print(f"Calendar files are saved in the '{args.output_dir}' directory.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 