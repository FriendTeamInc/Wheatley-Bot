# Bot management commands, for use by staff only

from subprocess import run
from sys import exit
from os.path import isfile

from discord.ext import commands

import toml
import aiofiles as aiof

class System(commands.Cog):
    """
    Bot management commands, for use by staff only
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("BotFriend")
    @commands.command(aliases=["pull"])
    async def botupdate(self, ctx, restarting:bool=False):
        """Pulls git commits."""
        msgtxt = "Pulling new git commits."
        msg = await ctx.send(msgtxt)
        run(["git", "stash"])
        run(["git", "pull"])
        run(["git", "stash", "clear"])
        
        msgtxt += " Changes pulled!"
        if restarting:
            msgtxt += " Restarting now."
        
        await msg.edit(content=msgtxt)
            

    # Bot is meant to run under systemctl to auto-restart it.
    @commands.has_role("BotFriend")
    @commands.command(aliases=["stop","restart"])
    async def botstop(self, ctx, silent:bool=False):
        """Stops the bot."""
        if not silent:
            await ctx.send("Exiting, should restart soon.")
        exit(0)
    
    # Is this safe? probably not lol
    @commands.has_role("BotFriend")
    @commands.command(aliases=["update"])
    async def upgrade(self, ctx):
        """Pulls git commits and stops the bot."""
        await self.botupdate(ctx, True)
        await self.botstop(ctx, True)

    @commands.has_role("BotFriend")
    @commands.command(aliases=["addon"])
    async def addons(self, ctx):
        """Shows the addons that were meant to be loaded."""
        cogsstring = "Cogs:"
        for cog in bot.cogs:
            cogsstring += f"\n- {cog}"
        await ctx.send(cogsstring)
    
    @commands.has_role("BotFriend")
    @commands.command()
    async def dumpconf(self, ctx):
        """Dumps the local (RAM) config to a TOML format."""
        tom = {"roles":{}}

        async with ctx.typing():
            async for roletype in self.bot.userroles:
                roleplural = roletype + "s"
                tom["roles"][roleplural] = {}
                for rolekey, rolename in self.bot.roles[roleplural].items():
                    if role != None:
                        tom["roles"][roleplural][rolekey] = rolename.name
                    else:
                        tom["roles"][roleplural][rolekey] = "error:missing"
            
        await ctx.send(f"```toml\n{toml.dumps(tom)}```")


    @commands.has_role("BotFriend")
    @commands.command()
    async def generatedb(self, ctx):
        """Generates a database file per user in a server."""
        async for user in self.bot.guild.members:
            dbfile = f"db/{user.id}.json"
            userjson = {}

            if isfile(dbfile):
                async with aiof.open(dbfile, "r") as f:
                    filejson = await f.read()
                    tempjson = json.loads(filejson)

                    if isinstance(userjson, list):
                        # convert warn db to new db style
                        userjson = {
                            "member": f"{user.name}#{user.discriminator}, {user.id}",
                            "muted": False,
                            "probated": False,
                            "roles": [],
                            "warns": tempjson
                        }
                    else:
                        continue # db file already exists for this user.
            else:
                userjson = {
                    "member": f"{user.name}#{user.discriminator}, {user.id}",
                    "muted": False,
                    "probated": False,
                    "roles": [],
                    "warns": []
                }

            async with aiof.open(dbfile, "w") as f:
                filejson = json.dumps(userjson)
                await f.write(filejson)


def setup(bot):
    bot.add_cog(System(bot))
    