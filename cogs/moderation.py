# Moderation functions for staff, because using Discord's UI can be slow.

from discord import Member, Embed, Colour, errors, Object
from discord.ext import commands


class Moderation(commands.Cog):
    """
    Moderation commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def dm(self, member, message):
        """DM the user and catch an eventual exception."""
        try:
            await member.send(message)
        except:
            pass

    async def noperms(self, ctx):
        """No perms!"""
        await ctx.send(":anger: I dont have permission to do this.")


    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=['dropkick','punt'])
    async def kick(self, ctx, member: Member=None, *, reason: str=""):
        """Kick a member. (Staff Only)"""
        try:
            if not member:
                await ctx.send("Please mention a user.")
                return
            elif member is ctx.message.author:
                await ctx.send("You cannot kick yourself!")
                return
            elif (self.bot.staff_role in member.roles and
                  self.bot.owner_role not in ctx.message.author.roles):
                await ctx.send("You may not kick another staffer")
                return
            elif ctx.me is member:
                await ctx.send("Kick me yourself!")
                return

            dm_msg = ""
            if reason == "":
                dm_msg = "You have been kicked from {}.".format(ctx.guild.name)
            else:
                dm_msg = ("You have been kicked from {} for the following reason:\n{}"
                          "".format(ctx.guild.name, reason))
            await self.dm(member, dm_msg)
            await member.kick()
            await ctx.send("I've kicked {}.".format(member))
        except errors.Forbidden:
            await self.noperms(ctx)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: Member=None, *, reason: str=""):
        """Ban a member. (Staff Only)"""
        if not member:
            await ctx.send("Please mention a user.")
            return
        if member == ctx.message.author:
            await ctx.send("You cannot ban yourself!")
            return
        elif (self.bot.staff_role in member.roles and
              self.bot.owner_role not in ctx.message.author.roles):
            await ctx.send("You may not ban another staffer")
            return
        elif ctx.me is member:
            await ctx.send("I am unable to ban myself to prevent stupid mistakes.\n"
                           "Please ban me by hand!")
            return
        else:
            try:
                dm_msg = ""
                if not reason:
                    dm_msg = "You have been banned from {}.".format(
                        ctx.guild.name)
                else:
                    dm_msg = ("You have been banned from {} for the following reason:\n{}"
                              "".format(ctx.guild.name, reason))
                await self.dm(member, dm_msg)
                await member.ban(delete_message_days=0)
                await ctx.send("I've banned {}.".format(member))
            except errors.Forbidden:
                await self.noperms(ctx)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def banid(self, ctx, uid="", *, reason=""):
        """Ban a member by user id. (Staff Only)"""
        try:
            member = Object(uid)
        except IndexError:
            await ctx.send("Please mention a user.")
            return

        try:
            await ctx.guild.ban(member)
            await ctx.send("I've banned ID: {}.".format(uid))
        except errors.Forbidden:
            await self.noperms(ctx)

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def lockdown(self, ctx, *, reason=""):
        """Lock down a channel."""
        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        if reason == "":
            await channel.send(":lock: Channel locked.")
        else:
            await channel.send(":lock: Channel locked. The given reason is: {}".format(reason))

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def unlock(self, ctx):
        """Unlock a channel."""
        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await channel.send(":unlock: Channel Unlocked")


def setup(bot):
    bot.add_cog(Moderation(bot))
