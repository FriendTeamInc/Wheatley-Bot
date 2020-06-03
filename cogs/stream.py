# Modified from colors.py

from discord.ext import commands


class Streams(commands.Cog):
    """
    Color commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.guild
        self.streams = bot.streams

    async def change(self, ctx, stream, lang, cur_stream, user):
        if stream not in cur_stream:
            await user.add_roles(stream)
            await ctx.send("{} {} role {} added."
                           "".format(user.mention, lang, stream.name))
        else:
            await user.remove_roles(stream)
            await ctx.send("{} {} role {} removed."
                           "".format(user.mention, lang, stream.name))

    @commands.command(aliases=['stream'])
    async def streamer(self, ctx, streamstring=""):
        """Choose your stream notif role."""
        user = ctx.message.author
        lang = (ctx.invoked_with).capitalize()
        if not streamstring:
            await ctx.send("{} You forgot to choose a {}! You can see the full list with `.list{}`"
                           "".format(user.mention, lang.lower(), lang.lower()))
            return
            
        streamstring = streamstring.lower()
        
        if streamstring == "all" or streamstring == "any":
            toggle = "enabled"
            
            # First check for any roles already had
            for stream in self.streams:
                if self.streams[stream] in user.roles:
                    toggle = "disabled"
                    await user.remove_roles(self.streams[stream])
            
            if toggle is "enabled":
                for stream in self.streams:
                    await user.add_roles(self.streams[stream])
            
            await ctx.send("{} now has all stream notifs {}."
                           "".format(user.mention, toggle))
            return
        
        applied_streams = []
        for stream in self.streams:
            if self.streams[stream] in user.roles:
                applied_streams.append(self.streams[stream])

        if streamstring in self.streams:
            await self.change(ctx, self.streams[streamstring], lang, applied_streams, user)
        else:
            await ctx.send("{} `{}` is not a permissible {}."
                           "".format(user.mention, streamstring, lang))

    @commands.command(aliases=['liststreamers', 'liststreamer', 'liststream'])
    async def liststreams(self, ctx):
        """List available streams to be notified of."""
        streamlist = ""
        for stream in self.streams:
            stream = stream.split("_")[0].title()
            streamlist += "- " + stream + "\n"
        streamlist = "- All\n" + streamlist
        await ctx.send(":tv: **__Streamer Notif roles:__**\n" + streamlist)
    
    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=['addstreamer'])
    async def addstream(self, ctx, streamer="", streamstring=""):
        streamer = streamer.lower()
        try:
            await self.guild.create_role(name=streamstring)
            self.streams[streamer] = get(self.guild.roles, name=streamstring)
            await ctx.send("Added stream for {} as {}".format(streamer, streamstring))
        except discord.Forbidden:
            await ctx.send("I don't have perms to do that!")
        
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def rmstream(self, ctx, streamer=""):
        streamer = streamer.lower()
        if streamer in self.streams:
            try:
                await self.streams[streamer].delete()
                del self.streams[streamer]
            except discord.Forbidden:
                await ctx.send("I don't have perms to do that!")
        else:
            await ctx.send("That stream doesn't exist!")


def setup(bot):
    bot.add_cog(Streams(bot))
