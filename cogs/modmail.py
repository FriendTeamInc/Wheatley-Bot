# ModMail system 

from discord import Member, Embed, Color, DMChannel, TextChannel, PermissionOverwrite
from discord.ext import commands

class ModMail(commands.Cog):
    """
    ModMail system.
    """

    def __init__(self, bot):
        self.bot = bot
        self.modmaillookup = {} # key: userid (str), value: channel object

    async def dm(self, member, message: str):
        """DM the member and catch an eventual exception."""
        try:
            await member.send(message)
        except:
            pass

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        user = self.bot.guild.get_member(msg.author.id)

        if user is None:
            return

        if self.bot.muted_role in user.roles or self.bot.probated_role in user.roles:
            pass
        else:
            return

        if not isinstance(msg.channel, DMChannel):
            return

        userthread = f"user-{user.id}"

        # Create "thread" channel for each mod mail if it doesnt exist.
        if userthread not in self.modmaillookup:
            overwrites = {self.bot.guild.default_role: PermissionOverwrite(read_messages=False)}
            mailthread = await self.bot.guild.create_text_channel(
                userthread,
                overwrites = overwrites,
                category = self.bot.modmail_category,
                topic = f"{user.name}#{user.discriminator}'s ModMail appeal thread."
            )

            self.modmaillookup[userthread] = mailthread

        # Create embed of message from user
        emb = Embed(color=Color.blurple())
        emb.set_author(name=f"{user.name}#{user.discriminator}-{user.id}", icon_url=user.avatar_url)
        emb.add_field(name="msg:", value=msg.content)

        # Post embed to thread.
        await self.modmaillookup[userthread].send("", embed=emb)


    @commands.has_role("Admin")
    @commands.command()
    async def reply(self, ctx, *, msg: str):
        """Reply to a modmail thread (send a message to the appealer)."""
        # check if in modmail thread, otherwise complain
        if ctx.channel.name not in self.modmaillookup:
            return await ctx.send("This isn't a modmail thread!")

        # Grab the user by their id, which is in the channel title
        try:
            user = self.bot.get_user(int(ctx.channel.name.split("-")[1]))
        except ValueError:
            return await ctx.send("This isn't a modmail thread!")

        if user is None:
            return await ctx.send("User not found!")

        await self.dm(user, f"Staff: {msg}")


    @commands.has_role("Admin")
    @commands.command()
    async def close(self, ctx, outcome: str="", *, reason: str=""):
        """
        Closes a modmail thread.
        Additional replies will not be sent, and the outcome dealt (unmuted, kicked, etc)
        Outcomes: unmute, unprobate, kick, ban
        """

        # check if in modmail thread, otherwise complain
        if ctx.channel.name not in self.modmaillookup:
            return await ctx.send("This isn't a modmail thread!")

        # Grab the user by their id, which is in the channel title
        try:
            user = self.bot.guild.get_member(int(ctx.channel.name.split("-")[1]))
        except ValueError:
            return await ctx.send("This isn't a modmail thread!")

        if user is None:
            return await ctx.send("User not found!")

        # A reason to close is required!
        if reason == "":
            return await ctx.send(f"A reason must be provided for the consequence!")

        if outcome == "unmute":
            await user.remove_roles(self.bot.muted_role)
            await self.dm(user, f"You have been unmuted in {self.bot.guild.name}. Understand that next time you may be put on probation.")
            emb = Embed(title="User Unmuted (MM)", color=Color.greyple())
            emb.add_field(name="Username:", value=f"{user.name}#{user.discriminator}", inline=True)
            emb.add_field(name="Member ID:", value=user.id, inline=True)
            emb.add_field(name="Reason:", value=reason, inline=True)
            emb.set_thumbnail(url=user.avatar_url)
            await self.bot.userlogs_channel.send("", embed=emb)
        elif outcome == "unprobate":
            await user.remove_roles(self.bot.probated_role)
            await self.dm(user, f"You have been unprobated in {self.bot.guild.name}. Understand that next time you may be banned outright.")
            emb = Embed(title="User Unprobated (MM)", color=Color.darker_grey())
            emb.add_field(name="Username:", value=f"{user.name}#{user.discriminator}", inline=True)
            emb.add_field(name="Member ID:", value=user.id, inline=True)
            emb.add_field(name="Reason:", value=reason, inline=True)
            emb.set_thumbnail(url=user.avatar_url)
            await self.bot.userlogs_channel.send("", embed=emb)
        elif outcome == "kick":
            await self.dm(user, f"You have been kicked from {self.bot.guild.name}.")
            await user.kick(reason="(MM) - "+reason)
        elif outcome == "ban":
            await self.dm(user, f"You have been banned from {self.bot.guild.name}.")
            await user.ban(delete_message_days=0, reason="(MM) - "+reason)
        else:
            return await ctx.send(f"Consequence \"{outcome}\" is not valid!")

        await ctx.channel.delete(reason=f"Closed - {outcome}'d - {reason}")


def setup(bot):
    bot.add_cog(ModMail(bot))
