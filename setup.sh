#!/bin/bash
# Setup script for the Discord bot

echo "Setting up Discord bot..."

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Activating..."
else
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Discord Bot API Key
# Add your bot token below (obtained from Discord Developer Portal)
# Example: DISCORD_TOKEN=your_bot_token_here
DISCORD_TOKEN=your_discord_bot_token_here
EOF
    echo ".env file created!"
    echo "Please edit the .env file and add your Discord bot token."
    echo "You can get your bot token from the Discord Developer Portal."
else
    echo ".env file found. Ready to run!"
fi

echo "Setup complete!"
echo "To run the bot, activate the virtual environment and run: python bot.py"