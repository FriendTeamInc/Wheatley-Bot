# Toggleable game roles for the whole family
# Modified from games.py

from discord.ext import commands
from discord.utils import get


class Games(commands.Cog):
    """
    Game commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.games = bot.roles["games"]

    @commands.command(pass_context=True, aliases=['game'])
    async def games(self, ctx, gamestring=""):
        """Choose your gameed role."""
        user = ctx.message.author
        if not gamestring:
            await ctx.send(f"{user.mention} You forgot to choose a game!"
                           f" You can see the full list with `.list{lang.lower()}`")
            return

        gamerole = gamestring.lower()

        if gamerole in self.games:
            gameset = self.games[gamerole]
            if gameset in user.roles:
                await user.remove_roles(gameset)
                await ctx.send(f"{user.mention} game {gameset} removed.")
            else:
                await user.add_roles(gameset)
                await ctx.send(f"{user.mention} game {gameset} added.")
        else:
            await ctx.send(f"{user.mention} `{gamestring}` is not a game we track.")

    @commands.command(pass_context=True, aliases=['listgame'])
    async def listgames(self, ctx):
        """List available games."""
        gamelist = ":game_die: **__game roles:__**\n"
        gamelist += "Example: `.games tf2` gives you the \"Team Fortress 2\" role.\n"
        for gamerole, gamename in enumerate(self.games):
            gamelist += f"- {gamerole} - {gamename}\n"
        await ctx.send(gamelist)


def setup(bot):
    bot.add_cog(Games(bot))
