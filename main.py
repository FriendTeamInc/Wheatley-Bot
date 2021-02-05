#!/usr/bin/env python3

from sys import exit, exc_info
from os import getenv
from os.path import isfile
from traceback import format_exception
from asyncio import sleep
from datetime import datetime

from discord import errors, Embed, Color, TextChannel
from discord.ext import commands
from discord.utils import get, escape_mentions

import json
import toml
import aiofiles as aiof

import logging


bot = commands.Bot(command_prefix='.')
try:
    conf = toml.load("conf.toml")
except FileNotFoundError:
    exit("Config not found!")


userroles = ["color", "pronoun", "game"]


@bot.event
async def on_ready():
    bot.conf = conf

    bot.userroles = userroles

    # important role vars for error reporting
    missingroleskey = False
    hasroleerr = False
    roleerr = {}
    hasroles = {}

    for role in userroles:
        roleerr[role] = {"role":[],"key":[]}
        hasroles[role] = True
    
    for guild in bot.guilds:
        # This bot is only meant to manage one server.
        # Do not invite your bot to more than one server.
        bot.guild = guild

        # Autoprobation (off by default)
        # To prevent raids
        bot.autoprobate = False

        # Friends
        # Will be changed later to different roles to make it more server-agnostic
        bot.owner_role  = get(guild.roles, name="Owner")
        bot.admin_role  = get(guild.roles, name="Admin")
        bot.staff_role  = get(guild.roles, name="Admin")
        bot.friend_role = get(guild.roles, name="Friend")

        # User roles given by staff (TODO: make configurable via toml.)
        bot.muted_role      = get(guild.roles, name="Muted")
        bot.probated_role   = get(guild.roles, name="Probated")
        bot.unapproved_role = get(guild.roles, name="Unapproved")

        # Dev channels
        bot.botdev_channel  = get(guild.channels, name="bot-dev")
        bot.botlogs_channel = get(guild.channels, name="bot-logs")

        # User log channels (joins, leaves, message edits, etc.)
        bot.userlogs_channel = get(guild.channels, name="user-logs")
        bot.msglogs_channel  = get(guild.channels, name="msg-logs")

        bot.modmail_category = get(guild.categories, name="MODMAIL")

        if conf["roles"] == None:
            missingroleskey = True
            break

        # Load in user obtainable roles
        bot.roles = {}
        for roletype in userroles:
            confrole = roletype + "s" # conf uses the plural noun
            if conf["roles"][confrole] != None: # check if role config exists
                # iterate through list and add roles
                bot.roles[confrole] = {}
                for rolekey, rolename in conf["roles"][confrole].items():
                    role = get(guild.roles, name=rolename)
                    bot.roles[confrole][rolekey.lower()] = role

                    # report roles for errors
                    if role is None:
                        roleerr[roletype]["key"].append(rolekey)
                        roleerr[roletype]["role"].append(rolename)
                        hasroleerr = True
            else:
                # roles not found in config
                hasroles[roletype] = False
        
        # stream specific role data
        bot.streams = {}
        bot.streams_data = {}
        bot.streams_notif_channel = None
        await bot.botlogs_channel.send(str(conf["streams"]))
        for rolekey, roledata in conf["streams"].items():
            if rolekey == "notif_channel":
                bot.streams_notif_channel = roledata
            else:
                bot.streams[rolekey] = conf["streams"][rolekey]["role"]
                bot.streams_data[conf["streams"][rolekey]["user"]] = {
                    "link": conf["streams"][rolekey]["link"],
                    "role": conf["streams"][rolekey]["role"]
                }
        

    await bot.botlogs_channel.send("Back online!")

    # Load addons
    bot.addons = [
        "events",
        "moderation",
        "modmail",
        "streams",
        "system",
        "warn"
    ]

    # load extra user role cogs if available
    for roletype in userroles:
        if hasroles[roletype]:
            bot.addons.append(roletype + "s")

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
            await bot.botlogs_channel.send("", embed=emb)
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
            await bot.botlogs_channel.send("", embed=emb)

    # We're in.
    print(f"Client logged in as {bot.user.name}, in the following guild : {bot.guild.name}")
    #await bot.botdev_channel.send("Back online!")


@bot.event
async def on_command_error(ctx, error):
    global bot
    if isinstance(error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)):
        return
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        helpm = await bot.formatter.format_help_for(ctx, ctx.command)
        for m in helpm: await ctx.send(m)
    elif isinstance(error, commands.errors.CommandOnCooldown):
        message = await ctx.send(
            "{} This command was used {:.2f}s ago and is on "
            "cooldown. Try again in {:.2f}s."
            "".format(ctx.message.author.mention,
                error.cooldown.per - error.retry_after,
                error.retry_after)
            )
        await sleep(10)
        await message.delete()
    else:
        await ctx.send(f"An error occured while processing the `{ctx.command.name}` command.")
        print(f"Ignoring exception in command {ctx.command} in {ctx.message.channel}")
        botdev_msg = f"Exception occured in `{ctx.command}` in {ctx.message.channel.mention}"
        tb = format_exception(type(error), error, error.__traceback__)
        print(''.join(tb))
        await bot.botdev_channel.send(botdev_msg + '\n```py' + ''.join(tb) + '\n```')

@bot.event
async def on_error(event, *args, **kwargs):
    global bot
    await bot.botlogs_channel.send(f"An error occured while processing an event.")
    txt = f"Event: {event}\n"
    (exc_type, exc_value, exc_tb) = exc_info()
    txt += f"```py\n{format_exception(exc_type, exc_value, exc_tb)}```"
    await bot.botlogs_channel.send(txt)


@bot.command(aliases=['source'])
async def about(ctx):
    """Links to source code on GitHub."""
    await ctx.send("You can view my source code here: "
        "https://github.com/NotQuiteApex/Wheatley-Bot")


@commands.has_any_role("Admin")
@bot.command()
async def say(ctx, channel: TextChannel, *, msg: str=""):
    """The bot speaks!"""
    await channel.send(msg)

@bot.command()
async def ping(ctx): # Thanks Ridley!
    """Pong!"""
    latency = datetime.now() - ctx.message.created_at
    await ctx.send(f":ping_pong: Pong! {latency.microseconds / 1000.0} ms")


# Run the bot
if __name__ == "__main__":
    bot.run(conf["discord"]["token"])
