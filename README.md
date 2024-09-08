# Discord Download Request Bot

## Description

This Discord bot manages and tracks links posted in specific channels. It allows users to search for downloads by number, ignore specific users, and manage link channels.

It checks for posts with the following:
- A DN number (`'DN : (.+)'`)
- A Link (`'Link : (https?://\S+)'`)
## Features

- Track links posted in designated channels
- Search for downloads by number
- Ignore specific users
- Manage link channels (add, remove, scan)
- Automatic scanning of messages in link channels

## Requirements

- Python 3.8+
- py-chord
- python-dotenv

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

The bot uses a `config.json` file to store settings. If it doesn't exist, it will be created automatically with default values.

## Usage

To start the bot, run:

`python bot.py`


## Commands

- `/download <number>`: Search for a download by number
- `/ignore <user>`: Ignore a specific user (Admin only)
- `/linkchannel <action> [channel]`: Manage link channels (Admin only)
  - Actions: `add`, `remove`, `scan`
  (When `scan` is used without a channel, it will scan all channels which are set in the config.json)

## Database

The bot uses a CSV file (`database.csv`) to store download information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under The Unlicense. This means it's free and unencumbered software released into the public domain. For more information, please refer to <http://unlicense.org/>

## Disclaimer

This bot is a hobby project and is provided "as is", without warranty of any kind, express or implied. The authors or copyright holders shall not be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

Use this code at your own risk. The creator(s) of this bot are not responsible for any misuse, damage, or legal issues that may arise from using this software. It is the user's responsibility to ensure they have the necessary permissions and rights to use and interact with Discord servers and to manage the data collected by this bot.
