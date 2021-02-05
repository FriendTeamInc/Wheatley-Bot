# Modified from colors.py

from discord import errors
from discord.ext import commands
from discord.utils import get


class Streams(commands.Cog):
    """
    Stream commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.guild
        self.streams = bot.streams
        self.streams_data = bot.streams_data
        self.streams_notif_channel = bot.streams_notif_channel

    async def change(self, ctx, stream, lang, cur_stream, user):
        if stream not in cur_stream:
            await user.add_roles(stream)
            await ctx.send(f"{user.mention} stream role {stream.name} added.")
        else:
            await user.remove_roles(stream)
            await ctx.send(f"{user.mention} stream role {stream.name} removed.")

    @commands.command(aliases=['streamer'])
    async def stream(self, ctx, streamstring=""):
        """Choose your stream notif role."""
        user = ctx.message.author
        lang = (ctx.invoked_with).capitalize()
        if not streamstring:
            await ctx.send(f"{user.mention} You forgot to choose a stream role!"
                           f" You can see the full list with `.list{lang.lower()}`")
            return
            
        streamstring = streamstring.lower()
        
        if streamstring == "all" or streamstring == "any":
            enable = True
            
            # First check for any roles already had
            for stream in self.streams:
                if self.streams[stream] in user.roles:
                    enable = False
                    await user.remove_roles(self.streams[stream])
            
            if enable:
                for stream in self.streams:
                    await user.add_roles(self.streams[stream])
            
            await ctx.send(f"{user.mention} now has all stream notifs"
                            f" {'enabled' if enable else 'disabled'}.")

            return
        
        applied_streams = []
        for stream in self.streams:
            if self.streams[stream] in user.roles:
                applied_streams.append(self.streams[stream])

        if streamstring in self.streams:
            await self.change(ctx, self.streams[streamstring], lang, applied_streams, user)
        else:
            await ctx.send(f"{user.mention} `{streamstring}` is not a permissible {lang}.")

    @commands.command(aliases=['liststreamers', 'liststreamer', 'liststream'])
    async def liststreams(self, ctx):
        """List available streams to be notified of."""
        streamlist = ":tv: **__Streamer Notif roles:__**\n- All\n"
        streamlist += "Example: `.stream Juici` gives you a role to be pinged when Juice goes live.\n"
        for stream in self.streams:
            streamlist += f"- {stream.title()}\n"
        await ctx.send(streamlist)
    
    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=['addstreamer'])
    async def addstream(self, ctx, streamer="", streamstring=""):
        if streamer == "":
            await ctx.send("Usage: `.addstream <streamer> <streamrole>")

        streamer = streamer.lower()
        if len(streamer) < 1 or len(streamstring) < 1:
            if len(streamer) < 1:
                await ctx.send("The streamer's name must be longer!")
            elif len(streamstring) < 1:
                await ctx.send("The stream role name must be longer!")
            return
        
        try:
            await self.guild.create_role(name=streamstring)
            self.streams[streamer] = get(self.guild.roles, name=streamstring)
            await ctx.send(f"Added stream for {streamer} as {streamstring}")
        except errors.Forbidden:
            await ctx.send("I don't have perms to do that!")
        
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def rmstream(self, ctx, streamer=""):
        if streamer == "":
            await ctx.send("Usage: `.rmstream <streamer>")

        streamer = streamer.lower()
        if streamer in self.streams:
            try:
                if self.streams[streamer] != None:
                    await self.streams[streamer].delete()
                await ctx.send(f"Deleted stream `{streamer}`.")
                del self.streams[streamer]
            except errors.Forbidden:
                await ctx.send("I don't have perms to do that!")
        else:
            await ctx.send("That stream doesn't exist!")
    
    @commands.has_any_role("StreamFriend")
    @commands.command()
    async def live(self, ctx, *, msg=""):
        if ctx.author.id in self.streams_data:
            channel = get(ctx.guild.channels, name=self.streams_notif_channel)
            role = get(ctx.guild.roles, name=self.streams_data[ctx.author.id]["role"])
            link = self.streams_data[ctx.author.id]["link"]
            if msg == "":
                channel.send(role.mention + " " + link)
            else:
                channel.send(role.mention + " " + msg + " " + link)


def setup(bot):
    bot.add_cog(Streams(bot))
