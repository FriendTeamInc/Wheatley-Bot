# General commands for all to use

from discord.ext import commands


class General(commands.Cog):
    """
    General Commands for all to use
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['source'])
    async def about(self, ctx):
        await ctx.send("You can view my source code here:"
            "https://github.com/NotQuiteApex/Wheatley-Bot")


def setup(bot):
    bot.add_cog(General(bot))