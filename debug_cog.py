#!/usr/bin/env python3
"""Debug script to check cog loading"""

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

    # Load the hello cog
    try:
        from cogs.hello_cog import HelloCog
        print("\nImported HelloCog successfully")
    except Exception as e:
        print(f"Failed to import HelloCog: {e}")
        sys.exit(1)

    try:
        cog = HelloCog(bot)
        print("Created HelloCog instance")
    except Exception as e:
        print(f"Failed to create HelloCog instance: {e}")
        sys.exit(1)

    try:
        bot.add_cog(cog)
        print("Added HelloCog to bot")
    except Exception as e:
        print(f"Failed to add HelloCog to bot: {e}")
        sys.exit(1)

    print("\nChecking commands:")
    print(f"bot.commands length: {len(list(bot.commands))}")
    print(f"bot.walk_commands length: {len(list(bot.walk_commands()))}")
    print(f"bot.all_commands length: {len(bot.all_commands)}")

    print("\nAll commands in bot.all_commands:")
    for name, command in bot.all_commands.items():
        print(f"  - {name} (cog: {command.cog_name}, owner: {command.callback.__qualname__})")

    print("\nCommands in HelloCog:")
    cog_commands = cog.get_commands()
    print(f"HelloCog has {len(cog_commands)} commands:")
    for command in cog_commands:
        print(f"  - {command.name} (cog: {command.cog_name})")

    print("\nCommands from walk_commands:")
    for command in bot.walk_commands():
        print(f"  - {command.name} (cog: {command.cog_name})")

    # Check if hello command exists
    if 'hello' in bot.all_commands:
        print("\n✓ 'hello' command found in bot.all_commands")
        print(f"  Command details: {bot.all_commands['hello']}")
    else:
        print("\n✗ 'hello' command NOT found in bot.all_commands")

    if 'hello' in cog.get_commands():
        print("✓ 'hello' command found in HelloCog.get_commands()")
    else:
        print("✗ 'hello' command NOT found in HelloCog.get_commands()")

    # Try to get the command
    try:
        hello_cmd = bot.get_command('hello')
        if hello_cmd:
            print(f"✓ bot.get_command('hello') returned: {hello_cmd}")
        else:
            print("✗ bot.get_command('hello') returned None")
    except Exception as e:
        print(f"✗ Error getting 'hello' command: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()