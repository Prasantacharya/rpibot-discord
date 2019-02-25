#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio
import logging, json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

description = '''A bot for the RPI discord server'''
pfx = '?'

green = 0x2dc614
red = 0xc91628
blue = 0x2044f7

bot = commands.Bot(command_prefix=pfx, description=description, pm_help=True,
        case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name='with the Tute Screw'))

@bot.command(aliases=['about'])
async def info(ctx):
    '''Shows info about the bot.'''
    embed = discord.Embed(title='About ComputerMan', description=bot.description, colour=blue)
    embed = embed.add_field(name='Contributing', value='Check out the source on GitHub: https://github.com/galengold/rpibot-discord', inline=False)
    embed = embed.add_field(name='License', value='ComputerMan is released under the GNU General Public License, version 3.0', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f'**Pong!** Current ping is {bot.latency*1000:.1f} ms')

@bot.command(aliases=['h'])
async def help(ctx):
    '''Show this message.'''
    with ctx.typing():
        embed = discord.Embed(title='Commands', description=bot.description, colour=green)
        cmds = sorted(list(bot.commands), key=lambda x:x.name)
        for cmd in cmds:
            if cmd.name in ['restart', 'shutdown']:
                continue
            v = cmd.help
            if len(cmd.aliases) > 0:
                v += '\n*Aliases:* ?' +\
                    f', {pfx}'.join(cmd.aliases).rstrip(f', {pfx}')
            embed = embed.add_field(name=pfx+cmd.name, value=v, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def delete(ctx, rng : str = ''):
    '''Deletes your messages in #support. Does not work in any other channel.
    Needs a range, either in hours as a float or `all`.'''
    async with ctx.typing():
        if str(ctx.channel.id) in secrets['nuke_channels']:
            if rng == '':
                    await ctx.channel.send("`?delete` needs a valid argument, either `all` or a number of hours to delete.")
                    return
            elif rng.lower() == 'all':
                history = await ctx.channel.history(limit=None, reverse=True).flatten()
                filtered = [x for x in history if x.author.id == ctx.author.id][:-1]
                for m in filtered:
                    print(m.content)
            elif rng.lower() == 'me':
                await ctx.send("No.")
                return
            else:
                try:
                    rng = float(rng)
                    after_date = datetime.utcnow() - timedelta(hours=rng)
                    history = await ctx.channel.history(limit=None, after=after_date).flatten()
                    filtered = [x for x in history if x.author.id == ctx.author.id][:-1]
                    for m in filtered:
                        print(m.content)
                except:
                    await ctx.channel.send("`?delete` needs a valid argument, either `all` or a number of hours to delete.")
                    return
            filtered_chunks = [filtered[i:i+100] for i in range(0, len(filtered), 100)]
            for c in filtered_chunks:
                if c[0].created_at <= (datetime.utcnow() - timedelta(days=14)) or c[-1].created_at <= (datetime.utcnow() - timedelta(days=14)):
                    for m in c:
                        await m.delete()
                else:
                    await ctx.channel.delete_messages(c)
            try:
                await ctx.message.add_reaction("✅")
            except:
                return
        else:
            try:
                await ctx.message.add_reaction("❌")
            except:
                return


# Special Commands

@bot.command()
async def restart(ctx):
    if any([str(x.id) in secrets['exit_role'] for x in ctx.author.roles]):
        await ctx.channel.send("Restarting...")
        await bot.logout()
    else:
        try:
            await ctx.message.add_reaction("❌")
        except:
            return

@bot.command()
async def shutdown(ctx):
    if any([str(x.id) in secrets['exit_role'] for x in ctx.author.roles]):
        await ctx.channel.send("Shutting down...")
        os._exit(42)
    else:
        try:
            await ctx.message.add_reaction("❌")
        except:
            return

#########################

with open('secrets.json') as secrets_file:
    secrets = json.load(secrets_file)

bot.run(secrets['token'])

