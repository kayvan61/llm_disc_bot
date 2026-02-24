#!/usr/bin/env python3
"""Test script to verify the bot configuration"""

import sys
import os

# Add parent directory to path to import dotenv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

def test_dotenv_loading():
    """Test that .env file is loaded correctly"""
    print("Testing .env file loading...")
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print(f"✓ DISCORD_TOKEN loaded successfully")
        print(f"✓ Token prefix: {token[:5]}...")
    else:
        print("✗ DISCORD_TOKEN not found in .env file")
    print()

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    try:
        import discord
        print(f"✓ discord.py version {discord.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import discord.py: {e}")
        return False
    
    try:
        from discord.ext import commands
        print(f"✓ discord.ext.commands imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import discord.ext.commands: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print(f"✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-dotenv: {e}")
        return False
    
    try:
        from cogs.hello_cog import HelloCog
        print(f"✓ HelloCog imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import HelloCog: {e}")
        return False
    
    print()
    return True

def test_bot_config():
    """Test bot configuration"""
    print("Testing bot configuration...")
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("✗ No bot token found")
        return False
    
    if token == 'your_discord_bot_token_here':
        print("✗ Using placeholder token. Please add your actual token to .env file")
        return False
    
    print(f"✓ Bot token is present and valid")
    print()
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Discord Bot Configuration Test")
    print("=" * 50)
    print()
    
    test_dotenv_loading()
    
    if not test_imports():
        print("\n✗ Import tests failed. Please install dependencies with:")
        print("   pip install -r requirements.txt")
        return
    
    if not test_bot_config():
        print("\n✗ Configuration tests failed.")
        print("Please ensure your .env file is set up correctly.")
        return
    
    print("=" * 50)
    print("✓ All tests passed! The bot is ready to run.")
    print("=" * 50)
    print("\nTo start the bot, run: python bot.py")

if __name__ == '__main__':
    main()