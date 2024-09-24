import asyncio
import logging
import os
import inspect
from functools import wraps
from logging.handlers import RotatingFileHandler
from discord.ext import commands

class ServerLogger:
    def __init__(self, server_id):
        self.server_id = server_id
        self.logger = self.setup_logger()

    def setup_logger(self):
        log_dir = f'data/{self.server_id}'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger(f'bot_server_{self.server_id}')
        logger.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            f'{log_dir}/bot_commands.log', 
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    def log_command(self, ctx, command_name, params, result):
        user = ctx.author
        guild = ctx.guild
        channel = ctx.channel

        if 'user' in params:
            if params['user'] is not None:
                params['user'] = f"{params['user'].name} (ID: {params['user'].id})"
            else:
                params['user'] = None

        log_message = (
            f"Command: {command_name} | "
            f"Params: {params} | "
            f"User: {user.name} (ID: {user.id}) | "
            f"Guild: {guild.name} (ID: {guild.id}) | "
            f"Channel: {channel.name} | "
            f"Result: {result}"
        )

        self.logger.info(log_message)

# Dictionary to store logger instances for each server
server_loggers = {}

def get_server_logger(server_id):
    if not server_id:
        raise commands.NoPrivateMessage("This command cannot be used in private messages.")
    if server_id not in server_loggers:
        server_loggers[server_id] = ServerLogger(server_id)
    return server_loggers[server_id]

def command_logger(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = next((arg for arg in args if hasattr(arg, 'command')), None)
        if ctx is None:
            return await func(*args, **kwargs)

        server_id = ctx.guild.id
        logger = get_server_logger(server_id)

        command_name = ctx.command.name
        
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        params = dict(bound_args.arguments)
        
        params.pop('self', None)
        params.pop('ctx', None)
        
        try:
            result = await func(*args, **kwargs)

            try:
                await asyncio.sleep(0.1)
                
                if ctx.interaction.response.is_done():
                    response_message = await ctx.interaction.original_response()
                    
                    if response_message.embeds:
                        response_content = f"Embed: {response_message.embeds[0].title}"
                    else:
                        response_content = response_message.content
                else:
                    response_content = "No response sent"

                logger.log_command(ctx, command_name, params, f"Success: {response_content}")
            except Exception as e:
                logger.log_command(ctx, command_name, params, f"Success: Unable to retrieve response content. Error: {str(e)}")
            
            return result
        except Exception as e:
            logger.log_command(ctx, command_name, params, f"Error: {str(e)}")
            raise

    return wrapper