# Events that the bot calls.

from discord import errors, Embed, Color, DMChannel, TextChannel, Emoji, PartialEmoji
from discord.ext import commands
from discord.utils import get

import json
import aiofiles as aiof
from os.path import isfile


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
    async def on_member_join(self, user):
        if self.bot.autoprobate:
            pass

        await user.add_roles(self.bot.unapproved_role)

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
    async def on_member_remove(self, user): await self.logembed(user, "Left", Color.red())

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user): await self.logembed(user, "Banned", Color.dark_red())

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user): await selflogembed(user, "Unbanned", Color.teal())


    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        if not isinstance(msg.channel, DMChannel):
            return

        # ModMail stuff here!


    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if msg.author.bot:
            return

        if isinstance(msg.channel, DMChannel):
            pass # pass a message to modmail about this event
            return # for now, ignore

        user = msg.author

        if msg.content is None:
            msg.content = "error:missing"

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
        emb.add_field(name="After:", value=after.content, inline=True)
        emb.add_field(name="Channel:", value=before.channel.name)
        emb.add_field(name="User:", value=f"{user.name}#{user.discriminator}\n<{user.id}>", inline=True)
        emb.set_thumbnail(url=user.avatar_url)
        await self.bot.msglogs_channel.send("", embed=emb)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        msg = reaction.message
        channel = msg.channel

        # Exit early if any of these are true
        if isinstance(reaction.emoji, (PartialEmoji, str)): return
        if not isinstance(channel, TextChannel):            return
        if channel.name != "rules":                         return

        if reaction.emoji.name == "gotcha": # Let this be changable later
            if self.bot.unapproved_role not in user.roles:
                await user.remove_roles(self.bot.unapproved_role)

        await reaction.remove(user)

        await self.bot.msglogs_channel.send(f"Reaction detected! (testing stuff rn) {reaction}")



def setup(bot):
    bot.add_cog(Events(bot))
