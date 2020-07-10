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
        
    async def dm(self, member: Member, message: str):
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
            return await msg.author.send("Nope.")

        if self.bot.muted_role not in user.roles:
            return

        if self.bot.probated_role not in user.roles:
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
                topic = f"{user.name}#{user.discriminator}'s ModMail Appeal thread."
            )

            self.modmaillookup[userthread] = mailthread

        # Create embed of message from user
        emb = Embed(color=Color.blurple())
        emb.author(f"{user.name}#{user.discriminator}-{user.id}")
        emb.add_field(name="msg:", value=msg.content)

        # Post embed to thread.
        await self.modmaillookup[userthread].send("", embed=emb)

    @commands.has_role("Admin")
    @commands.command()
    async def reply(self, ctx, *, msg: str):
        # check if in modmail thread, otherwise complain
        if ctx.channel.name not in self.modmaillookup:
            return await ctx.send("This isn't a modmail thread!")

        # parse message and pass it to the user in question
        user = self.bot.get_user(ctx.channel.name.split("-")[1])

        if user is None:
            return await ctx.send("User not found!")

        user.send(f"Staff: {msg}")


def setup(bot):
    bot.add_cog(ModMail(bot))
