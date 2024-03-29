# Bot management commands, for use by staff only

from subprocess import run
from sys import exit
from os.path import isfile

from discord.ext import commands

import json
import toml
import aiofiles as aiof


async def gen_user_json(bot, user):
    userjson = {
        "member": f"{user.name}#{user.discriminator}, {user.id}",
        "muted": False,
        "probated": False,
        "roles": [],
        "warns": []
    }

    for role in user.roles:
        userjson["roles"].append(role.name)

    if bot.muted_role in user.roles:
        userjson["muted"] = True

    if bot.probated_role in user.roles:
        userjson["probated"] = True

    return userjson

async def open_user_json(bot, user):
    userjson = await gen_user_json(bot, user)

    try:
        async with aiof.open(f"db/{user.id}.json") as f:
            userfile = await f.read()
            userjson = json.loads(userfile)
    except FileNotFoundError:
        pass

    return userjson

async def write_user_json(user, userjson):
    async with aiof.open(f"db/{user.id}.json", "w") as f:
        await f.write(json.dumps(userjson))


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
        async with ctx.typing():
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
        cogsstring = ":gear: Cogs:"
        for cog in self.bot.cogs:
            cogsstring += f"\n- {cog}"
        await ctx.send(cogsstring)

    @commands.has_role("BotFriend")
    @commands.command(aliases=["reloadaddon"])
    async def reload(self, ctx, cog: str=""):
        """Reloads a cog."""

        addonfail = False
        emb = None
        def cog_reload(addon):
            try:
                self.bot.reload_extension(f"cogs.{addon}")
                print(f"{addon} cog reloaded.")
            except Exception as e:
                if not addonfail:
                    emb = Embed(title="Reload", description="Failed to reload Cog", color=Color.dark_blue())
                addonfail = True
                emb.add_field(name=addon, value=f"{type(e).__name__} : {e}", inline=True)
                print(f"Failed to reload {addon} :\n{type(e).__name__} : {e}")

        if cog == "all" or cog == "":
            for addon in self.bot.addons:
                cog_reload(addon)
        elif cog in self.bot.addons:
            cog_reload(cog)
        else:
            return await ctx.send(f"Cog {cog} not a valid addon!")

        if addonfail:
            try:
                await bot.botlogs_channel.send("", embed=emb)
            except errors.Forbidden:
                pass

        await ctx.send("Reload complete.")
    
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
        async with ctx.typing():
            for user in self.bot.guild.members:
                userjson = await gen_user_json(self, user)

                dbfile = f"db/{user.id}.json"

                if isfile(dbfile):
                    async with aiof.open(dbfile, "r") as f:
                        filejson = await f.read()
                        print(dbfile, filejson)
                        tempjson = json.loads(filejson)

                        if isinstance(userjson, list):
                            # convert warn db to new db style
                            userjson["warns"] = tempjson

                async with aiof.open(dbfile, "w") as f:
                    filejson = json.dumps(userjson)
                    await f.write(filejson)
        await ctx.send("Done!")


def setup(bot):
    bot.add_cog(System(bot))
    