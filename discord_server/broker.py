import time

from bot import TOKEN, log, queue

import discord
from sleepmate.config import SLEEPMATE_NUDGE_TIME
from sleepmate.helpful_scripts import get_delay
from sleepmate.nudge import get_nudge, set_nudge, should_send_nudge


class MyClient(discord.Client):
    def __init__(self, channel_id, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = channel_id
        self.text = text

    async def on_ready(self):
        log.info(f"logged in as {self.user} (ID: {self.user.id})")
        channel = self.get_channel(self.channel_id)  # channel ID goes here
        async with channel.typing():
            await channel.send(self.text)
        await self.close()


async def send_nudge(ctx, *, channel_id, db_user_id, n=0, max_retries=5):
    db_nudge = get_nudge(db_user_id)
    log.info(
        f"send_nudge {channel_id=} {db_user_id=} {db_nudge.last_seen=} {n=} {max_retries=}"
    )
    if n > max_retries:
        log.info(
            f"send_nudge maxed out {channel_id=} {db_user_id=} {n=} {max_retries=}"
        )
        set_nudge(db_nudge, job_id=None)
        return
    if should_send_nudge(db_nudge):
        log.info(f"send_nudge sending {channel_id=} {db_user_id=} {db_nudge.text=}")
        client = MyClient(channel_id, db_nudge.text, intents=discord.Intents.default())
        await client.start(TOKEN)
        set_nudge(db_nudge, job_id=None, reset_text=True)
        return
    # reschedule a nudge
    job = await queue.enqueue(
        "send_nudge",
        channel_id=channel_id,
        db_user_id=db_user_id,
        n=n + 1,
        max_retries=max_retries,
        scheduled=time.time() + get_delay(SLEEPMATE_NUDGE_TIME, 5),
    )
    set_nudge(db_nudge, job_id=job.id)


settings = {
    "queue": queue,
    "functions": [send_nudge],
    "concurrency": 10,
}
