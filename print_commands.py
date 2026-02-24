#!/usr/bin/env python3
"""Test script to print all registered commands"""

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
    from cogs.hello_cog import HelloCog
    cog = HelloCog(bot)
    bot.add_cog(cog)

    # Print all commands from bot.walk_commands (includes all commands)
    print("\n" + "=" * 50)
    print("ALL REGISTERED COMMANDS (via walk_commands):")
    print("=" * 50)
    for command in bot.walk_commands():
        print(f"  - {command.name}")
    print("=" * 50 + "\n")

    # Print all commands from bot.commands
    print("\n" + "=" * 50)
    print("ALL REGISTERED COMMANDS (via bot.commands):")
    print("=" * 50)
    for command in bot.commands:
        print(f"  - {command.name}")
    print("=" * 50 + "\n")

    # Also print commands grouped by cog
    print("\n" + "=" * 50)
    print("COMMANDS BY COG:")
    print("=" * 50)
    for cog_name, cog_instance in bot.cogs.items():
        print(f"\n{cog_name}:")
        for command in cog_instance.get_commands():
            print(f"  - {command.name}")
    print("=" * 50 + "\n")

    # Print commands from bot.walk_commands grouped by cog
    print("\n" + "=" * 50)
    print("COMMANDS GROUPED BY COG (from walk_commands):")
    print("=" * 50)
    command_groups = {}
    for command in bot.walk_commands():
        if command.cog_name not in command_groups:
            command_groups[command.cog_name] = []
        command_groups[command.cog_name].append(command.name)

    for cog_name, commands in command_groups.items():
        print(f"\n{cog_name}:")
        for cmd_name in commands:
            print(f"  - {cmd_name}")
    print("=" * 50 + "\n")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()