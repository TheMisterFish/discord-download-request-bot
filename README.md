# Discord Download Request Bot
![ArchiverBotBanner_a4](https://github.com/user-attachments/assets/c5f70ade-8acb-41c6-8268-830b096dc8d2)

## Description

This Discord bot manages and tracks links posted in specific channels. It allows users to search for downloads by name or ID, manage ignored users, configure link channels, and view logs. The bot is designed to work with multiple servers, maintaining separate configurations and logs for each.

## Features

- Track links posted in designated download and video channels
- Search for downloads by name or ID
- Search for videos by title
- Ignore specific users
- Manage download channels, video channels, and allowed download channels
- View and download server-specific logs
- Automatic scanning of messages in link channels
- Server-specific configurations and databases
- Cooldown management for commands
- Configurable search regex for download messages

## Requirements

- Python 3.8+
- py-cord
- python-dotenv
- fuzzywuzzy
- python-Levenshtein
- pandas

## Installation

1. Clone the repository:

```git clone https://github.com/TheMisterFish/discord-download-request-bot.git``` 
& 
 ```cd discord-download-request-bot ```

2. **(Optional!)** Create a virtual environment: 

```python -m venv venv source venv/bin/activate # On Windows use venv\Scripts\activate```


3. Install the required packages:

```pip install -r requirements.txt```


4. Create a `.env` file in the root directory and add your Discord bot token:

```BOT_TOKEN=your_bot_token_here```


## Configuration

The bot uses server-specific configuration files stored in `data/<server_id>/config.json`. These are created automatically with default values when the bot joins a new server. The configuration includes settings for cooldowns, allowed channels, ignored users, video channels, download channels, and search regex.

## Usage

To start the bot, run:

`python bot.py`


## Commands

### User Commands
- `/download [name] [id]`: Search for a download by name or ID. Use either name or ID.
- `/dn <input>`: Shortcut for /download. Enter download name or ID.
- `/video <title>`: Search for a video by title.
- `/help`: Display available commands and their descriptions.

### Moderator Commands
- `/log [action] [limit] [page]`: Download log file or view recent logs. Actions: download, view.
- `/config allowed_download_channels [action] [channel]`: Manage allowed channels to download from (add, remove, list).
- `/config ignore [action] [user]`: Ignore, unignore, or list ignored users.
- `/config videochannel [action] [channel]`: Manage video channels (add, remove, scan, list).
- `/config downloadchannel [action] [channel]`: Manage channels where download links can be found (add, remove, scan, list).

### Admin Commands
- `/config cooldown [limit] [timeout]`: Configure cooldown settings for /download, /dn, and /video commands.
- `/config admin_download [allow]`: Configure admin download permissions.
- `/config search_regex [regex]`: Configure the search regex for download messages.
- `/config reset_regex`: Reset the search regex to default (DN : (.+)).

## Database

The bot uses CSV files to store download and video information for each server:
- `data/<server_id>/download_database.csv`
- `data/<server_id>/video_database.csv`

## Logging

The bot maintains separate log files for each server at `data/<server_id>/bot_commands.log`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under The Unlicense. This means it's free and unencumbered software released into the public domain. For more information, please refer to <http://unlicense.org/>

## Disclaimer

<p align="center">
  <img src="https://github.com/user-attachments/assets/188306c5-6079-4f3e-80fd-e2f9c7449cd5" alt="Designer (3)" width="150px">
</p>

This bot is a hobby project and is provided "as is", without warranty of any kind, express or implied. The authors or copyright holders shall not be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

Use this code at your own risk. The creator(s) of this bot are not responsible for any misuse, damage, or legal issues that may arise from using this software. It is the user's responsibility to ensure they have the necessary permissions and rights to use and interact with Discord servers and to manage the data collected by this bot.
