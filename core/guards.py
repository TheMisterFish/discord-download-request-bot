from discord.ext import commands
from discord.ext.commands import CheckFailure

from core.config import load_config

class UserIgnoredError(CheckFailure):
    pass

class NotAllowedChannelError(CheckFailure):
    pass

def is_not_ignored():
    async def predicate(ctx):
        if not ctx.guild or not ctx.guild.id:
            raise commands.NoPrivateMessage("This command cannot be used in private messages.")
        server_id = ctx.guild.id
        config = load_config(server_id)
        if str(ctx.author.id) in config['ignored_users']:
            raise UserIgnoredError("This user is ignored and cannot use bot commands.")
        return True
    return commands.check(predicate)

def is_admin():
    async def predicate(ctx):
        if not ctx.guild or not ctx.guild.id:
            raise commands.NoPrivateMessage("This command cannot be used in private messages.")
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["Administrator"])
        return True
    return commands.check(predicate)

def is_moderator():
    async def predicate(ctx):
        if not ctx.guild or not ctx.guild.id:
            raise commands.NoPrivateMessage("This command cannot be used in private messages.")
        if ctx.author.guild_permissions.administrator:
            return True
        
        if ctx.author.guild_permissions.manage_messages and ctx.author.guild_permissions.kick_members:
            return True
        
        raise commands.MissingPermissions(["Moderator"])
    return commands.check(predicate)

def in_allowed_channel():
    async def predicate(ctx):
        if not ctx.guild or not ctx.guild.id:
            raise commands.NoPrivateMessage("This command cannot be used in private messages.")
        server_id = ctx.guild.id
        config = load_config(server_id)
        admin_always_download = config.get('admin_always_download', False)

        if admin_always_download:
            if ctx.author.guild_permissions.administrator:
                return True
            if ctx.author.guild_permissions.manage_messages and ctx.author.guild_permissions.kick_members:
                return True

        allowed_channels = config.get('allowed_channels', {})
        
        if not allowed_channels:
            return True
        
        if str(ctx.channel.id) not in allowed_channels:
            raise NotAllowedChannelError("This command can only be used in allowed channels.")
        return True
    return commands.check(predicate)