#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import datetime, timedelta
import settings

INITIAL_EXTENSIONS = []

async def run():
    """
    Where the bot gets started. If you wanted to create an database connection pool or other session for the bot to use,
    it's recommended that you create it here and pass it to the bot as a kwarg.
    """


    description = '''A bot for the RPI discord server'''

    bot = Bot(description=description)
    try:
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
    except KeyboardInterrupt:
        await bot.logout()
        await db.close()

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=('?',),
            pm_help=True,
            case_insensitive=True,
            description=kwargs['description']
        )
        self.start_time = None
        self.app_info = None

        self.loop.create_task(self.track_start())

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
                logging.info(f'Loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                logging.warning(f'Failed to load extension {error}')

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.utcnow()

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        self.app_info = await self.application_info()
        logging.info(f'Logged in as: {self.user.name}')
        logging.info(f'Using discord.py version: {discord.__version__}')
        logging.info(f'Owner: {self.app_info.owner}')

        await self.change_presence(activity=discord.Game(name=settings.status))

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        # ignore all bots
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_error(self, context, exception):
        tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        logging.error(f'Ignoring exception in command {context.command}:\n{tb}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
