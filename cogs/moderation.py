import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio


class ModerationCog(commands.Cog):
    def __init__(self):
        self.bot = bot

	@commands.command()
	async def delete(self, ctx, rng : str = ''):
	    '''Deletes your messages in a channel. Needs a range, either in hours as a float or `all`.'''
	    async with ctx.typing():
	        msg_time = ctx.message.created_at
	        if rng == '':
	            await ctx.send("`?delete` needs a valid argument, either `all` or a number of hours to delete.")
	            return
	        elif rng.lower() == 'all':
	            after_date = None
	        elif rng.lower() == 'me':
	            await ctx.send("No.")
	            return
	        else:
	            try:
	                rng = float(rng)
	                after_date = msg_time - timedelta(hours=rng)
	            except:
	                await ctx.send("`?delete` needs a valid argument, either `all` or a number of hours to delete.")
	                return
	        history = await ctx.channel.history(limit=None, after=after_date).flatten()
	        filtered = list(filter(lambda x: x.author.id == ctx.author.id, history))
	        filtered_chunks = [filtered[i:i+100] for i in range(0, len(filtered), 100)]
	        for c in filtered_chunks:
	            if c[0].created_at <= (msg_time - timedelta(days=14)) or c[-1].created_at <= (msg_time - timedelta(days=14)):
	            	await asyncio.gather(*(m.delete() for msg in c))
	            else:
	                await ctx.channel.delete_messages(c)
	        try:
	            await ctx.send("✅")
	        except:
	            return


	# Secret Commands
	@commands.command(hidden=True)
	async def mute(self, ctx, user: discord.Member, until = None):
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

	@commands.command(hidden=True)
	async def unmute(self, ctx, user: discord.Member):
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

	@commands.command(hidden=True)
	async def restart(self, ctx):
	    if any([x.id == settings.exit_role for x in ctx.author.roles]):
	        await ctx.channel.send("Restarting...")
	        await self.bot.logout()
	    else:
	        try:
	            await ctx.message.add_reaction("❌")
	        except:
	            return

	@commands.command(hidden=True)
	async def shutdown(self, ctx):
	    if any([x.id == settings.exit_role for x in ctx.author.roles]):
	        await ctx.channel.send("Shutting down...")
	        os._exit(42)
	    else:
	        try:
	            await ctx.message.add_reaction("❌")
	        except:
	            return

def setup(bot):
    bot.add_cog(ModerationCog(bot))
