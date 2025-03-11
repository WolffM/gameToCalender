# Steam Games to Calendar

This tool creates calendar events for upcoming game releases. It takes a comma-separated list of game names, looks up their release dates using the Steam API, and creates calendar events that you can add directly to Google Calendar or import into any calendar application.

## What This Tool Does

- Searches for games on Steam to find their release dates
- Creates calendar events for each game's release date
- Generates a webpage where you can:
  - Add events directly to Google Calendar with one click
  - Download calendar files (.ics) to import into any calendar app
  - View the games on Steam

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

In your command prompt or terminal, run:

```
python main.py "Game1, Game2, Game3"
```

Replace "Game1, Game2, Game3" with the names of the games you want to track, separated by commas.

For example:
```
python main.py "Starfield, Elden Ring, Hollow Knight: Silksong"
```

If you have a lot of games, you can put them in a text file (one game per line) and run:
```
python main.py -f games.txt
```

### What Happens Next

1. The tool will search for each game on Steam
2. It will create calendar files for each game it finds
3. A webpage will open in your browser with all the games and their release dates
4. For each game, you'll see three buttons:
   - **Add to Google Calendar**: Opens Google Calendar with the event details
   - **Download .ics File**: Downloads a calendar file you can import into any calendar app
   - **View on Steam**: Opens the game's page on Steam

### Adding Events to Your Calendar

#### Google Calendar:
1. Click the "Add to Google Calendar" button
2. Google Calendar will open in your browser
3. Review the event details
4. Click "Save" to add it to your calendar

#### Other Calendar Apps (Apple Calendar, Outlook, etc.):
1. Click the "Download .ics File" button
2. Open your calendar application
3. Import the downloaded .ics file:
   - In Apple Calendar: File > Import
   - In Outlook: File > Open & Export > Import/Export > Import an iCalendar (.ics) file
   - In other apps: Look for an "Import" option in the menu

## Troubleshooting

### "Python is not recognized as an internal or external command"
- Make sure Python is installed and added to your PATH
- Try using `python3` instead of `python`

### "No module named 'requests'"
- Make sure you ran `pip install -r requirements.txt`
- Try using `pip3` instead of `pip`

### "No games found"
- Check that your Steam API key is correct in the .env file
- Make sure the game names are spelled correctly
- Some games might not be available on Steam

### "Calendar events not opening"
- Make sure you have a default web browser set up
- Try downloading the .ics file and importing it manually

## Need Help?

If you're having trouble, feel free to open an issue on GitHub or contact me at [your email or contact info]. 