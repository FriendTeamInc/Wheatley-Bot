# Modified from colors.py

from discord.ext import commands


class Streams(commands.Cog):
    """
    Color commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.streams = {
            "any_role":  self.bot.anystream_role,
            "apex_role":  self.bot.apexstream_role,
            "kigu_role":  self.bot.kigustream_role,
            "juici_role": self.bot.juicistream_role,
            "percy_role": self.bot.percystream_role,
        }

    async def change(self, ctx, stream, lang, cur_stream, user):
        if stream not in cur_stream:
            await user.add_roles(stream)
            await ctx.send("{} {} role {} added."
                           "".format(user.mention, lang, stream.name))
        else:
            await user.remove_roles(stream)
            await ctx.send("{} {} role {} removed."
                           "".format(user.mention, lang, stream.name))

    @commands.command(pass_context=True, aliases=['stream'])
    async def streamer(self, ctx, streamstring=""):
        """Choose your stream notif role."""
        user = ctx.message.author
        lang = (ctx.invoked_with).capitalize()
        if not streamstring:
            await ctx.send("{} You forgot to choose a {}! You can see the full list with `.list{}`"
                           "".format(user.mention, lang.lower(), lang.lower()))
            return

        streamrole = streamstring.lower() + "_role"

        applied_streams = []
        for stream in self.streams:
            if self.streams[stream] in user.roles:
                applied_streams.append(self.streams[stream])

        if streamrole in self.streams:
            await self.change(ctx, self.streams[streamrole], lang, applied_streams, user)
        else:
            await ctx.send("{} `{}` is not a permissible {}."
                           "".format(user.mention, streamstring, lang))

    @commands.command(pass_context=True, aliases=['liststreamers', 'liststreamer', 'liststream'])
    async def liststreams(self, ctx):
        """List available streams to be notified of."""
        streamlist = ""
        for stream in self.streams:
            stream = stream.split("_")[0].title()
            streamlist += "- " + stream + "\n"
        await ctx.send(":tv: **__Streamer Notif roles:__**\n" + streamlist)


def setup(bot):
    bot.add_cog(Streams(bot))
