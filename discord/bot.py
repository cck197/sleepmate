import logging
import os

import discord
from sleepmate.agent import X
from sleepmate.config import SLEEPMATE_DISCORD_CHANNEL_EXCLUDE
from sleepmate.user import get_user_from_username

TOKEN = os.getenv("DISCORD_TOKEN")


# This example requires the 'message_content' intent.

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

log = logging.getLogger("discord.bot")


@client.event
async def on_ready():
    log.info(f"logged in as {client.user}")


def get_db_user(author):
    return get_user_from_username(username=str(author), name=author.name)


@client.event
async def on_message(message):
    if message.channel.name in SLEEPMATE_DISCORD_CHANNEL_EXCLUDE:
        log.info(f"ignoring message in {message.channel.name}")
        return

    if message.author == client.user:
        return

    if message.content.startswith("!"):
        return

    async with message.channel.typing():
        db_user = get_db_user(message.author)
        x = X(username=db_user.username, hello=None, log_=log)
        await message.channel.send(await x.arun(message.content))


client.run(TOKEN, root_logger=True)
