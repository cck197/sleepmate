import logging

from .agent import BaseAgent
from .mi import get_completion
from .prompt import get_template

log = logging.getLogger(__name__)


def explain_paradoxical_insomnia(x: BaseAgent, utterance: str):
    """Use this whenever the human asks about the difference between the data
    reported by a wearable device and how they feel."""
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x.goal, x.db_user_id, GOALS[0]["paradoxical_insomnia"]),
    )


GOALS = [
    {
        "paradoxical_insomnia": """
        Your goal is to help the human understand the difference between
        self-reported and sensor-based methods of sleep tracking, also known as
        sleep-state misperception or paradoxical insomnia:

        You may notice differences between your sleep diary and sleep tracking
        wearable device, which is completely normal. All of us, whether 'good'
        or 'poor' sleepers, can overestimate or underestimate our sleep. This is
        because sleep is not an on-or-off switch, but rather a time when our
        brain continues to process internal and external information.

        When we overestimate how long we are awake during the night, and
        underestimate the time we have spent sleeping, we can start to become
        concerned. Doubts and worries about sleep can make it even harder to
        sleep.  Hopefully this information can help your sleep data into perspective.

        - Time Spent Sleeping

        It's important to remember that the amount of sleep we get naturally
        changes from night to night. Additionally, there is not a magical number
        that tells us exactly how much sleep we need. The best way to tell
        whether you have had enough sleep, is to see how you feel during the
        day. If you can do most things you would like to do, without dosing off
        when you do not wish to, there is a good chance that you have had enough
        sleep. If you are sleeping shorter on some nights, keep in mind that on
        subsequent night(s) your brain will naturally sleep deeper, but not
        necessarily longer.

        - Sleep Efficiency

        Sleep efficiency is the percentage of time you spend asleep compared to
        the time you spend in bed. Sleep efficiency is a better aspect to focus
        on rather than the total sleep time, as the quality of our sleep is
        often more important than the quantity.

        - Time Taken to Fall Asleep

        Time taken to fall asleep is the time it takes you to fall asleep each
        night. This is also called sleep onset latency. It is important to keep
        in mind that sleep is not an on-or-off state but rather has several
        different stages. When you are drifting into sleep, some parts of your
        brain may still be aware of the surroundings. This means that sometimes
        we may have fallen asleep even though it feels like we are awake, which
        is normal. A helpful tip: when you attempt to sleep, focus on resting
        and relaxing your body, rather than pondering when sleep may come. Sleep
        naturally happens when our body and mind is relaxed. The Open Focus
        exercise is particular helpful here.
        
        Night-time Awakening

        Night-time awakening is the amount of time you spend awake during the
        night. This is also called wake after sleep onset. It's important to
        remember that awakenings are a natural part of everyone's sleep. We all
        go through several sleep cycles per night. After each sleep cycle, we
        naturally wake up briefly, before drifting into the next cycle. It is
        normal for us to wake up a few times per night. Some of these awakenings
        are brief, and we may not remember them at all in the morning. We may
        remember other awakenings if they last a little longer. Night-time
        awakenings are only a problem if we have trouble getting back to sleep.
        A helpful tip: when you wake up in the middle of the night, tell
        yourself that this is normal, as you are probably in between two sleep
        cycles. Let your mind and body keep drifting towards the next sleep
        cycle.  You are more likely to drift back to sleep quickly when you feel
        calm and relaxed during these normal part of awakenings.
        """
    }
]

TOOLS = [explain_paradoxical_insomnia]
