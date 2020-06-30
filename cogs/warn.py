# Warnings from the mods, for use by staff

from json import load, dump
from time import strftime, localtime

from discord import Member, Embed, Color
from discord.ext import commands

class Warn(commands.Cog):
    """
    Warn commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def dm(self, member: Member, message: str):
        """DM the member and catch an eventual exception."""
        try:
            await member.send(message)
        except:
            pass

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def warn(self, ctx, member: Member, *, reason: str=""):
        """
        Warn a member of rule breaking. (Staff only)
        A ping or member ID can be used for <member>.
        1st warn - Verbal warning, nothing more
        2nd warn - Kicked from server
        3rd warn - Indefinite ban
        """
        author = ctx.message.author

        # Make sure not to allow certain people form being warned.
        if member == author:
            return await ctx.send("You can't warn yourself.")
        elif self.bot.staff_role in member.roles:
            return await ctx.send("You can't warn staff.")
        elif ctx.me is member:
            return await ctx.send("I can't warn myself.")

        memberid = str(member.id)

        warnsno = 0
        warnlist = []

        # Try to search db for any previous warns on file.
        try:
            with open(f"db/{memberid}.json") as f:
                warnlist = load(f)
        except FileNotFoundError:
            pass

        # Add warn
        warnlist.append({
            "warnno": len(warnlist)+1,
            "active": True, # warnings will stay on file even if inactive.
            "member": f"{member.name}#{member.discriminator}, {memberid}",
            "timestamp": strftime("%Y-%m-%d %H:%M:%S", localtime()),
            "reason": reason,
            "author": f"{author.name}"
        })

        # Count active warns.
        for warn in warnlist:
            if warn["active"]:
                warnsno += 1

        # Prep to announce the warn
        msg = f":triangular_flag_on_post:"

        # DM the member about the warn.
        if reason == "":
            await self.dm(member,
                "You have been warned in {}.".format(ctx.guild.name))
        else:
            await self.dm(member,
                "You have been warned in {} for the following reason :\n{}\n"
                "".format(ctx.guild.name, reason))

        # Do what needs to be done based on the active warns.
        if warnsno == 1:
            msg += f" {member.mention}, this is a verbal warning."
            await self.dm(member,
                "This is only a verbal warning, but on your next"
                " warning you will be kicked from the server.")
        elif warnsno == 2:
            msg += f" {member.mention} has been muted."
            await self.dm(member,
                "This is your second warning, so you have been muted."
                " You will be unmuted by staff at their discretion, but you"
                " may contact staff via modmail after 24 hours if left muted.")
        elif warnsno >= 3:
            msg += f" {member.mention} has been banned."
            await self.dm(member,
                "You have been banned indefinitely as a result of the warn."
                " If you would like to appeal this ban, please direct"
                " message this bot after 24 hours to contact staff.")
            
        if reason:
            msg += f"\nWarn reason: {reason}"

        # Announce the warn
        await ctx.send(msg)

        # Time to log
        if reason == "":
            reason = "No reason specified."

        emb = Embed(title="User Warned", color=Color.orange())
        emb.add_field(name="User:", value=member, inline=True)
        emb.add_field(name="Mod:", value=ctx.message.author, inline=True)
        emb.add_field(name="Reason:", value=reason, inline=True)
        emb.add_field(name="Warn#:", value=warnsno, inline=True)
        await self.bot.userlogs_channel.send("", embed=emb)
        
        with open(f"db/{memberid}.json", "w") as f:
            dump(warnlist, f)


    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["deletewarn", "delwarn"])
    async def unwarn(self, ctx, member: Member, num: int=0):
        """
        Remove a warning from a member. (Staff only)
        The warn is not deleted from the file we keep, but is simply made inactive.
        """
        author = ctx.message.author
        if member == author:
            return await ctx.send("You cannot remove a warn from yourself.")
        elif num < 1:
            return await ctx.send("Please properly specify a warn to undo. ( >=1 )")

        memberid = str(member.id)
        warnlist = []
        try:
            with open(f"db/{memberid}.json") as f:
                warnlist = load(f)
        except FileNotFoundError:
            return await ctx.send("This member does not have any warns on file.")

        if len(warnlist) == 0:
            return await ctx.send("This member does not have any warns on file.")

        # Count active warns and find what matches the index.
        warnsno = 0
        warnidx = 0
        for i, warn in enumerate(warnlist):
            if warn["active"]:
                warnsno += 1
                if warnsno == num:
                    warnidx = i
                    break
        else:
            return await ctx.send(f"This member does not have warn #{num}.")

        warnlist[warnidx]["active"] = False
        await ctx.send(f"Warn #{num} removed for member.")

        emb = Embed(title="User Unwarned", color=Color.blue())
        emb.add_field(name="User:", value=member, inline=True)
        emb.add_field(name="Mod:", value=ctx.message.author, inline=True)
        emb.add_field(name="Warning#:", value=num, inline=True)
        await self.bot.userlogs_channel.send("", embed=emb)

        with open(f"db/{memberid}.json", "w") as f:
            dump(warnlist, f)


    @commands.command(aliases=["listwarns"])
    async def listwarn(self, ctx, member: Member=None, postit: bool=False):
        """
        List warnings someone may have.
        """
        if not member:
            member = ctx.message.author

        hasperms = self.bot.staff_role in ctx.message.author.roles

        if not hasperms and member != ctx.message.author:
            return await ctx.send(f"{ctx.message.author.mention} You're not allowed to view other peoples warns.")

        memberid = str(member.id)
        warnlist = []
        try:
            with open(f"db/{memberid}.json") as f:
                warnlist = load(f)
        except FileNotFoundError:
            return await ctx.send(f"Member {member} does not have any warns on file.")

        shortwarns = []
        for warn in warnlist:
            if warn["active"]:
                shortwarns.append(warn)

        if len(shortwarns) < 1:
            return await ctx.send("This member does not have any active warns on file.")

        msg = f":warning: {member}'s warns.\n"
        for i, warn in enumerate(shortwarns, 1):
            msg += f"*{i}.* \"" + warn["reason"] + f"\" on {warn['timestamp']}"
            if hasperms:
                msg += f" from {warn['author']}"
            msg += "\n"
        msg += f"Total warns: {len(warnlist)}"

        if not hasperms:
            await self.dm(member, msg)
            await ctx.send(f"{ctx.message.author.mention} I have DM'd your list of warnings.")
        else:
            if postit:
                await ctx.send(msg)
            else:
                await self.bot.userlogs_channel.send(msg)


def setup(bot):
    bot.add_cog(Warn(bot))