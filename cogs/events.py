# Events that the bot calls.

from discord import errors, Embed
from discord.ext import commands
from discord.utils import get

import json
import aiofiles as aiof


class Events(commands.Cog):
    """
    Events, not commands!
    """

    def __init__(self, bot):
        self.bot = bot

    async def logembed(self, user, stat, color):
        emb = Embed(title="Member "+stat, color=color)
        emb.add_field(name="Username:", value=f"{user.name}#{user.discriminator}", inline=True)
        emb.add_field(name="Member ID:", value=user.id, inline=True)
        emb.set_thumbnail(url=user.avatar_url)
        await self.bot.userlogs_channel.send("", embed=emb)


    @commands.Cog.listener()
    async def on_member_join(user):
        if self.bot.autoprobate:
            pass

        dbfile = f"db/{user.id}.json"

        if isfile(dbfile):
            async with aiof.open(dbfile, "r") as f:
                filejson = await f.read()
                userjson = json.loads(filejson)

                for rolename in userjson["roles"]:
                    role = get(guild.roles, name=role)
                    await user.add_roles(role)

                if userjson["muted"]: await user.add_roles(self.bot.muted_role)
                if userjson["probated"]: await user.add_roles(self.bot.probated_role)
        else:
            async with aiof.open(dbfile, "w") as f:
                userjson = {
                    "member": f"{user.name}#{user.discriminator}, {user.id}",
                    "muted": False,
                    "probated": False,
                    "roles": [],
                    "warns": []
                }
                filejson = json.dumps(userjson)
                await f.write(filejson)

        await self.logembed(user, "Joined", Color.green())

    @commands.Cog.listener()
    async def on_member_remove(user): await self.logembed(user, "Left", Color.red())

    @commands.Cog.listener()
    async def on_member_ban(guild, user): await self.logembed(user, "Banned", Color.dark_red())

    @commands.Cog.listener()
    async def on_member_unban(guild, user): await selflogembed(user, "Unbanned", Color.teal())


    @commands.Cog.listener()
    async def on_message_delete(msg):

        if msg.author.bot:
            return

        user = msg.author

        emb = Embed(title="Message Deleted", color=Color.dark_red())
        emb.add_field(name="User:", value=f"<{user.id}> {user.name}#{user.discriminator}")
        emb.add_field(name="Message:", value=msg.content, inline=True)
        emb.set_thumbnail(url=user.avatar_url)
        await self.bot.msglogs_channel.send("", embed=emb)

    @commands.Cog.listener()
    async def on_message_edit(before, after):

        if before.author.bot or before.content == after.content:
            return

        user = before.author

        emb = Embed(title="Message Edited", color=Color.blue())
        emb.add_field(name="User:", value=f"<{user.id}> {user.name}#{user.discriminator}")
        emb.add_field(name="Before:", value=before.content, inline=True)
        emb.add_field(name="After:", value=after.content, inline=True)
        emb.set_thumbnail(url=user.avatar_url)
        await self.bot.msglogs_channel.send("", embed=emb)



def setup(bot):
    bot.add_cog(Events(bot))
