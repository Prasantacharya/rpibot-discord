import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import aiohttp

API_LINK = "https://alert.rpi.edu/alerts.js"
ALERT_START = "alert_content = "
ALERT_END = "alert_default ="

ALERT_IMG = "https://i.imgur.com/WdSyxXi.jpg"

ALERT_CHANNEL = 178200737422114816

class RpiAlertCog(commands.Cog):
    def __init__(self):
        self.bot = bot

        self.ALERT_CHANNEL = self.bot.get_channel(ALERT_CHANNEL)
        self.ALERT_COLOUR = discord.Colour(0xc91628)

        self.LAST_ALERT_CACHED = ""
        self.ALERT_CACHE_TIME = datetime.now()

        self.alertCheckLoop.start()


    def cog_unload(self):
        self.alertCheckLoop.cancel()


    def createAlertEmbed(self):
        embed = discord.Embed(
            title='**RPI ALERT**',
            description=self.LAST_ALERT_CACHED,
            colour=self.ALERT_COLOUR,
            url="https://alert.rpi.edu"
        )
        embed.set_thumbnail(url=ALERT_IMG)
        embed.set_footer(text=f"This alert was generated at {self.ALERT_CACHE_TIME!s}")
        return embed


    async def checkRPIAlert(self):
        '''
            Polls the given API_LINK for alert changes
            
            Returns:
                True if a new alert has been posted (or the existing alert has been updated)
                False otherwise
        '''

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_LINK) as response:
                    web_request = await response.text()

            begin_index = web_request.find(ALERT_START)
            end_index = web_request.find(ALERT_END)

            # Prepare the text
            alert_text = web_request[begin_index + len(ALERT_START) + 1 : end_index - 3].strip()

            if not alert_text:
                self.LAST_ALERT_CACHED = "No active alerts detected."
                self.ALERT_CACHE_TIME = datetime.now()
                return None

            # Don't spam on startup
            if not self.LAST_ALERT_CACHED:
                self.LAST_ALERT_CACHED = alert_text
                self.ALERT_CACHE_TIME = datetime.now()
                return None
            
            if self.LAST_ALERT_CACHED != alert_text:
                # We have an RPI Alert!
                # Let's hope its not too late!
                self.ALERT_CACHE_TIME = datetime.now()
                self.LAST_ALERT_CACHED = alert_text
                return createAlertEmbed()

        except Exception as ex:
            print("Failed to check alert status!")
            print(ex)
            return None


    @commands.command() 
    async def alert(self, ctx):
        await ctx.send(embed=self.createAlertEmbed())


    @tasks.loop(seconds=60)
    async def alertCheckLoop(self):
        await self.bot.wait_until_ready()
        embed = await checkRPIAlert()
        if embed is not None:
            await self.ALERT_CHANNEL.send(embed=embed)


def setup(bot):
    bot.add_cog(RpiAlertCog(bot))
