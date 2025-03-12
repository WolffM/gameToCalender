![image](https://github.com/user-attachments/assets/a45d3133-7412-4157-8d5f-431ba3987ae4)
# Steam Games to Calendar

This tool creates calendar events for upcoming game releases. It takes a Steam ID to fetch your wishlist, looks up the release dates using the Steam API, and creates calendar events that you can add directly to Google Calendar or import into any calendar application.

## What This Tool Does

- Fetches games directly from your Steam wishlist using your Steam ID
- Searches for games on Steam to find their release dates
- Creates calendar events for upcoming game releases (skips games already released)
- Generates a webpage where you can:
  - Add events directly to Google Calendar with one click
  - Download calendar files (.ics) to import into any calendar app
  - Bulk import all game events at once
  - View the games on Steam

## Recent Updates

- **Skip Past Releases**: The tool now automatically skips games with release dates in the past, focusing only on upcoming releases.
- **Simplified Command Structure**: You can now directly pass your Steam ID as a parameter to fetch your wishlist and create calendar events in one step.
- **Improved Error Handling**: Better handling of unparseable dates and API rate limiting.

## Complete Setup Guide (For Beginners)

### 1. Install Python

If you don't have Python installed:

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest version for your operating system (Windows, Mac, or Linux)
3. Run the installer
   - On Windows: Make sure to check "Add Python to PATH" during installation
   - On Mac/Linux: The installer should handle this automatically

To verify Python is installed, open a command prompt (Windows) or terminal (Mac/Linux) and type:
```
python --version
```
You should see something like `Python 3.10.x`

### 2. Download This Project

If you're familiar with Git:
```
git clone https://github.com/yourusername/steamGamesToCalendar.git
cd steamGamesToCalendar
```

If you're not familiar with Git:
1. Download this project as a ZIP file
2. Extract the ZIP file to a folder on your computer
3. Open a command prompt or terminal
4. Navigate to the folder where you extracted the files:
   ```
   cd path/to/steamGamesToCalendar
   ```

### 3. Get a Steam API Key

1. Go to [Steam's Web API Key page](https://steamcommunity.com/dev/apikey)
2. Sign in with your Steam account
3. Enter a domain name (you can use "localhost" if you don't have a website)
4. Click "Register" to get your API key

### 4. Create the .env File

1. In the project folder, create a new text file named `.env` (including the dot)
2. Open the file in a text editor (like Notepad, TextEdit, or VS Code)
3. Add the following line, replacing `your_steam_api_key` with the key you got from Steam:
   ```
   STEAM_API_KEY=your_steam_api_key
   ```
4. Save the file

### 5. Install Required Packages

In your command prompt or terminal (make sure you're in the project folder), run:
```
pip install -r requirements.txt
```

This installs all the necessary Python packages for the project.

## How to Use

### Running the Tool

You can run this tool in several ways:

### 1. Using Your Steam ID (Recommended)

This is the simplest method that automatically fetches your wishlist and creates calendar events:

```
python main.py YOUR_STEAM_ID
```

For example:
```
python main.py 76561197990237856
```

This will:
1. Fetch your wishlist using the Steam API
2. Look up release dates for each game
3. Create calendar events for upcoming games (skipping past releases)
4. Open a webpage with all the events

### 2. Using a Text File with Game Names

If you prefer to manually specify games:

1. Create a text file with one game name per line
2. Run the tool with the file option:

```
python main.py -f wishlist.txt
```

Example wishlist.txt content:
```
Baldur's Gate 3
Starfield
Elden Ring
Cyberpunk 2077
```

### 3. Specifying Games Directly

```
python main.py -g "Game1, Game2, Game3"
```

Replace "Game1, Game2, Game3" with the names of the games you want to track, separated by commas.

### Finding Your Steam ID

If you don't know your Steam ID:

1. Go to your Steam profile page
2. Look at the URL, which will be in one of these formats:
   - `https://steamcommunity.com/profiles/76561197990237856` (the number is your Steam ID)
   - `https://steamcommunity.com/id/username` (you'll need to use a Steam ID finder tool)
3. If your URL has a custom username, you can use a Steam ID finder like [steamid.io](https://steamid.io/) to get your numeric Steam ID

### Troubleshooting Wishlist Access

If you encounter issues accessing your wishlist:

1. **Check Privacy Settings**: Make sure your Steam profile and game details are set to public
   - Go to your Steam profile > Edit Profile > Privacy Settings
   - Set "Game details" to "Public"

2. **Try Without VPN**: Steam may block requests from VPN IP addresses

3. **Wait and Try Later**: Steam may be rate-limiting your requests. Wait a while and try again.

### What Happens Next

1. The tool will fetch your wishlist and search for each game on Steam
2. It will create calendar files for each upcoming game it finds (skipping past releases)
3. A webpage will open in your browser with all the games and their release dates
4. You'll see options to:
   - **Bulk import all events at once** (at the top of the page)
   - Add individual events to your calendar

### Adding Events to Your Calendar

#### Bulk Import (All Events at Once):
1. At the top of the webpage, click the "Download All Events (.ics)" button
2. Open your calendar application
3. Import the downloaded .ics file:
   - In Google Calendar: Click the "+" next to "Other calendars" > "Import"
   - In Apple Calendar: File > Import
   - In Outlook: File > Open & Export > Import/Export > Import an iCalendar (.ics) file

#### Google Calendar (Individual Events):
1. Click the "Add to Google Calendar" button for a specific game
2. Google Calendar will open in your browser
3. Review the event details
4. Click "Save" to add it to your calendar

#### Other Calendar Apps (Individual Events):
1. Click the "Download .ics File" button for a specific game
2. Open your calendar application
3. Import the downloaded .ics file

## Troubleshooting

### "Python is not recognized as an internal or external command"
- Make sure Python is installed and added to your PATH
- Try using `python3` instead of `python`

### "No module named 'requests'"
- Make sure you ran `pip install -r requirements.txt`
- Try using `pip3` instead of `pip`

### "No games found"
- Check that your Steam API key is correct in the .env file
- Make sure your Steam ID is correct
- Verify that your wishlist is not empty

### "Cannot fetch wishlist"
- Steam may be rate-limiting your requests. Wait a while and try again.
- If you're using a VPN, try disabling it temporarily as Steam may block requests from VPN IP addresses.
- Make sure your wishlist is public (Profile > Edit Profile > Privacy Settings)

### "Calendar events not opening"
- Make sure you have a default web browser set up
- Try downloading the .ics file and importing it manually

### "No upcoming games found"
- If all games in your wishlist have already been released, no calendar events will be created
- Try adding some unreleased games to your wishlist or manually specify future game releases
