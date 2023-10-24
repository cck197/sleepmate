import os

import discord
from sleepmate.agent import X
from sleepmate.user import get_user_from_username

TOKEN = os.getenv("DISCORD_TOKEN")


# This example requires the 'message_content' intent.

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


def get_db_user(author):
    return get_user_from_username(username=str(author), name=author.name)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        db_user = get_db_user(message.author)
        x = X(username=db_user.username, hello=None)
        await message.channel.send(await x.arun(message.content))


client.run(TOKEN)
