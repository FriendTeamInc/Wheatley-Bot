# Taken from NutCord's GLaDOS bot

from discord.ext import commands


class Colors(commands.Cog):
    """
    Color commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.colors = {
            "white_role":  self.bot.white_role,
            "turq_role":   self.bot.turq_role,
            "green_role":  self.bot.green_role,
            "sky_role":    self.bot.sky_role,
            "purple_role": self.bot.purple_role,
            "red_role":    self.bot.red_role,
            "orange_role": self.bot.orange_role,
            "yellow_role": self.bot.yellow_role,
            "dark_role":   self.bot.dark_role,
            "pink_role":   self.bot.pink_role,
            "blue_role":   self.bot.blue_role,
        }

    async def change(self, ctx, color, lang, cur_color, user):
        if not cur_color:
            await user.add_roles(color)
            await ctx.send("{} {} {} added."
                           "".format(user.mention, lang, color.name.lower()))
        elif cur_color != color:
            await user.remove_roles(cur_color)
            await user.add_roles(color)
            await ctx.send("{} {} {} removed.\n"
                           "{} {} {} added."
                           "".format(user.mention, lang, cur_color.name.lower(),
                                     user.mention, lang, color.name.lower()))
        else:
            await user.remove_roles(color)
            await ctx.send("{} {} {} removed."
                           "".format(user.mention, lang, color.name.lower()))

    @commands.command(pass_context=True, aliases=['colour'])
    async def color(self, ctx, colorstring=""):
        """Choose your colored role."""
        user = ctx.message.author
        await ctx.message.delete()
        lang = (ctx.invoked_with).capitalize()
        if not colorstring:
            await ctx.send("{} You forgot to choose a {}! You can see the full list with `.list{}`"
                           "".format(user.mention, lang.lower(), lang.lower()))
            return

        colorrole = colorstring.lower() + "_role"

        applied_colors = []
        for color in self.colors:
            if self.colors[color] in user.roles:
                applied_colors.append(self.colors[color])
        if applied_colors:
            cur_color = applied_colors[0]
        else:
            cur_color = None

        if colorrole in self.colors:
            await self.change(ctx, self.colors[colorrole], lang, cur_color, user)
        else:
            await ctx.send("{} `{}` is not a permissible {}."
                           "".format(user.mention, colorstring, lang))

    @commands.command(pass_context=True, aliases=['listcolours', 'listcolor', 'listcolour'])
    async def listcolors(self, ctx):
        """List available colors"""
        colorlist = ""
        for color in self.colors:
            color = color.split("_")[0]
            colorlist += "- " + color + "\n"
        await ctx.send(":art: **__Colored roles:__**\n" + colorlist)


def setup(bot):
    bot.add_cog(Colors(bot))
