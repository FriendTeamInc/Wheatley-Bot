# Events that the bot calls.

from discord import errors, Embed, Color, DMChannel, TextChannel, Emoji, PartialEmoji
from discord.ext import commands
from discord.utils import get

import json
import aiofiles as aiof
from os.path import isfile

from cogs.system import gen_user_json, write_user_json


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
    async def on_member_join(self, member):
        if self.bot.autoprobate:
            pass

        #await user.add_roles(self.bot.unapproved_role)

        dbfile = f"db/{user.id}.json"

        if isfile(dbfile):
            async with aiof.open(dbfile, "r") as f:
                filejson = await f.read()
                userjson = json.loads(filejson)

                for rolename in userjson["roles"]:
                    role = get(self.bot.guild.roles, name=role)
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

        await self.logembed(member, "Joined", Color.green())

    @commands.Cog.listener()
    async def on_member_remove(self, user):
        userjson = await gen_user_json(self.bot, user)
        await write_user_json(user, userjson)

        await self.logembed(user, "Left", Color.red())

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user): await self.logembed(user, "Banned", Color.dark_red())

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user): await self.logembed(user, "Unbanned", Color.teal())


    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if msg.author.bot:
            return

        if isinstance(msg.channel, DMChannel):
            return # ignore, this is handled in modmail for dm's

        user = msg.author

        if msg.content is None or msg.content == "":
            return

        emb = Embed(title="Message Deleted", color=Color.dark_red())
        emb.add_field(name="Message:", value=msg.content, inline=True)
        emb.add_field(name="User:", value=f"{user.name}#{user.discriminator}\n<{user.id}>")
        emb.set_thumbnail(url=user.avatar_url)
        await self.bot.msglogs_channel.send("", embed=emb)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        if isinstance(before.channel, DMChannel):
            pass # pass a message to modmail about this event

        user = before.author

        emb = Embed(title="Message Edited", color=Color.blue())
        emb.add_field(name="Before:", value=before.content, inline=True)
        emb.add_field(name="After:", value=after.content)
        emb.add_field(name="Channel:", value=before.channel.name, inline=True)
        emb.add_field(name="User:", value=f"{user.name}#{user.discriminator}\n<{user.id}>", inline=True)
        emb.set_thumbnail(url=user.avatar_url)
        await self.bot.msglogs_channel.send("", embed=emb)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = payload.member
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emote = payload.emoji.name

        # Exit early if any of these are true
        if not isinstance(channel, TextChannel): return
        if channel.name != "rules":              return

        if emote == "gotcha": # Let this be changable later
            if self.bot.unapproved_role in user.roles:
                await user.remove_roles(self.bot.unapproved_role)

        await message.clear_reactions()


def setup(bot):
    bot.add_cog(Events(bot))
