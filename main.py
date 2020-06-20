#!/usr/bin/env python3.8

from sys import exit
from os import getenv
from traceback import format_exception
from asyncio import sleep

from discord import errors, Embed, Color
from discord.ext import commands
from discord.utils import get

import toml


bot = commands.Bot(command_prefix='.')
try:
    conf = toml.load("conf.toml")
except FileNotFoundError:
    exit("Config not found!")


@bot.event
async def on_ready():
    bot.conf = conf

    missingroleskey = False
    roleerr = {
        "color": {"role":[],"key":[]},
        "stream": {"role":[],"key":[]},
        "pronoun": {"role":[],"key":[]}
    }
    hasroleerr = False

    hascolorroles = False
    hasstreamroles = False
    haspronounroles = False
    
    for guild in bot.guilds:
        # This bot is only meant to manage one server.
        # Do not invite your bot to more than one server.
        bot.guild = guild

        # Friends
        # Will be changed later to different roles to make it more server-agnostic
        bot.admin_role  = get(guild.roles, name="Admin")
        bot.friend_role = get(guild.roles, name="Friend")
        bot.staff_role  = get(guild.roles, name="Admin")
        bot.owner_role  = get(guild.roles, name="Admin")

        # Dev channels
        bot.botdev_channel   = get(guild.channels, name="bot-dev")
        bot.logs_channel     = get(guild.channels, name="bot-logs")
        bot.userlogs_channel = get(guild.channels, name="user-logs")

        if conf["roles"] == None:
            missingroleskey = True
            break

        # Color roles
        if conf["roles"]["colors"] != None:
            hascolorroles = True
            bot.colors = {}
            colors = conf["roles"]["colors"]
            for color, role in colors.items():
                bot.colors[color.lower()] = get(guild.roles, name=role)
                if bot.colors[color.lower()] is None:
                    roleerr["color"]["key"].append(color)
                    roleerr["color"]["role"].append(role)
                    hasroleerr = True

        # Stream roles
        if conf["roles"]["streams"] != None:
            hasstreamroles = True
            bot.streams = {}
            streams = conf["roles"]["streams"]
            for stream, role in streams.items():
                bot.streams[stream.lower()] = get(guild.roles, name=role)
                if bot.streams[stream.lower()] is None:
                    roleerr["stream"]["key"].append(stream)
                    roleerr["stream"]["role"].append(role)
                    hasroleerr = True

        # Pronoun roles
        if conf["roles"]["pronouns"] != None:
            haspronounroles = True
            bot.pronouns = {}
            pronouns = conf["roles"]["pronouns"]
            for pronoun, role in pronouns.items():
                bot.pronouns[pronoun.lower()] = get(guild.roles, name=role)
                if bot.pronouns[pronoun.lower()] is None:
                    roleerr["pronoun"]["key"].append(pronoun)
                    roleerr["pronoun"]["role"].append(role)
                    hasroleerr = True

    await bot.logs_channel.send("Coming back online.")

    # Load addons
    bot.addons = [
        "moderation",
        "system",
    ]

    if hascolorroles: bot.addons.append("colors")
    if hasstreamroles: bot.addons.append("stream")
    if haspronounroles: bot.addons.append("pronouns")

    # Notify if an addon fails to load.
    addonfail = False
    for addon in bot.addons:
        try:
            bot.load_extension("cogs." + addon)
            print("{} cog loaded.".format(addon))
        except Exception as e:
            if not addonfail:
                emb = Embed(title="Startup", description="Failed to load Cog", color=Color.blue())
            addonfail = True
            emb.add_field(name=addon, value=f"{type(e).__name__} : {e}", inline=True)
            print(f"Failed to load {addon} :\n{type(e).__name__} : {e}")
    if addonfail:
        try:
            logchannel = bot.logs_channel
            await logchannel.send("", embed=emb)
        except errors.Forbidden:
            pass

    # Notify if any roles are missing from the server's role manager.
    if hasroleerr:
        for roletype, v in roleerr.items():
            if len(v["key"]) == 0:
                continue # Skip empty roleerr partitions!
            emb = Embed(title=f"Missing `{roletype}` roles", color=Color.orange())
            emb.add_field(name="Key", value="\n".join(v["key"]), inline=True)
            emb.add_field(name="Role", value="\n".join(v["role"]), inline=True)
            await bot.logs_channel.send("", embed=emb)
        #await bot.logs_channel.send("Patch these roles in your `conf.toml` or the roles manager dingus!")

    # We're in.
    print(f"Client logged in as {bot.user.name}, in the following guild : {bot.guild.name}")
    #await bot.botdev_channel.send("Back online!")


@bot.event
async def on_member_join(user):
    await user.add_roles(bot.friend_role)

    emb = Embed(title="Member Joined", colour=Colour.green())
    emb.add_field(name="Member:", value=user.name, inline=True)
    emb.set_thumbnail(url=user.avatar_url)
    await bot.userlogs_channel.send("", embed=emb)


@bot.event
async def on_member_remove(user):
    emb = Embed(title="Member Left", colour=Colour.green())
    emb.add_field(name="Member:", value=user.name, inline=True)
    emb.set_thumbnail(url=user.avatar_url)
    await bot.userlogs_channel.send("", embed=emb)


@bot.event
async def on_member_unban(self, guild, user):
    emb = Embed(title="Member Unbanned", colour=Colour.red())
    emb.add_field(name="Member:", value=user.name, inline=True)
    emb.set_thumbnail(url=user.avatar_url)
    await bot.userlogs_channel.send("", embed=emb)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)):
        return
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        helpm = await bot.formatter.format_help_for(ctx, ctx.command)
        for m in helpm:
            await ctx.send(m)
    elif isinstance(error, commands.errors.CommandOnCooldown):
        message = await ctx.message.channel.send(
            "{} This command was used {:.2f}s ago and is on "
            "cooldown. Try again in {:.2f}s."
            "".format(ctx.message.author.mention,
                error.cooldown.per - error.retry_after,
                error.retry_after)
            )
        await sleep(10)
        await message.delete()
    else:
        await ctx.send("An error occured while processing the `{}` command."
                       "".format(ctx.command.name))
        print(
            'Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        botdev_msg = "Exception occured in `{0.command}` in {0.message.channel.mention}".format(
            ctx)
        tb = format_exception(type(error), error, error.__traceback__)
        print(''.join(tb))
        botdev_channel = bot.botdev_channel
        await botdev_channel.send(botdev_msg + '\n```' + ''.join(tb) + '\n```')


@bot.command(aliases=['source'])
async def about(ctx):
    """Links to source code on GitHub."""
    await ctx.send("You can view my source code here: "
        "https://github.com/NotQuiteApex/Wheatley-Bot")


# Run the bot
if __name__ == "__main__":
    bot.run(conf["discord"]["token"])
