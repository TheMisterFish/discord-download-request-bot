import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

from core.config import load_config, save_config
from core.guards import is_admin, is_moderator
from core.logger import command_logger
from core.utils import scan_download_channel, scan_video_channel
from core.database import get_server_database

class ConfigCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    config = SlashCommandGroup("config", "Configure bot settings")

    ########################################
    # Cooldown command
    ########################################

    @config.command(name="cooldown", description="Configure cooldown settings for the /download and /dn command")
    @is_admin()
    @command_logger
    async def config_cooldown(
        self,
        ctx,
        cooldown_limit: Option(int, "Set the cooldown limit", required=True),
        cooldown_timeout: Option(int, "Set the cooldown timeout in seconds", required=True)
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        config['cooldown'] = {
            'limit': cooldown_limit,
            'timeout': cooldown_timeout
        }
        
        save_config(server_id, config)

        self.bot.dispatch('config_update', server_id)
        
        # Update the cooldown for the DownloadCommand
        download_cog = self.bot.get_cog('DownloadCommand')
        if download_cog:
            download_cog.config = config
        
        await ctx.respond(f"Cooldown configuration updated. Limit: {cooldown_limit}, Timeout: {cooldown_timeout} seconds", ephemeral=True)


    ########################################
    # Admin always download
    ########################################

    @config.command(name="admin_download", description="Configure admin download permissions")
    @is_admin()
    async def config_admin_download(
        self,
        ctx,
        allow_admin_download: Option(bool, "Allow admins to always use /download & /dn", required=True)
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        config['admin_always_download'] = allow_admin_download
        
        save_config(server_id, config)
        
        await ctx.respond(f"Admin download permission updated. Admins can {'always' if allow_admin_download else 'not always'} use /download", ephemeral=True)


    ########################################
    # Allowed download channels
    ########################################

    @config.command(name="allowed_download_channels", description="Manage allowed channels to download from")
    @is_moderator()
    @command_logger
    async def config_allowdownload(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        if 'allowed_channels' not in config:
            config['allowed_channels'] = {}

        if action == "add":
            if channel:
                if str(channel.id) not in config['allowed_channels']:
                    config['allowed_channels'][str(channel.id)] = channel.name
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Added **{channel.name}** to allowed channels to download from", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already an allowed channel to download from", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if str(channel.id) in config['allowed_channels']:
                    del config['allowed_channels'][str(channel.id)]
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from allowed channels to download from", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not an allowed channel to download from", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "list":
            if not config['allowed_channels']:
                await ctx.respond("No downloadable channels are currently configured. Meaning /download and /dn can be used in all text channels.", ephemeral=True)
                return

            allowed_channels = [f"• <#{channel_id}> ({channel_name})" for channel_id, channel_name in config['allowed_channels'].items()]
            embed = discord.Embed(title="🆗 Allowed channels to download from:", color=discord.Color.blue())
            embed.description = "\n".join(allowed_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', or 'list'.", ephemeral=True)


    ########################################
    # Ignore user commands (ignoring their commands)
    ########################################

    @config.command(name="ignore", description="Ignore, unignore, or list ignored users")
    @is_moderator()
    @command_logger
    async def config_ignore(
        self, 
        ctx, 
        action: Option(str, "Choose to add, remove, or list ignored users", choices=["add", "remove", "list"]),
        user: Option(discord.Member, "The user to ignore or unignore", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        if 'ignored_users' not in config:
            config['ignored_users'] = {}

        if action == "add":
            if not user:
                await ctx.respond("You must specify a user to ignore.", ephemeral=True)
                return
            if user.guild_permissions.administrator or (user.guild_permissions.manage_messages and user.guild_permissions.kick_members):
                await ctx.respond(f"❌ Cannot ignore an admin. **{user.name}** is an administrator.", ephemeral=True)
                return

            if str(user.id) not in config['ignored_users']:
                config['ignored_users'][str(user.id)] = user.name
                save_config(server_id, config)
                await ctx.respond(f"✅ Now ignoring user: **{user.name}**", ephemeral=True)
            else:
                await ctx.respond(f"Already ignoring user: **{user.name}**", ephemeral=True)

        elif action == "remove":
            if not user:
                await ctx.respond("You must specify a user to unignore.", ephemeral=True)
                return
            if str(user.id) in config['ignored_users']:
                del config['ignored_users'][str(user.id)]
                save_config(server_id, config)
                await ctx.respond(f"✅ User **{user.name}** is no longer ignored.", ephemeral=True)
            else:
                await ctx.respond(f"User **{user.name}** is not currently ignored.", ephemeral=True)

        elif action == "list":
            if not config['ignored_users']:
                await ctx.respond("No users are currently ignored.", ephemeral=True)
                return

            ignored_users = [f"{username} (ID: {user_id})" for user_id, username in config['ignored_users'].items()]
            embed = discord.Embed(title="🤐 Ignored Users", color=discord.Color.blue())
            embed.description = "\n".join(ignored_users)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', or 'list'.")


    ########################################
    # Video channels to scan
    ########################################

    @config.command(name="videochannel", description="Manage video channels")
    @is_moderator()
    @command_logger
    async def config_videochannel(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "scan", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)

        if 'video_channels' not in config:
            config['video_channels'] = {}

        if action == "add":
            if channel:
                if str(channel.id) not in config['video_channels']:
                    config['video_channels'][str(channel.id)] = channel.name
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Added **{channel.name}** to video channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already a video channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if str(channel.id) in config['video_channels']:
                    del config['video_channels'][str(channel.id)]
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from video channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not a video channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "scan":
            if channel:
                await ctx.respond(f"🔍 Scanning video channel **{channel}**", ephemeral=True)
                await scan_video_channel(ctx, channel)
            else:
                await ctx.respond("🔍 Scanning all configured video channels...", ephemeral=True)
                for channel_id, channel_name in config['video_channels'].items():
                    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                    if channel:
                        await scan_video_channel(ctx, channel)
                    else:
                        await ctx.followup.send(f"❌ Could not find channel: **{channel_name}**", ephemeral=True)
                await ctx.followup.send("✅ Scan completed for all configured video channels.", ephemeral=True)

        elif action == "list":
            if 'video_channels' not in config or not config['video_channels']:
                await ctx.respond("No video channels are currently configured.", ephemeral=True)
                return

            video_channels = [f"• <#{channel_id}> ({channel_name})" for channel_id, channel_name in config['video_channels'].items()]
            embed = discord.Embed(title=f"📋 Video Channels", color=discord.Color.blue())
            embed.description = "\n".join(video_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', 'scan', or 'list'.", ephemeral=True)


    ########################################
    # Download channels to scan
    ########################################

    @config.command(name="downloadchannel", description="Manage channels where download links can be found")
    @is_moderator()
    @command_logger
    async def config_downloadchannel(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "scan", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)

        if 'download_channels' not in config:
            config['download_channels'] = {}

        if action == "add":
            if channel:
                if str(channel.id) not in config['download_channels']:
                    config['download_channels'][str(channel.id)] = channel.name
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Added **{channel.name}** to download posts channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already a download posts channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if str(channel.id) in config['download_channels']:
                    del config['download_channels'][str(channel.id)]
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from download posts channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not a download posts channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "scan":
            if channel:
                await ctx.respond(f"🔍 Scanning channel **{channel}**", ephemeral=True)
                await scan_download_channel(ctx, channel)
            else:
                await ctx.respond("🔍 Scanning all configured channels...", ephemeral=True)
                for channel_id, channel_name in config['download_channels'].items():
                    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                    if channel:
                        await scan_download_channel(ctx, channel)
                    else:
                        await ctx.followup.send(f"❌ Could not find channel: **{channel_name}**", ephemeral=True)
                await ctx.followup.send("✅ Scan completed for all configured channels.", ephemeral=True)

        elif action == "list":
            if 'download_channels' not in config or not config['download_channels']:
                await ctx.respond("No channels to get downloads from are currently configured.", ephemeral=True)
                return

            download_channels = [f"• <#{channel_id}> ({channel_name})" for channel_id, channel_name in config['download_channels'].items()]
            embed = discord.Embed(title=f"📋 Download Posts Channels", color=discord.Color.blue())
            embed.description = "\n".join(download_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', 'scan', or 'list'.", ephemeral=True)


    ########################################
    # Update/Reset search regex
    ########################################

    @config.command(name="search_regex", description="Configure the search regex for download messages, default is `DN : (.+)`")
    @is_admin()
    @command_logger
    async def config_search_regex(
        self,
        ctx,
        regex: Option(str, "Set the search regex", required=True)
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        config['search_regex'] = regex
        save_config(server_id, config)

        self.bot.dispatch('config_update', server_id)
        await ctx.respond(f"Search regex updated to: {regex}", ephemeral=True)

    @config.command(name="reset_regex", description="Reset the search regex for download messages to `DN : (.+)`")
    @is_admin()
    @command_logger
    async def config_search_regex(
        self,
        ctx
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        config['search_regex'] = 'DN : (.+)'
        save_config(server_id, config)

        self.bot.dispatch('config_update', server_id)
        await ctx.respond(f"Search regex updated to: {'DN : (.+)'}", ephemeral=True)


    ########################################
    # Watcher management
    ########################################
    @config.command(name="watcher", description="Manage watchers that reply to specific messages")
    @is_moderator()
    @command_logger
    async def config_watcher(
        self,
        ctx,
        action: Option(str, "Choose an action", choices=["add", "remove", "list", "help"]),
        question: Option(str, "Question to watch for (or index number for removal)", required=False),
        reply: Option(str, "Response to send when question is detected", required=False),
        page: Option(int, "Page number to show (for list only)", required=False, default=1)
    ):
        server_id = ctx.guild.id
        db = get_server_database(server_id)

        if action == "help":
            help_text = (
                "**Watcher Help**\n\n"
                "**Add a watcher:**\n"
                "`/config watcher add question:<text> reply:<response>`\n"
                "Use `*wildcard*` in the question to match any message that contains that text.\n\n"
                "**Remove a watcher:**\n"
                "`/config watcher remove`\n"
                "This shows a list of watchers with index numbers.\n"
                "To remove one: `/config watcher remove question:<number>`\n\n"
                "**List watchers:**\n"
                "`/config watcher list`\n"
                "Displays a list of currently configured watchers."
            )
            await ctx.respond(help_text, ephemeral=True)
            return

        if action == "add":
            if not question or not reply:
                await ctx.respond("You must provide a question, an reply.", ephemeral=True)
                return

            success = db.add_watcher(question.strip(), reply.strip())
            
            if success:
                self.bot.dispatch('update_watcher', server_id)
                await ctx.respond(f"✅ Watcher added for: **{question}**", ephemeral=True)
            else:
                await ctx.respond("❌ Failed to add watcher.", ephemeral=True)

        elif action == "remove":
            watchers = db.list_watchers()

            if not watchers:
                await ctx.respond("No watchers configured to remove.", ephemeral=True)
                return

            if not question:
                desc = ""
                for i, w in enumerate(watchers, 1):
                    preview = w['question'] if len(w['question']) <= 50 else w['question'][:47] + "..."
                    desc += f"**{i}.** {preview}\n"
                embed = discord.Embed(title="🗑️ Watchers - Select one to remove", description=desc, color=discord.Color.orange())
                embed.set_footer(text="To remove a watcher, run /config watcher remove question:<number>")
                await ctx.respond(embed=embed, ephemeral=True)
                return

            try:
                index = int(question)
                if 1 <= index <= len(watchers):
                    removed = db.remove_watcher(watchers[index - 1]['id'])
                    if removed:
                        self.bot.dispatch('update_watcher', server_id)
                        await ctx.respond(f"✅ Removed watcher #{index}: **{watchers[index - 1]['question']}**", ephemeral=True)
                    else:
                        await ctx.respond("❌ Failed to remove watcher.", ephemeral=True)
                else:
                    await ctx.respond("Invalid watcher number.", ephemeral=True)
            except ValueError:
                removed = db.remove_watcher_by_question(question.strip())
                if removed:
                    await ctx.respond(f"✅ Removed watcher for question: **{question}**", ephemeral=True)
                else:
                    await ctx.respond("❌ Watcher not found by question.", ephemeral=True)

        elif action == "list":
            watchers = db.list_watchers(page)
            if not watchers:
                await ctx.respond("No watchers configured.", ephemeral=True)
                return

            def truncate(text, length):
                return text if len(text) <= length else text[:length - 3] + "..."

            # Set max display length for each column
            MAX_ID_LEN = 4
            MAX_QUESTION_LEN = 40
            MAX_REPLY_LEN = 40

            # Header row
            header = (
                f"{'ID':<{MAX_ID_LEN}} "
                f"{'Question':<{MAX_QUESTION_LEN}} "
                f"{'Reply':<{MAX_REPLY_LEN}}"
            )
            separator = "-" * len(header)

            # Table rows
            lines = [header, separator]
            for idx, w in enumerate(watchers, 1):
                q = truncate(w['question'], MAX_QUESTION_LEN)
                a = truncate(w['reply'], MAX_REPLY_LEN)
                lines.append(
                    f"{str(idx):<{MAX_ID_LEN}} "
                    f"{q:<{MAX_QUESTION_LEN}} "
                    f"{a:<{MAX_REPLY_LEN}}"
                )

            table = "```\n" + "\n".join(lines) + "\n```"
            await ctx.respond(table, ephemeral=True)


def setup(bot):
    bot.add_cog(ConfigCommand(bot))
