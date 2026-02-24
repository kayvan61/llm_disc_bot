#!/usr/bin/env python3
"""Test script to check if hello command is registered"""

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

    # Add a callback to on_ready to print commands
    @bot.event
    async def on_ready():
        print("\n" + "=" * 50)
        print("BOT READY - ALL COMMANDS:")
        print("=" * 50)

        print("\nUsing bot.commands:")
        for command in bot.commands:
            print(f"  - {command.name} (cog: {command.cog_name})")

        print("\nUsing bot.walk_commands:")
        for command in bot.walk_commands():
            print(f"  - {command.name} (cog: {command.cog_name})")

        print("\nUsing bot.all_commands:")
        for name, command in bot.all_commands.items():
            print(f"  - {name} (cog: {command.cog_name})")

        print("=" * 50 + "\n")

        # Load the hello cog
        from cogs.hello_cog import HelloCog
        cog = HelloCog(bot)
        bot.add_cog(cog)

        print("\n" + "=" * 50)
        print("AFTER LOADING HELLO COG:")
        print("=" * 50)

        print("\nUsing bot.commands:")
        for command in bot.commands:
            print(f"  - {command.name} (cog: {command.cog_name})")

        print("\nUsing bot.walk_commands:")
        for command in bot.walk_commands():
            print(f"  - {command.name} (cog: {command.cog_name})")

        print("\nUsing bot.all_commands:")
        for name, command in bot.all_commands.items():
            print(f"  - {name} (cog: {command.cog_name})")

        print("=" * 50 + "\n")

        # Cancel the event
        await bot.close()

    # Start the bot
    bot.run(os.getenv('DISCORD_TOKEN'))

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()