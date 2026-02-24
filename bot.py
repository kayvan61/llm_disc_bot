import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio
from cogs.hello_cog import HelloCog
from cogs.chat_cog import ChatCog

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True


# Create bot instance with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready and has connected to Discord"""
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Successfully connected to {len(bot.guilds)} guilds')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Unknown command. Use !hello to get started.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide the required arguments.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument provided.')
    else:
        logger.error(f'Error in command {ctx.command.name}: {str(error)}')
        await ctx.send('An error occurred while processing your command.')

@bot.event
async def on_message(message):
    """Handle all messages and pass to bot commands"""
    # Ignore messages from the bot itself
    if message.author.bot:
        return

    # Log all messages for debugging
    logger.info(f'Received message from {message.author} in {message.guild.name if message.guild else "DM"}: {message.content}')

    # Pass messages to command processing
    await bot.process_commands(message)

def add_cog(bot, cog):
    try:
        bot.add_cog(cog).send(None)
    except StopIteration as e:
        logger.info(f'Successfully loaded {cog.__class__.__name__}')
        logger.info(f'Commands in {cog.__class__.__name__}: {[command.name for command in cog.get_commands()]}')
    
def main():
    # Load the hello cog
    try:
        logger.info('adding Hello Cog...')
        add_cog(bot, HelloCog(bot))
        logger.info('adding Chat Cog...')
        add_cog(bot, ChatCog(bot))
    except ImportError:
        logger.error('Failed to load HelloCog - file not found')

    # Print all commands from bot.commands after cogs are loaded
    print("\n" + "=" * 50)
    print("ALL REGISTERED COMMANDS:")
    print("=" * 50)
    for command in bot.commands:
        print(f"  - {command.name}")
    print("=" * 50 + "\n")

    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')

    if token and token != 'your_discord_bot_token_here':
        logger.info('Starting bot...')
        bot.run(token)
    else:
        logger.error('DISCORD_TOKEN not found or not set correctly in .env file')
        logger.error(f'DISCORD_TOKEN={token}')
        print('Please set your Discord bot token in the .env file and run the bot again.')

# Run the main function
main()
