#!/usr/bin/env python3
"""Test script to load cogs and print commands"""

import sys
import os

# Add parent directory to path to import discord
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

try:
    import discord
    from discord.ext import commands

    # Setup bot intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    # Create bot instance
    bot = commands.Bot(command_prefix='!', intents=intents)

    # Import and add cogs
    from cogs.hello_cog import HelloCog
    from cogs.chat_cog import ChatCog

    # Add cogs using the same pattern as bot.py
    def add_cog(bot, cog):
        try:
            bot.add_cog(cog).send(None)
        except StopIteration as e:
            logger.info(f'Successfully loaded {cog.__class__.__name__}')
            logger.info(f'Commands in {cog.__class__.__name__}: {[command.name for command in cog.get_commands()]}')
    
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 50)
    print("LOADING COGS...")
    print("=" * 50 + "\n")

    print("Adding HelloCog...")
    add_cog(bot, HelloCog(bot))

    print("Adding ChatCog...")
    add_cog(bot, ChatCog(bot))

    print("\n" + "=" * 50)
    print("ALL REGISTERED COMMANDS:")
    print("=" * 50)
    for command in bot.commands:
        print(f"  - {command.name}")
    print("=" * 50 + "\n")

    print("\n" + "=" * 50)
    print("ALL COMMANDS (via all_commands):")
    print("=" * 50)
    for name, command in bot.all_commands.items():
        print(f"  - {name} (cog: {command.cog_name})")
    print("=" * 50 + "\n")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()