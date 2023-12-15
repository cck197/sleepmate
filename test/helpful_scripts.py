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
