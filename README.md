# Discord Bot Setup Guide

This is a simple Discord bot built with Python using Discord cogs.

## Prerequisites

1. Python 3.8 or higher installed
2. A Discord Developer Account with a bot application created
3. Your bot token from the Discord Developer Portal

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Your Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select an existing one
3. Go to the Bot tab and create a bot
4. Copy the token
5. Open the `.env` file and add your token:

```env
DISCORD_TOKEN=your_actual_bot_token_here
```

**Note:** The setup script will create the `.env` file automatically if it doesn't exist. You just need to edit it with your actual token.

### 3. Run the Bot

```bash
python bot.py
```

Or use the setup script to automate the process:

```bash
./setup.sh
python bot.py
```

## Usage

- The bot listens for commands starting with `!`
- Type `!hello` to get a hello response
- The bot will only respond to users, not other bots
- The bot will reply to the user's display name

## Testing Your Configuration

Before running the bot, you can test your configuration with the test script:

```bash
python test_bot.py
```

This will verify that:
- The .env file is loaded correctly
- All required modules are installed
- Your bot token is valid

## Features

- **Discord Cogs**: Modular command structure using cogs
- **Logging**: Console and file logging for debugging
- **Error Handling**: Graceful error handling for commands
- **Security**: .env file for storing sensitive credentials
- **Self-Response Prevention**: Bot won't respond to itself

## Project Structure

```
llms-on-disc/
├── bot.py                 # Main bot entry point
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (bot token)
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── cogs/
    └── hello_cog.py     # Hello command implementation
```

## Troubleshooting

**Bot not responding:**
- Check that the bot is online in the Discord Developer Portal
- Verify the token is correctly set in .env
- Ensure the bot has been added to your server
- Check the console logs for error messages

**Module not found errors:**
- Make sure you've activated the virtual environment
- Run `pip install -r requirements.txt` again

**Permission errors:**
- Make sure the bot has been given necessary permissions in your server
- Check that the bot has been added to the server