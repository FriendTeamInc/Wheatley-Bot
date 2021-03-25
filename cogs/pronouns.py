# Modified from colors.py

from discord.ext import commands
from discord.utils import get


class Pronouns(commands.Cog):
    """
    Pronoun commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.pronouns = bot.roles["pronouns"]

    @commands.command(pass_context=True, aliases=['pros'])
    async def pronouns(self, ctx, pronounstring=""):
        """Choose your pronouned role."""
        user = ctx.message.author
        if not pronounstring:
            await ctx.send(f"{user.mention} You forgot to choose a pronoun set!"
                           f" You can see the full list with `.list{lang.lower()}`")
            return

        pronounrole = pronounstring.lower()

        if pronounrole in self.pronouns:
            pronounset = self.pronouns[pronounrole]
            if pronounset in user.roles:
                await user.remove_roles(pronounset)
                await ctx.send(f"{user.mention} pronoun set {pronounset} removed.")
            else:
                await user.add_roles(pronounset)
                await ctx.send(f"{user.mention} pronoun set {pronounset} added.")
        else:
            await ctx.send(f"{user.mention} `{pronounstring}` is not an allowed pronoun set.")

    @commands.command(pass_context=True, aliases=['listpros'])
    async def listpronouns(self, ctx):
        """List available pronouns."""
        pronounlist = ":crown: **__pronoun roles:__** "
        pronounlist += "Example: `.pronouns they/them` gives you nonbinary pronouns.\n"
        for pronoun in self.pronouns:
            pronounlist += f"- {pronoun}\n"
        await ctx.send(pronounlist)


def setup(bot):
    bot.add_cog(Pronouns(bot))
