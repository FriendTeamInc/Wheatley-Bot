#!/usr/bin/env python3

from sys import exit
from os import getenv
from traceback import format_exception
from asyncio import sleep

from discord import errors, Embed, Color, TextChannel
from discord.ext import commands
from discord.utils import get, escape_mentions

import toml


bot = commands.Bot(command_prefix='.')
try:
    conf = toml.load("conf.toml")
except FileNotFoundError:
    exit("Config not found!")


userroles = ["color", "stream", "pronoun"]


@bot.event
async def on_ready():
    bot.conf = conf

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

        # Friends
        # Will be changed later to different roles to make it more server-agnostic
        bot.owner_role  = get(guild.roles, name="Admin")
        bot.admin_role  = get(guild.roles, name="Admin")
        bot.staff_role  = get(guild.roles, name="Admin")
        bot.friend_role = get(guild.roles, name="Friend")

        # Dev channels
        bot.botdev_channel   = get(guild.channels, name="bot-dev")
        bot.botlogs_channel  = get(guild.channels, name="bot-logs")
        bot.userlogs_channel = get(guild.channels, name="user-logs")
        bot.msglogs_channel  = get(guild.channels, name="msg-logs")

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
                    bot.roles[roletype][rolekey.lower()] = role

                    # report roles for errors
                    if role is None:
                        roleerr[roletype]["key"].append(rolekey)
                        roleerr[roletype]["role"].append(rolename)
                        hasroleerr = True
            else:
                # roles not found in config
                hasroles[roletype] = False

    await bot.botlogs_channel.send("Coming back online.")

    # Load addons
    bot.addons = [
        "moderation",
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
        #await bot.botlogs_channel.send("Patch these roles in your `conf.toml` or the roles manager dingus!")

    # We're in.
    print(f"Client logged in as {bot.user.name}, in the following guild : {bot.guild.name}")
    #await bot.botdev_channel.send("Back online!")


async def logembed(user, stat, color):
    global bot
    emb = Embed(title="Member "+stat, color=color)
    emb.add_field(name="Member:", value=user.name, inline=True)
    emb.set_thumbnail(url=user.avatar_url)
    await bot.userlogs_channel.send("", embed=emb)

@bot.event
async def on_member_join(user): await logembed(user, "Joined", Color.green())

@bot.event
async def on_member_remove(user): await logembed(user, "Left", Color.red())

@bot.event
async def on_member_ban(guild, user): await logembed(user, "Banned", Color.dark_red())

@bot.event
async def on_member_unban(guild, user): await logembed(user, "Unbanned", Color.teal())


@bot.event
async def on_command_error(ctx, error):
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
        await bot.botdev_channel.send(botdev_msg + '\n```' + ''.join(tb) + '\n```')


@bot.command(aliases=['source'])
async def about(ctx):
    """Links to source code on GitHub."""
    await ctx.send("You can view my source code here: "
        "https://github.com/NotQuiteApex/Wheatley-Bot")


@commands.has_role("Admin")
@bot.command()
async def say(ctx, channel: TextChannel, *, msg: str=""):
    """The bot speaks!"""
    await channel.send(escape_mentions(msg))


# Run the bot
if __name__ == "__main__":
    bot.run(conf["discord"]["token"])
