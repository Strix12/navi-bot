import asyncio
import discord
import logging
import os
import praw

from datetime import datetime, time, timedelta
from dataclasses import dataclass


@dataclass
class Command:
    name: str
    description: str


class BotClient(discord.Client):
    __CMD_LIST = [
        Command("help", "Displays a list of valid commands.")
    ]
    __CMD_SIGNIFIER = "!"
    __WHEN_TO_POST = time(8, 0, 0)

    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(intents=intents)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter("[%(asctime)s] <%(levelname)s> %(message)s",
                                                       datefmt="%Y-%m-%d %H:%M:%S"))

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)

        self.reddit = praw.Reddit(
            client_id="qhvBd_uVcKSvIhs5-0XxPg",
            client_secret=os.environ.get("REDDIT_TOKEN"),
            user_agent="windows:io.strix12.navibot:v1.0.0 (by u/ShadowCurv)"
        )
        self.logger.info("Successfully established connection to Reddit API")

        loggers = (logging.getLogger(name) for name in ("praw", "prawcore"))

        for logger in loggers:
            logger.setLevel(logging.DEBUG)
            logger.addHandler(console_handler)

    async def post_eyebleach(self):
        async def publish_msg():
            top_post = self.reddit.subreddit("eyebleach").top(time_filter="day", limit=1).next()
            msg_content = top_post.url
            channel = self.get_guild(1189962335243223223).get_channel(1191127646243922000)

            await channel.send(msg_content)
            self.logger.info(f"Published eyebleach to the {channel.name} channel.")
            self.logger.debug(f"Published image url: {msg_content}")

        async def wait_until_tomorrow():
            today = datetime.utcnow()
            tomorrow = datetime.combine(today.date() + timedelta(days=1), self.__WHEN_TO_POST)
            wait_time = (tomorrow - today).total_seconds()
            self.logger.debug(f"waiting {wait_time} seconds before posting")
            await asyncio.sleep(wait_time)

        now = datetime.utcnow()

        if now.time() > self.__WHEN_TO_POST:
            await wait_until_tomorrow()

        while True:
            await wait_until_tomorrow()
            await publish_msg()

    async def on_ready(self):
        self.logger.info(f"Successfully connected to the WIRED using credentials @{self.user}")
        await self.post_eyebleach()

    async def on_message(self, message: discord.Message):
        def author_is_self():
            return message.author == self.user

        def message_empty():
            return len(message.content) == 0

        def not_command():
            return message.content[0] != self.__CMD_SIGNIFIER

        if any(f() for f in (author_is_self, message_empty, not_command)):
            return

        tokens = message.content.split(" ")
        cmd = tokens[0][1:]
        args = tokens[1:]

        if all((cmd_data.name != cmd for cmd_data in self.__CMD_LIST)):
            return

        self.logger.info(f"User @{message.author} executed the {cmd} command")
        guild_id = message.guild.id
        channel_id = message.channel.id

        if cmd == "help":
            msg_content = "\n" + "\n".join((f"`{self.__CMD_SIGNIFIER}{cmd_data.name}` `{cmd_data.description}`"
                                            for cmd_data in self.__CMD_LIST))
            await self.get_guild(guild_id).get_channel(channel_id).send(msg_content)
