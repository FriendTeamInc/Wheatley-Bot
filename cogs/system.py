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
    async def botupdate(self, ctx, restarting:bool=False):
        """Pulls git commits."""
        msgtxt = "Pulling new git commits."
        msg = await ctx.send(msgtxt)
        run(["git", "stash", "save"])
        run(["git", "pull"])
        run(["git", "stash", "clear"])
        
        msgtxt += " Changes pulled!"
        if restarting:
            msgtxt += " Restarting now."
        
        await msg.edit(content=msgtxt)
            

    # Bot is meant to run under systemctl to auto-restart it.
    @commands.has_role("BotDev")
    @commands.command(aliases=["stop","restart"])
    async def botstop(self, ctx, silent:bool=False):
        """Stops the bot."""
        if not silent:
            await ctx.send("Exiting, should restart soon.")
        exit(0)
    
    # Is this safe? probably not lol
    @commands.has_role("BotDev")
    @commands.command(aliases=["update"])
    async def upgrade(self, ctx):
        """Pulls git commits and stops the bot."""
        await self.botupdate(ctx, True)
        await self.botstop(ctx, True)

    @commands.has_role("BotDev")
    @commands.command(aliases=["addon"])
    async def addons(self, ctx):
        """Shows the addons that were meant to be loaded."""
        cogsstring = "Cogs:\n- " + "\n- ".join(addons)
        await ctx.send(cogsstring)
    
    @commands.has_role("BotDev")
    @commands.command()
    async def dumpconf(self, ctx):
        """Dumps the local (RAM) config to a TOML format."""
        tom = {"roles":{"colors":{},"streams":{}}}
        for color, role in self.bot.colors.items():
            if role != None:
                tom["roles"]["colors"][color] = role.name
            else:
                tom["roles"]["colors"][color] = "error:missing"
        for stream, role in self.bot.streams.items():
            if role != None:
                tom["roles"]["streams"][stream] = role.name
            else:
                tom["roles"]["streams"][stream] = "error:missing"
            
        await ctx.send("```toml\n{}```".format(toml.dumps(tom)))

    @commands.has_role("BotDev")
    @commands.command()
    async def reloadroles(self, ctx):
        """Does nothing yet."""
        pass


def setup(bot):
    bot.add_cog(System(bot))
    