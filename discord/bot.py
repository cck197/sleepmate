import logging
import os
import time

from saq import Queue

import discord
from sleepmate.config import (
    REDIS_URL,
    SLEEPMATE_DISCORD_CHANNEL_EXCLUDE,
    SLEEPMATE_NUDGE_TIME,
)
from sleepmate.executor import X
from sleepmate.nudge import get_or_create_nudge, set_nudge
from sleepmate.user import get_user_from_username

TOKEN = os.getenv("DISCORD_TOKEN")


# requires the message_content intent

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
queue = Queue.from_url(REDIS_URL)

log = logging.getLogger("discord.bot")


@client.event
async def on_ready():
    log.info(f"logged in as {client.user}")


def get_db_user(author):
    return get_user_from_username(username=str(author), name=author.name)


@client.event
async def on_message(message):
    log.info(f"on_message {message.channel.id=} {message.author=} {message.content=}")
    if message.channel.name in SLEEPMATE_DISCORD_CHANNEL_EXCLUDE:
        log.info(f"ignoring message in {message.channel.name}")
        return

    if message.author == client.user:
        return

    if message.content.strip().startswith("//"):
        return

    async with message.channel.typing():
        db_user = get_db_user(message.author)
        x = X(username=db_user.username, hello=None, log_=log)
        await message.channel.send(await x.arun(message.content))
        db_nudge = get_or_create_nudge(x)
        log.info(f"on_message {db_user.username=} {db_nudge.to_mongo().to_dict()=}")
        if not db_nudge.nudged:
            log.info(f"scheduling nudge for {db_user.username}")
            await queue.enqueue(
                "send_nudge",
                channel_id=message.channel.id,
                db_user_id=str(db_user.id),
                scheduled=time.time() + SLEEPMATE_NUDGE_TIME,
            )
            set_nudge(db_nudge, nudged=True)


if __name__ == "__main__":
    client.run(TOKEN, root_logger=True)
