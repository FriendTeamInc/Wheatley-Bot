# ModMail system 

from discord import Member, Embed, Color, PermissionOverwrite
from discord.ext import commands

class ModMail(commands.Cog):
    """
    ModMail system.
    """

    def __init__(self, bot):
        self.bot = bot
        self.modmaillookup = {} # key: userid (str), value: channel object

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        if not isinstance(msg.channel, DMChannel):
            return

        user = msg.author
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
