import discord
from discord.ext import commands
import re
from typing import List, Tuple, Pattern
from core.database import get_server_database

class WatcherCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._watcher_cache: dict[int, List[Tuple[Pattern, str]]] = {}

    def _compile_pattern(self, question: str) -> Pattern:
        """
        Compile a watcher question into a regex pattern.
        '*' becomes '.*', everything else is escaped.
        """
        escaped = re.escape(question)
        pattern_str = escaped.replace(r"\*", ".*")
        if "*" not in question:
            pattern_str = f"^{pattern_str}$"
        return re.compile(pattern_str, re.IGNORECASE)

    def _load_watchers_for_guild(self, guild_id: int):
        db = get_server_database(guild_id)
        watchers = db.get_watchers()
        compiled = []
        for watcher in watchers:
            try:
                regex = self._compile_pattern(watcher["question"])
                compiled.append((regex, watcher["reply"]))
            except re.error as e:
                print(f"[Watcher] Failed to compile pattern '{watcher['question']}': {e}")
        self._watcher_cache[guild_id] = compiled

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id

        if guild_id not in self._watcher_cache:
            self._load_watchers_for_guild(guild_id)

        watchers = self._watcher_cache.get(guild_id, [])
        content = message.content

        for regex, reply in watchers:
            if regex.search(content):
                try:
                    await message.channel.send(reply)
                except discord.Forbidden:
                    print(f"[Watcher] Missing permissions to send message in {message.channel}")
                except Exception as e:
                    print(f"[Watcher] Error sending message: {e}")
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        self._watcher_cache.pop(guild.id, None)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self._watcher_cache.pop(guild.id, None)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        self._watcher_cache.pop(after.id, None)

    @commands.Cog.listener()
    async def on_update_watcher(self, server_id: int):
        self._watcher_cache.pop(server_id, None)
        self._load_watchers_for_guild(server_id)

    def invalidate_cache(self, guild_id: int):
        """Call this when watchers are externally modified to force a reload."""
        self._watcher_cache.pop(guild_id, None)

def setup(bot):
    bot.add_cog(WatcherCommand(bot))