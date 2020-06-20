# Taken from NutCord's GLaDOS bot

from discord.ext import commands
from discord.utils import get


class Pronouns(commands.Cog):
    """
    Pronoun commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['pros'])
    async def pronouns(self, ctx, pronounstring=""):
        """Choose your pronouned role."""
        user = ctx.message.author
        lang = ctx.invoked_with
        if not pronounstring:
            await ctx.send("{} You forgot to choose a pronoun set! You can see"
                           " the full list with `.list{}`".format(user.mention,
                            lang.lower(), lang.lower()))
            return

        pronounrole = pronounstring.lower()

        if pronounrole in self.bot.pronouns:
            pronounset = self.bot.pronouns[pronounrole]
            if pronounset in user.roles:
                await user.remove_roles(pronounset)
                await ctx.send("{} pronoun set {} removed."
                               "".format(user.mention, lang, pronounset))
            else:
                await user.add_roles(pronounset)
                await ctx.send("{} pronoun set {} added."
                               "".format(user.mention, lang, pronounset))
        else:
            await ctx.send("{} `{}` is not an allowed pronoun set."
                           "".format(user.mention, pronounstring))

    @commands.command(pass_context=True, aliases=['listpros'])
    async def listpronouns(self, ctx):
        """List available pronouns."""
        pronounlist = ""
        for pronoun in self.bot.pronouns:
            pronounlist += "- " + pronoun + "\n"
        await ctx.send(":crown: **__pronoun roles:__**\n" + pronounlist)


def setup(bot):
    bot.add_cog(Pronouns(bot))
