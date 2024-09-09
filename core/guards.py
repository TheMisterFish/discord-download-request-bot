from discord.ext import commands
from discord.ext.commands import CheckFailure
from core.config import load_config

class UserIgnoredError(CheckFailure):
    pass

class NotAllowedChannelError(CheckFailure):
    pass

def is_not_ignored():
    async def predicate(ctx):
        config = load_config()
        if str(ctx.author.id) in config['ignored_users']:
            raise UserIgnoredError("This user is ignored and cannot use bot commands.")
        return True
    return commands.check(predicate)

def is_moderator():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        
        if ctx.author.guild_permissions.manage_messages and ctx.author.guild_permissions.kick_members:
            return True
        
        raise commands.MissingPermissions(["Moderator"])
    
    return commands.check(predicate)

def in_allowed_channel():
    async def predicate(ctx):
        # TODO: Add config that allows the admin/moderator to always use /download
        # if ctx.author.guild_permissions.administrator:
        #     return True
        
        # if ctx.author.guild_permissions.manage_messages and ctx.author.guild_permissions.kick_members:
        #     return True

        allowed_channels = load_config().get('allowed_channels', {})
        
        if not allowed_channels:
            return True
        
        if not str(ctx.channel.id) in allowed_channels:
            raise NotAllowedChannelError("This user is ignored and cannot use bot commands.")
        return True
    
    return commands.check(predicate)