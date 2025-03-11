import os
import uuid
from datetime import datetime, timedelta
import urllib.parse

def create_ics_file(game_info, output_dir="calendar_events"):
    """
    Create an .ics file for a game release that can be imported into any calendar app.
    
    Args:
        game_info (dict): Information about the game.
        output_dir (str): Directory to save the .ics file.
        
    Returns:
        str: Path to the created .ics file or None if failed.
    """
    # Check if we have a valid release date
    release_date = game_info.get('release_date')
    if not release_date:
        print(f"No release date available for {game_info.get('name')}")
        return None
    
    # Handle string dates (when we couldn't parse the date)
    if isinstance(release_date, str):
        print(f"Using string date for {game_info.get('name')}: {release_date}")
        # Try to create an approximate date if it's just a year or month/year
        if release_date.isdigit() and len(release_date) == 4:  # Just a year
            release_date = datetime(int(release_date), 1, 1)
        else:
            print(f"Cannot create event with unparseable date: {release_date}")
            return None
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Format dates for iCalendar
    start_date = release_date.strftime("%Y%m%d")
    end_date = (release_date + timedelta(days=1)).strftime("%Y%m%d")
    
    # Create a unique identifier for the event
    event_uid = str(uuid.uuid4())
    
    # Create event details
    game_name = game_info.get('name', 'Unknown Game')
    description = game_info.get('short_description', '')
    
    # Add Steam store link to description
    description += f"\n\nSteam Store Link: https://store.steampowered.com/app/{game_info.get('app_id')}"
    
    # Format description for iCalendar (replace newlines with \\n)
    ics_description = description.replace('\n', '\\n')
    
    # Create the .ics content
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Steam Games Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{event_uid}",
        f"SUMMARY:Game Release: {game_name}",
        f"DESCRIPTION:{ics_description}",
        f"DTSTART;VALUE=DATE:{start_date}",
        f"DTEND;VALUE=DATE:{end_date}",
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "TRIGGER:-P1D",  # 1 day before
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR"
    ]
    
    # Create a safe filename
    safe_name = "".join([c if c.isalnum() else "_" for c in game_name])
    file_path = os.path.join(output_dir, f"{safe_name}_release.ics")
    
    # Write the .ics file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\r\n".join(ics_content))
        print(f"Created calendar event file for {game_name}: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to create calendar event file for {game_name}: {e}")
        return None

def create_combined_ics_file(game_events, output_dir="calendar_events", filename="all_game_releases.ics"):
    """
    Create a single .ics file containing all game release events for bulk import.
    
    Args:
        game_events (list): List of dictionaries with game info.
        output_dir (str): Directory to save the .ics file.
        filename (str): Name of the combined .ics file.
        
    Returns:
        str: Path to the created .ics file or None if failed.
    """
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Start the calendar file
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Steam Games Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    # Add each game as an event
    valid_events = 0
    for event in game_events:
        game_info = event['game_info']
        
        # Check if we have a valid release date
        release_date = game_info.get('release_date')
        if not release_date:
            print(f"Skipping {game_info.get('name')} - No release date available")
            continue
        
        # Handle string dates (when we couldn't parse the date)
        if isinstance(release_date, str):
            # Try to create an approximate date if it's just a year or month/year
            if release_date.isdigit() and len(release_date) == 4:  # Just a year
                release_date = datetime(int(release_date), 1, 1)
            else:
                print(f"Skipping {game_info.get('name')} - Cannot use unparseable date: {release_date}")
                continue
        
        # Format dates for iCalendar
        start_date = release_date.strftime("%Y%m%d")
        end_date = (release_date + timedelta(days=1)).strftime("%Y%m%d")
        
        # Create a unique identifier for the event
        event_uid = str(uuid.uuid4())
        
        # Create event details
        game_name = game_info.get('name', 'Unknown Game')
        description = game_info.get('short_description', '')
        
        # Add Steam store link to description
        description += f"\n\nSteam Store Link: https://store.steampowered.com/app/{game_info.get('app_id')}"
        
        # Format description for iCalendar (replace newlines with \\n)
        ics_description = description.replace('\n', '\\n')
        
        # Add the event to the calendar
        ics_content.extend([
            "BEGIN:VEVENT",
            f"UID:{event_uid}",
            f"SUMMARY:Game Release: {game_name}",
            f"DESCRIPTION:{ics_description}",
            f"DTSTART;VALUE=DATE:{start_date}",
            f"DTEND;VALUE=DATE:{end_date}",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "TRIGGER:-P1D",  # 1 day before
            "END:VALARM",
            "END:VEVENT"
        ])
        
        valid_events += 1
    
    # End the calendar file
    ics_content.append("END:VCALENDAR")
    
    # If no valid events, don't create the file
    if valid_events == 0:
        print("No valid events to include in the combined calendar file.")
        return None
    
    # Write the combined .ics file
    file_path = os.path.join(output_dir, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\r\n".join(ics_content))
        print(f"Created combined calendar file with {valid_events} events: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to create combined calendar file: {e}")
        return None

def create_google_calendar_link(game_info):
    """
    Create a Google Calendar link for a game release.
    
    Args:
        game_info (dict): Information about the game.
        
    Returns:
        str: Google Calendar link.
    """
    # Check if we have a valid release date
    release_date = game_info.get('release_date')
    if not release_date or isinstance(release_date, str):
        # If no valid date, return None
        return None
    
    # Format dates for Google Calendar
    start_date = release_date.strftime("%Y%m%d")
    end_date = (release_date + timedelta(days=1)).strftime("%Y%m%d")
    
    # Create event details
    game_name = game_info.get('name', 'Unknown Game')
    title = f"Game Release: {game_name}"
    
    # Create description with Steam link
    description = game_info.get('short_description', '')
    description += f"\n\nSteam Store Link: https://store.steampowered.com/app/{game_info.get('app_id')}"
    
    # Create Google Calendar link
    base_url = "https://calendar.google.com/calendar/render"
    params = {
        'action': 'TEMPLATE',
        'text': title,
        'dates': f"{start_date}/{end_date}",
        'details': description,
        'sf': 'true',
        'output': 'xml'
    }
    
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def create_html_calendar_page(game_info_list, output_dir="calendar_events", output_file="game_releases.html"):
    """
    Create an HTML page with links to all the calendar events.
    
    Args:
        game_info_list (list): List of dictionaries with game info.
        output_dir (str): Directory to save the HTML file.
        output_file (str): Name of the HTML file.
        
    Returns:
        str: Path to the created HTML file.
    """
    # Create combined calendar file for bulk import
    game_events = [{'game_info': info} for info in game_info_list]
    combined_ics_path = create_combined_ics_file(game_events, output_dir)
    combined_ics_filename = os.path.basename(combined_ics_path) if combined_ics_path else None
    
    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "    <title>Game Release Calendar Events</title>",
        "    <style>",
        "        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
        "        h1, h2 { color: #333; }",
        "        .bulk-section { background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 30px; }",
        "        .game-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; }",
        "        .game-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }",
        "        .game-date { color: #666; margin-bottom: 10px; }",
        "        .game-desc { margin-bottom: 15px; }",
        "        .button { display: inline-block; padding: 10px 15px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-right: 10px; }",
        "        .google-button { background-color: #4285f4; color: white; }",
        "        .google-button:hover { background-color: #3367d6; }",
        "        .download-button { background-color: #34a853; color: white; }",
        "        .download-button:hover { background-color: #2e8b57; }",
        "        .steam-button { background-color: #171a21; color: white; }",
        "        .steam-button:hover { background-color: #2a3f5f; }",
        "        .bulk-button { background-color: #ea4335; color: white; font-size: 1.1em; padding: 12px 20px; }",
        "        .bulk-button:hover { background-color: #d33426; }",
        "    </style>",
        "</head>",
        "<body>",
        "    <h1>Game Release Calendar Events</h1>"
    ]
    
    # Add bulk import section if we have a combined file
    if combined_ics_filename:
        html_content.extend([
            "    <div class='bulk-section'>",
            "        <h2>Bulk Import All Events</h2>",
            "        <p>Click the button below to download a single calendar file with all game release events:</p>",
            f"        <a href='{combined_ics_filename}' class='button bulk-button'>Download All Events (.ics)</a>",
            "    </div>",
            "    <h2>Individual Game Events</h2>"
        ])
    
    # Add individual game cards
    for info in game_info_list:
        game_info = info
        file_path = create_ics_file(game_info)
        
        # Format the release date
        release_date = game_info.get('release_date')
        date_str = "Unknown date"
        if isinstance(release_date, datetime):
            date_str = release_date.strftime("%B %d, %Y")
        elif isinstance(release_date, str):
            date_str = release_date
        
        # Create Google Calendar link
        google_cal_link = create_google_calendar_link(game_info)
        
        # Create a card for each game
        html_content.extend([
            "    <div class='game-card'>",
            f"        <div class='game-title'>{game_info.get('name', 'Unknown Game')}</div>",
            f"        <div class='game-date'>Release Date: {date_str}</div>",
            f"        <div class='game-desc'>{game_info.get('short_description', '')}</div>",
            "        <div class='button-group'>"
        ])
        
        # Add Google Calendar button if we have a valid date
        if google_cal_link:
            html_content.append(f"            <a href='{google_cal_link}' class='button google-button' target='_blank'>Add to Google Calendar</a>")
        
        # Add download .ics file button
        html_content.append(f"            <a href='{os.path.basename(file_path)}' class='button download-button'>Download .ics File</a>")
        
        # Add Steam store link
        html_content.append(f"            <a href='https://store.steampowered.com/app/{game_info.get('app_id')}' class='button steam-button' target='_blank'>View on Steam</a>")
        
        html_content.extend([
            "        </div>",
            "    </div>"
        ])
    
    html_content.extend([
        "</body>",
        "</html>"
    ])
    
    # Write the HTML file
    try:
        with open(os.path.join(output_dir, output_file), 'w', encoding='utf-8') as f:
            f.write("\n".join(html_content))
        print(f"Created HTML calendar page: {output_file}")
        return os.path.join(output_dir, output_file)
    except Exception as e:
        print(f"Failed to create HTML calendar page: {e}")
        return None 