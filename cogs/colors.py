# Taken from NutCord's GLaDOS bot

from discord.ext import commands


class Colors(commands.Cog):
    """
    Color commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def change(self, ctx, color, lang, cur_color, user):
        if not cur_color:
            await user.add_roles(color)
            await ctx.send("{} {} {} added."
                           "".format(user.mention, lang, color.name.lower()))
        elif cur_color != color:
            await user.remove_roles(cur_color)
            await user.add_roles(color)
            await ctx.send("{} {} changed from {} to {}.".format(user.mention,
                           lang, cur_color.name.lower(), color.name.lower()))
        else:
            await user.remove_roles(color)
            await ctx.send("{} {} {} removed."
                           "".format(user.mention, lang, color.name.lower()))

    @commands.command(pass_context=True, aliases=['colour'])
    async def color(self, ctx, colorstring=""):
        """Choose your colored role."""
        user = ctx.message.author
        lang = (ctx.invoked_with).capitalize()
        if not colorstring:
            await ctx.send("{} You forgot to choose a {}! You can see the full list with `.list{}`"
                           "".format(user.mention, lang.lower(), lang.lower()))
            return

        colorrole = colorstring.lower()

        applied_colors = []
        for color in self.bot.colors:
            if self.bot.colors[color] in user.roles:
                applied_colors.append(self.bot.colors[color])
        if applied_colors:
            cur_color = applied_colors[0]
        else:
            cur_color = None

        if colorrole in self.bot.colors:
            await self.change(ctx, self.bot.colors[colorrole], lang, cur_color, user)
        else:
            await ctx.send("{} `{}` is not a permissible {}."
                           "".format(user.mention, colorstring, lang))

    @commands.command(pass_context=True, aliases=['listcolours', 'listcolor', 'listcolour'])
    async def listcolors(self, ctx):
        """List available colors."""
        colorlist = ""
        for color in self.bot.colors:
            colorlist += "- " + color + "\n"
        await ctx.send(":art: **__Colored roles:__**\n" + colorlist)


def setup(bot):
    bot.add_cog(Colors(bot))
