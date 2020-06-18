# Taken from NutCord's GLaDOS bot

from discord.ext import commands
from discord.utils import get


class pronouns(commands.Cog):
    """
    pronoun commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def change(self, ctx, pronoun, lang, cur_pronoun, user):
        if not cur_pronoun:
            await user.add_roles(pronoun)
            await ctx.send("{} {} {} added."
                           "".format(user.mention, lang, pronoun.name.lower()))
        elif cur_pronoun != pronoun:
            await user.remove_roles(cur_pronoun)
            await user.add_roles(pronoun)
            await ctx.send("{} {} changed from {} to {}.".format(user.mention,
                           lang, cur_pronoun.name.lower(), pronoun.name.lower()))
        else:
            await user.remove_roles(pronoun)
            await ctx.send("{} {} {} removed."
                           "".format(user.mention, lang, pronoun.name.lower()))

    @commands.command(pass_context=True, aliases=['pros'])
    async def pronouns(self, ctx, pronounstring=""):
        """Choose your pronouned role."""
        user = ctx.message.author
        lang = (ctx.invoked_with).capitalize()
        if not pronounstring:
            await ctx.send("{} You forgot to choose a {}! You can see the full list with `.list{}`"
                           "".format(user.mention, lang.lower(), lang.lower()))
            return

        pronounrole = pronounstring.lower()

        applied_pronouns = []
        for pronoun in self.bot.pronouns:
            if self.bot.pronouns[pronoun] in user.roles:
                applied_pronouns.append(self.bot.pronouns[pronoun])
        if applied_pronouns:
            cur_pronoun = applied_pronouns[0]
        else:
            cur_pronoun = None

        if pronounrole in self.bot.pronouns:
            await self.change(ctx, self.bot.pronouns[pronounrole], lang, cur_pronoun, user)
        else:
            await ctx.send("{} `{}` is not a permissible {}."
                           "".format(user.mention, pronounstring, lang))

    @commands.command(pass_context=True, aliases=['listcolours', 'listpronoun', 'listcolour'])
    async def listpronouns(self, ctx):
        """List available pronouns."""
        pronounlist = ""
        for pronoun in self.bot.pronouns:
            pronounlist += "- " + pronoun + "\n"
        await ctx.send(":art: **__pronouned roles:__**\n" + pronounlist)


def setup(bot):
    bot.add_cog(pronouns(bot))
