# Bot management commands, for use by staff only

from subprocess import run
from sys import exit

from discord.ext import commands

import toml

class System(commands.Cog):
    """
    Bot management commands, for use by staff only
    """

    def __init__(self, bot):
        self.bot = bot

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
    
    # Is this safe? probably not lol
    @commands.has_role("BotDev")
    @commands.command(aliases=["update"])
    async def upgrade(self, ctx):
        await self.botupdate(ctx)
        await self.botstop(ctx)
    
    @commands.has_role("BotDev")
    @commands.command()
    async def dumpconf(self, ctx):
        await ctx.send("```toml\n{}\n{}\n```".format(toml.dumps(self.bot.colors), toml.dumps(self.bot.streams)))


def setup(bot):
    bot.add_cog(System(bot))