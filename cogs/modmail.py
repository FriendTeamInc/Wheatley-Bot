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

        # parse message and pass it to the user in question
        try:
            user = self.bot.get_user(int(ctx.channel.name.split("-")[1]))
        except ValueError:
            return await ctx.send("This isn't a modmail thread!")

        if user is None:
            return await ctx.send("User not found!")

        await self.dm(user, f"Staff: {msg}")


    @commands.has_role("Admin")
    @commands.command()
    async def close(self, ctx, outcome: str, *, reason: str):
        """
        Closes a modmail thread.
        Additional replies will not be sent, and the outcome dealt (unmuted, kicked, etc)
        Outcomes: unmute, unprobate, kick, ban
        """
        if outcome == "unmute":
            pass
        elif outcome == "unprobate":
            pass
        elif outcome == "kick":
            pass
        elif outcome == "ban":
            pass
        else:
            return await ctx.send(f"Consequence {outcome} is not valid!")

        if reason == "":
            return await ctx.send(f"A reason must be provided for the consequence!")


def setup(bot):
    bot.add_cog(ModMail(bot))
