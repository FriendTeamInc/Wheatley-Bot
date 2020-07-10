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
            return await ctx.send("Please mention a user.")
        elif member == ctx.message.author:
            return await ctx.send("You can't ban yourself.")
        elif (self.bot.staff_role in member.roles and
              self.bot.owner_role not in ctx.message.author.roles):
            return await ctx.send("You can't ban another staffer.")
        elif ctx.me is member:
            return await ctx.send("I can't ban myself, mate.")
        else:
            try:
                dm_msg = f"You've been banned from {ctx.guild.name}."
                if reason:
                    dm_msg += f"\nReason: {reason}"
                await self.dm(member, dm_msg)
                await member.ban(delete_message_days=0, reason=reason)
                await ctx.send(f"I've banned {member}.")
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
            await member.ban(delete_message_days=0, reason=reason)
            await ctx.send(f"I've banned ID: {uid}.")
        except errors.Forbidden:
            await self.noperms(ctx)


    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def mute(self, ctx, member: Member=None, *, reason: str=""):
        """Mute a user. (Staff Only)"""
        if not member:
            return await ctx.send("Please mention a user.")
        elif member == ctx.message.author:
            return await ctx.send("You can't mute yourself.")
        elif (self.bot.staff_role in member.roles and
              self.bot.owner_role not in ctx.message.author.roles):
            return await ctx.send("You can't mute another staffer.")
        elif ctx.me is member:
            return await ctx.send("I can't mute myself, mate.")

        await member.add_roles(self.bot.muted_role)

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unmute(self, ctx, member: Member=None, *, reason: str=""):
        """Mute a user. (Staff Only)"""
        if not member:
            return await ctx.send("Please mention a user.")
        elif self.bot.muted_role not in member.roles:
            return await ctx.send("This user is not muted.")

        await member.remove_roles(self.bot.muted_role)
        await ctx.send(f"User {member} has been muted.")


    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def probate(self, ctx, member: Member=None, *, reason: str=""):
        """Probate a user. (Staff Only)"""
        if not member:
            return await ctx.send("Please mention a user.")
        elif member == ctx.message.author:
            return await ctx.send("You can't probate yourself.")
        elif (self.bot.staff_role in member.roles and
              self.bot.owner_role not in ctx.message.author.roles):
            return await ctx.send("You can't probate another staffer.")
        elif ctx.me is member:
            return await ctx.send("I can't probate myself, mate.")

        await member.add_roles(self.bot.probated_role)
        await ctx.send(f"User {member} has been put on probation.")


    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def approve(self, ctx, member: Member=None, *, reason: str=""):
        """Approves a user, to un-probate them. (Staff Only)"""
        if not member:
            return await ctx.send("Please mention a user.")
        elif member == ctx.message.author:
            return await ctx.send("You can't approve yourself.")
        elif ctx.me is member:
            return await ctx.send("I can't approve myself, mate.")
        elif self.bot.unapproved_role in member.roles:
            await member.remove_roles(self.bot.unapproved_role)
            return await ctx.send(f"User {member} is approved.")
        elif self.bot.probated_role in member.roles:
            await member.remove_roles(self.bot.probated_role)
            return await ctx.send(f"User {member} is unprobated.")
        else:
            return await ctx.send(f"Nothing to do for {member}")


    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def lockdown(self, ctx, *, reason=""):
        """Lock down a channel. (Staff Only)"""
        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        if reason == "":
            await channel.send(":lock: Channel locked.")
        else:
            await channel.send(f":lock: Channel locked. Reason: {reason}")

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def unlock(self, ctx):
        """Unlock a channel. (Staff Only)"""
        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await channel.send(":unlock: Channel Unlocked")


def setup(bot):
    bot.add_cog(Moderation(bot))
