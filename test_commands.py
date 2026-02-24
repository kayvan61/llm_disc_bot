#!/usr/bin/env python3
"""Simple test to verify the bot is working"""

import sys
import os

# Add parent directory to path to import discord
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Check if the bot is loaded correctly
try:
    import discord
    from discord.ext import commands

    # Create a bot instance without running it
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    # Load the cog
    from cogs.hello_cog import HelloCog
    cog = HelloCog(bot)
    bot.add_cog(cog)

    # Check commands
    commands = cog.get_commands()
    print(f"Commands loaded: {[command.name for command in commands]}")

    if 'hello' in [command.name for command in commands]:
        print("✓ Command 'hello' is properly registered")
    else:
        print("✗ Command 'hello' is not registered")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()