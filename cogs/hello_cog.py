import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class HelloCog(commands.Cog):
    """A cog that handles the hello command"""

    def __init__(self, bot):
        """Initialize the cog with the bot instance"""
        self.bot = bot
        logger.info('HelloCog initialized')

    @commands.command(name='hello')
    async def hello(self, ctx):
        """Responds with 'hello' to the user"""
        logger.info(f'Hello command invoked by {ctx.author} in {ctx.guild}')
        await ctx.send(f'Hello {ctx.author.display_name}! 👋')
