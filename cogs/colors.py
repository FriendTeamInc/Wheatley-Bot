# Taken from NutCord's GLaDOS bot

from discord.ext import commands
from discord.utils import get


class Colors(commands.Cog):
    """
    Color commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.colors = bot.roles["colors"]

    async def change(self, ctx, color, lang, cur_color, user):
        if not cur_color:
            await user.add_roles(color)
            await ctx.send(f"{user.mention} {lang} {color.name} added.")
        elif cur_color != color:
            await user.remove_roles(cur_color)
            await user.add_roles(color)
            await ctx.send(f"{user.mention} {lang} changed from {cur_color.name} to {color.name}.")
        else:
            await user.remove_roles(color)
            await ctx.send(f"{user.mention} {lang} {color.name} removed.")

    @commands.command(pass_context=True, aliases=['colour'])
    async def color(self, ctx, colorstring=""):
        """Choose your colored role."""
        user = ctx.message.author
        lang = (ctx.invoked_with).capitalize()
        if not colorstring:
            await ctx.send(f"{user.mention} You forgot to choose a {lang}!"
                            f"You can see the full list with `.list{lang}`")
            return

        colorrole = colorstring.lower()

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
            await ctx.send(f"{user.mention} `{colorstring}` is not a permissible {lang}.")

    @commands.command(pass_context=True, aliases=['listcolours', 'listcolor', 'listcolour'])
    async def listcolors(self, ctx):
        """List available colors."""
        colorlist = ":art: **__Colored roles:__** `.color yellow` gives you the yellow color for your name.\n"
        for color in self.colors:
            colorlist += f"- {color}\n"
        await ctx.send(colorlist)


def setup(bot):
    bot.add_cog(Colors(bot))
