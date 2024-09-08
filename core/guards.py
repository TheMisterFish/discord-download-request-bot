from discord.ext import commands
from discord.ext.commands import CheckFailure
from core.config import load_config

class UserIgnoredError(CheckFailure):
    pass

def is_not_ignored():
    async def predicate(ctx):
        config = load_config()
        if str(ctx.author.id) in config['ignored_users']:
            raise UserIgnoredError("This user is ignored and cannot use bot commands.")
        return True
    return commands.check(predicate)

def is_admin():
    async def predicate(ctx):
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["Administrator"])
        return True
    return commands.check(predicate)