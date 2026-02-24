import discord
from discord.ext import commands
import logging
import re
import aiohttp

logger = logging.getLogger(__name__)

class ChatCog(commands.Cog):
    """A cog that handles chat interactions with an OpenAI-compatible LLM"""

    def __init__(self, bot):
        """Initialize the cog with the bot instance"""
        self.bot = bot
        self.llm_url = "http://192.168.1.148:8080/v1"
        self.current_model = "glm-4.7-30b"
        logger.info('ChatCog initialized')

    def extract_model(self, message: str) -> tuple[str, str]:
        """Extract model name from message if present.
        Returns tuple of (model_name, remaining_message)"""
        model_pattern = r'/([^/]+)/'
        match = re.search(model_pattern, message)
        if match:
            model = match.group(1)
            remaining = message[:match.start()] + message[match.end():]
            return model, remaining.strip()
        return self.current_model, message

    @commands.command(name='chat_history', aliases=['chat_hist', 'history_chat'])
    async def chat_history(self, ctx, num_messages: int, *, message: str):
        """Responds to the user using the OpenAI-compatible LLM with chat history"""
        try:
            model, clean_message = self.extract_model(message)
            logger.info(f'Chat history command invoked by {ctx.author} in {ctx.guild.name if ctx.guild else "DM"}: {clean_message} (model: {model}, history: {num_messages} messages)')

            if model != self.current_model:
                self.current_model = model

            if not clean_message:
                await ctx.send('Please provide a message to send to the AI.')
                return

            if num_messages < 1 or num_messages > 200:
                await ctx.send('Please provide a number between 1 and 200 for message history.')
                return

            channel = ctx.channel
            messages = [msg async for msg in channel.history(limit=num_messages+1)]
            messages = messages[::-1]
            messages = messages[:-1]

            await ctx.send("🤔 Thinking...")
            
            user_names = set()
            history_messages = []
            for msg in messages:
                if msg.author != ctx.bot.user:
                    user_names.add(msg.author.name)
                if msg.author == ctx.bot.user:
                    history_messages.append({"role": "assistant", "content": msg.content})
                else:
                    history_messages.append({
                        "role": "user",
                        "content": f"{msg.author.name}: {msg.content}"
                    })

            user_list = ", ".join(sorted(user_names))
            system_prompt = f"You are a helpful assistant participating in a group chat with multiple users. The users are: {user_list}."

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *history_messages,
                    {"role": "user", "content": clean_message}
                ],
                "temperature": 0.7
            }

            logger.info(f"sending chat: {payload}")

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.llm_url}/chat/completions", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI")
                        
                        logger.info(f'AI response received: {ai_response[:100]}...')
                        await ctx.send(f'🤖 {ai_response}')
                    else:
                        error_text = await response.text()
                        logger.error(f'LLM API error: {response.status} - {error_text}')
                        await ctx.send(f'Error from AI server: {response.status}')

        except aiohttp.ClientError as e:
            logger.error(f'Network error calling LLM: {str(e)}')
            await ctx.send(f'Network error: {str(e)}')
        except Exception as e:
            logger.error(f'Error in chat_history command: {str(e)}')
            await ctx.send(f'Error: {str(e)}')

    @commands.command(name='chat', aliases=['ask', 'ai'])
    async def chat(self, ctx, *, message: str):
        """Responds to the user using the OpenAI-compatible LLM"""
        try:
            model, clean_message = self.extract_model(message)
            logger.info(f'Chat command invoked by {ctx.author} in {ctx.guild.name if ctx.guild else "DM"}: {clean_message} (model: {model})')

            if model != self.current_model:
                self.current_model = model
            
            if not clean_message:
                await ctx.send('Please provide a message to send to the AI.')
                return

            # Send a message to the user that we're thinking
            await ctx.send("🤔 Thinking...")

            # Prepare the payload
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": clean_message}
                ],
                "temperature": 0.7
            }

            # Send POST request to LLM
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.llm_url}/chat/completions", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI")
                        
                        logger.info(f'AI response received: {ai_response[:100]}...')
                        await ctx.send(f'🤖 {ai_response}')
                    else:
                        error_text = await response.text()
                        logger.error(f'LLM API error: {response.status} - {error_text}')
                        await ctx.send(f'Error from AI server: {response.status}')

        except aiohttp.ClientError as e:
            logger.error(f'Network error calling LLM: {str(e)}')
            await ctx.send(f'Network error: {str(e)}')
        except Exception as e:
            logger.error(f'Error in chat command: {str(e)}')
            await ctx.send(f'Error: {str(e)}')

    @commands.command(name='models', aliases=['list_models', 'available_models'])
    async def models(self, ctx):
        """Lists all available models from the LLM server"""
        try:
            logger.info(f'Models command invoked by {ctx.author}')

            # Send a message to the user that we're fetching models
            await ctx.send("🔍 Fetching available models...")

            # Send GET request to fetch models
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.llm_url}/models") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        
                        if models:
                            model_list = "\n".join([f"  - {model.get('id', 'Unknown')}" for model in models])
                            await ctx.send(f"🤖 Available models:\n{model_list}")
                        else:
                            await ctx.send("No models found from the AI server.")
                        
                        logger.info(f'Models fetched: {len(models)} models available')
                    else:
                        error_text = await response.text()
                        logger.error(f'Models API error: {response.status} - {error_text}')
                        await ctx.send(f'Error fetching models: {response.status}')

        except aiohttp.ClientError as e:
            logger.error(f'Network error fetching models: {str(e)}')
            await ctx.send(f'Network error: {str(e)}')
        except Exception as e:
            logger.error(f'Error in models command: {str(e)}')
            await ctx.send(f'Error: {str(e)}')

    @commands.command(name='load', aliases=['load_model', 'use_model'])
    async def load(self, ctx, model: str):
        """Loads a model from the LLM server and sets it as the default for chat commands"""
        try:
            logger.info(f'Load command invoked by {ctx.author}: {model}')

            # Send a message to the user that we're loading the model
            await ctx.send(f"📦 Loading model: `{model}`...")

            # Prepare the payload
            payload = {
                "model": model
            }

            # Send POST request to load model
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.llm_url}/models/load", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status", "Loaded")
                        self.current_model = model
                        await ctx.send(f"✅ Model `{model}` loaded successfully! This will be used for future chat commands.")
                        logger.info(f'Model {model} loaded successfully')
                    else:
                        error_text = await response.text()
                        logger.error(f'Load model API error: {response.status} - {error_text}')
                        await ctx.send(f'Error loading model: {response.status}')

        except aiohttp.ClientError as e:
            logger.error(f'Network error loading model: {str(e)}')
            await ctx.send(f'Network error: {str(e)}')
        except Exception as e:
            logger.error(f'Error in load command: {str(e)}')
            await ctx.send(f'Error: {str(e)}')

async def setup(bot):
    """Setup function for the cog - called by the bot"""
    await bot.add_cog(ChatCog(bot))
    logger.info('ChatCog setup complete')
