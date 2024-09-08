import logging
from logging.handlers import RotatingFileHandler
import os
from functools import wraps
import inspect

def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('bot')
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        'logs/bot_commands.log', 
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

def log_command(ctx, command_name, params, result):
    user = ctx.author
    guild = ctx.guild
    channel = ctx.channel
    
    log_message = f"Command: {command_name} | Params: {params} | User: {user} (ID: {user.id}) | " \
                  f"Guild: {guild.name} (ID: {guild.id}) | " \
                  f"Channel: {channel.name} (ID: {channel.id}) | " \
                  f"Result: {result}"
    
    logger.info(log_message)

def command_logger(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = next((arg for arg in args if hasattr(arg, 'command')), None)
        if ctx is None:
            return await func(*args, **kwargs)

        command_name = ctx.command.name
        
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        params = dict(bound_args.arguments)
        
        params.pop('self', None)
        params.pop('ctx', None)
        
        try:
            result = await func(*args, **kwargs)
            log_command(ctx, command_name, params, "Command executed successfully")
            return result
        except Exception as e:
            log_command(ctx, command_name, params, f"Error: {str(e)}")
            raise

    return wrapper