import discord
from discord.commands import slash_command
from discord.ext import commands

class CreditCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="credits", description="Show credits for the bot")
    async def credits(self, ctx):
        embed = discord.Embed(
            title="Bot Credits",
            description="Information about the creators of this bot",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Creator",
            value="[TheMisterFish](https://github.com/TheMisterFish)",
            inline=False
        )

        embed.add_field(
            name="Special Thanks",
            value="TheOrangeDot for their invaluable help in creating this bot.",
            inline=False
        )

        embed.set_footer(text="Thank you for using our bot!")

        # Send the embed as an ephemeral message (only visible to the command user)
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(CreditCommand(bot))