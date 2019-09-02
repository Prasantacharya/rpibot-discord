#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime, timedelta
import settings

logging.basicConfig(level=logging.INFO)

description = '''A bot for the RPI discord server'''

bot = commands.Bot(command_prefix=settings.pfx, description=description, pm_help=True,
        case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name=settings.status))

@bot.event
async def on_message(message):
    if 'xd' in message.content.lower():
        await message.add_reaction(discord.utils.find(lambda x: x.id == 564136561927651338, bot.emojis))

    await bot.process_commands(message)

@bot.command(aliases=['about'])
async def info(ctx):
    '''Shows info about the bot.'''
    embed = discord.Embed(title='About ComputerMan', description=bot.description, colour=settings.blue)
    embed = embed.add_field(name='Contributing', value='Check out the source on GitHub: https://github.com/ClassAbbyAmp/rpibot-discord', inline=False)
    embed = embed.add_field(name='License', value='ComputerMan is released under the GNU General Public License, version 3.0', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f'**Pong!** Current ping is {bot.latency*1000:.1f} ms')

@bot.command(aliases=['h'])
async def help(ctx):
    '''Show this message.'''
    with ctx.typing():
        embed = discord.Embed(title='Commands', description=bot.description, colour=settings.green)
        cmds = sorted(list(bot.commands), key=lambda x:x.name)
        for cmd in cmds:
            if cmd.name in settings.hide_cmds:
                continue
            v = cmd.help
            if len(cmd.aliases) > 0:
                v += f'\n*Aliases:* {settings.pfx}' + f', {settings.pfx}'.join(cmd.aliases).rstrip(f', {settings.pfx}')
            embed = embed.add_field(name=settings.pfx+cmd.name, value=v, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def delete(ctx, rng : str = ''):
    '''Deletes your messages in a channel. Needs a range, either in hours as a float or `all`.'''
    async with ctx.typing():
        if rng == '':
                await ctx.channel.send("`?delete` needs a valid argument, either `all` or a number of hours to delete.")
                return
        elif rng.lower() == 'all':
            after_date = None
        elif rng.lower() == 'me':
            await ctx.send("No.")
            return
        else:
            try:
                rng = float(rng)
                after_date = datetime.utcnow() - timedelta(hours=rng)
            except:
                await ctx.channel.send("`?delete` needs a valid argument, either `all` or a number of hours to delete.")
                return
        history = await ctx.channel.history(limit=None, after=after_date).flatten()
        filtered = [x for x in history if x.author.id == ctx.author.id]
        filtered_chunks = [filtered[i:i+100] for i in range(0, len(filtered), 100)]
        for c in filtered_chunks:
            if c[0].created_at <= (datetime.utcnow() - timedelta(days=14)) or c[-1].created_at <= (datetime.utcnow() - timedelta(days=14)):
                for m in c:
                    await m.delete()
            else:
                await ctx.channel.delete_messages(c)
        try:
            await ctx.send("✅")
        except:
            return


# Secret Commands
@bot.command()
async def mute(ctx, user: discord.Member, until = None):
    if any([x.id == settings.exit_role for x in ctx.author.roles]):
        try:
            mute_role = discord.utils.get(ctx.guild.roles, id=settings.muted_role)
            await user.add_roles(mute_role, reason=f'Muted by RPIbot until {until}')
            # write until date to file
        except Exception as e:
            print(e)
            return
    else:
        try:
            await ctx.message.add_reaction("❌")
        except:
            return

@bot.command()
async def unmute(ctx, user: discord.Member):
    if any([x.id == settings.exit_role for x in ctx.author.roles]):
        try:
            mute_role = discord.utils.get(ctx.guild.roles, id=settings.muted_role)
            await user.remove_roles(mute_role, reason='Unmuted by RPIbot')
        except Exception as e:
            print(e)
            return
    else:
        try:
            await ctx.message.add_reaction("❌")
        except:
            return

@bot.command()
async def restart(ctx):
    if any([x.id == settings.exit_role for x in ctx.author.roles]):
        await ctx.channel.send("Restarting...")
        await bot.logout()
    else:
        try:
            await ctx.message.add_reaction("❌")
        except:
            return

@bot.command()
async def shutdown(ctx):
    if any([x.id == settings.exit_role for x in ctx.author.roles]):
        await ctx.channel.send("Shutting down...")
        os._exit(42)
    else:
        try:
            await ctx.message.add_reaction("❌")
        except:
            return

#########################

# check muted list

token = open('token').read().strip()

bot.run(token)

