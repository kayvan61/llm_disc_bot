import discord
from discord.ext import commands
import logging
import re
import aiohttp
from cogs.tools import tool_router

logger = logging.getLogger(__name__)

class ChatCog(commands.Cog):
    """A cog that handles chat interactions with an OpenAI-compatible LLM"""

    def __init__(self, bot):
        """Initialize the cog with the bot instance"""
        self.bot = bot
        self.llm_url = "http://192.168.1.148:8080/v1"
        self.current_model = "nv-nemotron-30b"
        self.system_prompt = f"You are a helpful assistant " +\
                              "participating in a group chat " +\
                              "with multiple users. " +\
                              "consider the last send message as the request you are answering to."
        self.tools = tool_router.open_ai_tool_list()
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

    async def handle_reply_chain(self, message):
        current_message = message
        reply_chain = [message]
        
        ctx = await self.bot.get_context(message)
        thinking_msg = await ctx.send("🤔 Thinking...")

        # Loop while there is a message reference
        while current_message.reference:
            try:
                # Fetch the full message object being replied to
                # message.channel.fetch_message is the method to get the full object
                referenced_message = await current_message.channel.fetch_message(current_message.reference.message_id)
                reply_chain.append(referenced_message)
                # Move to the next message in the chain
                current_message = referenced_message
            except discord.NotFound:
                # The referenced message might have been deleted
                logger.error(f"Referenced message {current_message.reference.message_id} not found.")
                break
            except discord.Forbidden:
                # Bot might not have permissions to read the channel history
                logger.error("Missing permissions to fetch message history.")
                break
            except discord.HTTPException as e:
                # Other potential API errors
                logger.error(f"HTTPException while fetching message: {e}")
                break

        reply_chain = reply_chain[::-1]
        assert len(reply_chain) > 0, "reply chain was empty. wtf."
        logger.info(f"reply chain found with len: {len(reply_chain)}")

        payload, _ = self.construct_ctx_from_message_list(reply_chain, self.bot)
        logger.info(f"payload for replies: {payload}")
        ai_response = await self.query_model(payload)

        await self._send_ai_response(ctx, thinking_msg, ai_response, message)

    @commands.Cog.listener()
    async def on_message(self, message):
        logger.info("listening in the chat cog")

        if message.author.id == self.bot.user.id:
            return
    
        # Check if the message is a reply
        if message.reference is not None:
            if self.bot.user in message.mentions:
                await self.handle_reply_chain(message)

    
    # ctx, message to edit, what to say, message to reply if any
    async def _send_ai_response(self, ctx, msg, ai_response: str, reply_to=None):
        """Send or edit message with AI response, handling chunking and filtering.
        
        Removes content before reasoning/thinking tags and splits responses over 2000 chars.
        """
        logger.info(f"raw ai reply is: {ai_response}")
        for tag in ["</thinking>", "</reasoning>", "</think>"]:
            if tag in ai_response:
                ai_response = ai_response.split(tag)[-1]
                break
        logger.info(f"ai reply after filtering: {ai_response}")

        # if we have to reply, delete the thinker, and then reply else we edit in place
        if reply_to:
            await msg.delete()

        MAX_MSG_LEN = 1000
        if len(ai_response) <= MAX_MSG_LEN:
            if reply_to:
                await ctx.reply(f'{ai_response}')
            else:
                await msg.edit(content=f'{ai_response}')
        else:
            chunks = []
            lines = ai_response.split('\n')
            current_chunk = ""
            
            for line in lines:
                if len(current_chunk) + len(line) + 1 <= MAX_MSG_LEN:
                    if current_chunk:
                        current_chunk += '\n' + line
                    else:
                        current_chunk = line
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    if len(line) <= MAX_MSG_LEN:
                        current_chunk = line
                    else:
                        words = line.split()
                        current_chunk = ""
                        for word in words:
                            if len(current_chunk) + len(word) + 1 <= MAX_MSG_LEN:
                                if current_chunk:
                                    current_chunk += ' ' + word
                                else:
                                    current_chunk = word
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                current_chunk = word
            if current_chunk:
                chunks.append(current_chunk)
            
            for idx, chunk in enumerate(chunks):
                if idx == 0:
                    if reply_to:
                        context = await self.bot.get_context(reply_to) 
                        new_msg = await context.reply(f'{chunk}')
                    else:
                        new_msg = await msg.edit(content=f'{chunk}')
                else:
                    new_msg = await ctx.reply(chunk)
                ctx = await self.bot.get_context(new_msg)


    def construct_ctx_from_message_list(self, msgs, bot):
        """given a list of messages it returns a json payload of the chat history
           along with a list of the users in the chain"""

        user_names = set()
        history_messages = []
        for msg in msgs:
            if msg.author != bot.user:
                user_names.add(msg.author.name)
            if msg.author == bot.user:
                history_messages.append({"role": "assistant", "content": msg.content})
            else:
                history_messages.append({
                    "role": "user",
                    "content": f"{msg.author.name}: {msg.content}"
                })

        user_list = ", ".join(sorted(user_names))

        payload = {
            "model": self.current_model,
            "messages": [
                {"role": "system", "content": self.system_prompt + f" The current users are {user_list}."},
                *history_messages
            ],
            "temperature": 0.7
        }

        return payload, user_names
           
    async def query_model(self, payload):
        import json
        payload["tools"] = self.tools

        timeout = aiohttp.ClientTimeout(total=600)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.llm_url}/chat/completions", json=payload, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"raw reply packet: {data}")

                    if data["choices"][0]["finish_reason"] == "tool_calls":
                        tool_calls = data["choices"][0]["message"]["tool_calls"]
                        payload["messages"].append(
                                {
                                    "role": "assistant",
                                    "tool_calls": tool_calls,
                                }
                        )
                        for tc in tool_calls:
                            logger.info(f"asked for a tool! Tool name: {tc['function']['name']}")
                            tool_name = tc['function']['name']
                            tool_call_id = tc['id']
                            tool_arguments_str = tc['function']['arguments']
                            tool_arguments_dict = json.loads(tool_arguments_str)
                            tool_result = await tool_router.route_tool(tool_name, **tool_arguments_dict)
                            tool_result_dict = {
                                "results" : [{x:y} for x,y in tool_result],
                            }
                            logger.info(f"tool result: {tool_result_dict}")
                            payload["messages"].append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": json.dumps(tool_result_dict),
                            })
                        
                        ai_response = await self.query_model(payload)
                    else:
                        ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI")
                    
                    logger.info(f'AI response received: {ai_response[:100]}...')
                    
                    return ai_response
                else:
                    error_text = await response.text()
                    logger.error(f'LLM API error: {response.status} - {error_text}')
                    return 'Error from AI server: {response.status}'

    @commands.command(name='get_system_prompt')
    async def get_system_prompt(self, ctx):
        await ctx.send(f"Current system prompt is: {self.system_prompt}")

    @commands.command(name='set_system_prompt')
    async def set_system_prompt(self, ctx, *, message: str):
        self.system_prompt = message

    @commands.command(name='chat_history', aliases=['chat_hist', 'history_chat'])
    async def chat_history(self, ctx, num_messages: int, *, message: str):
        """Responds to the user using the OpenAI-compatible LLM with chat history"""
        try:
            logger.info(f'Chat history command invoked by {ctx.author} in {ctx.guild.name if ctx.guild else "DM"}: {clean_message} (model: {model}, history: {num_messages} messages)')

            if not clean_message:
                await ctx.send('Please provide a message to send to the AI.')
                return

            if num_messages < 1 or num_messages > 200:
                await ctx.send('Please provide a number between 1 and 200 for message history.')
                return

            channel = ctx.channel
            messages = [msg async for msg in channel.history(limit=num_messages+1)]
            messages = messages[::-1]

            thinking_msg = await ctx.send("🤔 Thinking...")
            
            payload, users = self.construct_ctx_from_message_list(messages, ctx.bot)

            logger.info(f"sending chat: {payload}")

            ai_response = await query_model(payload)
            await self._send_ai_response(ctx, thinking_msg, ai_response, ctx.message)

        except aiohttp.ClientError as e:
            logger.error(f'Network error calling LLM: {str(e)}')
            await thinking_msg.edit(content=f'Network error: {str(e)}')
        except Exception as e:
            logger.error(f'Error in chat_history command: {str(e)}')
            await thinking_msg.edit(content=f'Error: {str(e)}')

    @commands.command(name='chat', aliases=['ask', 'ai'])
    async def chat(self, ctx, *, message: str):
        """Responds to the user using the OpenAI-compatible LLM"""
        try:
            model, clean_message = self.extract_model(message)
            logger.info(f'Chat command invoked by {ctx.author} in {ctx.guild.name if ctx.guild else "DM"}: {clean_message} (model: {model})')

            if not clean_message:
                await ctx.send('Please provide a message to send to the AI.')
                return
            
            # if the message has a reply, then add both to the chain.
            msg_handle = ctx.message
            if msg_handle.reference is not None:
                await self.handle_reply_chain(msg_handle)
                return

            # Send a message to the user that we're thinking
            thinking_msg = await ctx.send("🤔 Thinking...")
            payload, _ = self.construct_ctx_from_message_list([ctx.message], self.bot)
            ai_response = await self.query_model(payload)
            await self._send_ai_response(ctx, thinking_msg, ai_response, ctx.message)

        except aiohttp.ClientError as e:
            logger.error(f'Network error calling LLM: {str(e)}')
            await thinking_msg.edit(content=f'Network error: {str(e)}')
        except Exception as e:
            import traceback
            logger.error(f'Error in chat command: {str(e)}')
            logger.error(f'trace: {traceback.format_exc()}')
            await thinking_msg.edit(content=f'Error: {str(e)}')

    @commands.command(name='models', aliases=['list_models', 'available_models'])
    async def models(self, ctx):
        """Lists all available models from the LLM server"""
        try:
            logger.info(f'Models command invoked by {ctx.author}')

            # Send a message to the user that we're fetching models
            msg = await ctx.send("🔍 Fetching available models...")

            # Send GET request to fetch models
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.llm_url}/models") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        
                        if models:
                            model_list = "\n".join([f"  - {model.get('id', 'Unknown')}" for model in models])
                            await msg.edit(content=f"🤖 Available models:\n{model_list}")
                        else:
                            await msg.edit(content="No models found from the AI server.")
                        
                        logger.info(f'Models fetched: {len(models)} models available')
                    else:
                        error_text = await response.text()
                        logger.error(f'Models API error: {response.status} - {error_text}')
                        await msg.edit(content=f'Error fetching models: {response.status}')

        except aiohttp.ClientError as e:
            logger.error(f'Network error fetching models: {str(e)}')
            await msg.edit(content=f'Network error: {str(e)}')
        except Exception as e:
            logger.error(f'Error in models command: {str(e)}')
            await msg.edit(content=f'Error: {str(e)}')

    @commands.command(name='load', aliases=['load_model', 'use_model'])
    async def load(self, ctx, model: str):
        """Loads a model from the LLM server and sets it as the default for chat commands"""
        try:
            logger.info(f'Load command invoked by {ctx.author}: {model}')

            # Send a message to the user that we're loading the model
            msg = await ctx.send(f"📦 Loading model: `{model}`...")

            self.current_model = model
            await msg.edit(content=f"default using model: `{model}` :)")

        except Exception as e:
            logger.error(f'Error in load command: {str(e)}')
            await msg.edit(content=f'Error: {str(e)}')

async def setup(bot):
    """Setup function for the cog - called by the bot"""
    await bot.add_cog(ChatCog(bot))
    logger.info('ChatCog setup complete')
