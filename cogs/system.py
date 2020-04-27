# Bot management commands, for use by staff only

from subprocess import run
from sys import exit

from discord.ext import commands

__admin_role__ = None

class System(commands.Cog):
    """
    Bot management commands, for use by staff only
    """

    def __init__(self, bot):
        self.bot = bot
        __admin_role__ = self.bot.admin_role

    @commands.has_role("BotDev")
    @commands.command(aliases=["pull"])
    async def botupdate(self, ctx):
        await ctx.send("Pulling new git commits.")
        run(["git", "stash", "save"])
        run(["git", "pull"])
        run(["git", "stash", "clear"])

        await ctx.send("Changes pulled.")

    @commands.has_role("BotDev")
    @commands.command(aliases=["stop","restart"])
    async def botstop(self, ctx):
        await ctx.send("Exiting, should restart soon.")
        exit(0)


def setup(bot):
    bot.add_cog(System(bot))