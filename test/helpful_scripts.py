import logging

from sleepmate.executor import X
from sleepmate.helpful_scripts import display_rich_markdown


def get_X(user, goal):
    return X(
        username=user.username,
        hello=None,
        goal=goal,
        fixed_goal=True,
        display_func=display_rich_markdown,
        log_=logging.getLogger("sleepmate.executor"),
    )


x(
    "who or what do you believe if the device says that you slept well but you "
    "know you slept like crap? it's sleep-state misperception or paradoxical insomnia"
)
