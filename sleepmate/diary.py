from langchain.memory import ReadOnlySharedMemory

from .mi import get_completion, get_template

model_name = "gpt-4"


DIARY_GOAL_PROMPTS = [
    """
    Your goal is find out if the human has ever kept a sleep diary, but don't
    ask until they've confirmed the accuracy of at least one listening
    statement. If they haven't kept a sleep diary, ask if they'd like the AI to
    help them keep one. If they have, ask if they'd like to share it with the
    AI.
    """,
    """
    Your goal is to record a sleep diary entry for a given night. First ask if
    now is a good time to collect the data. Then ask the following questions:

    1. Date of the night you're recording, in the format "mm/dd/yyyy"
    2. Sleep quality, one of the following: "very good", "good", "okay", "bad",
    "very bad"
    3. Time you went to bed, in the format "hh:mm am/pm"
    4. Time you tried to fall asleep, in the format "hh:mm am/pm"
    5. How long it took you to fall asleep, in the format "hh:mm"
    6. How many times you woke up during the night, as a number
    7. Total time you were awake during the night, in the format "hh:mm"
    8. Final wake up time, in the format "hh:mm am/pm"
    9. Time you got out of bed, in the format "hh:mm am/pm"

    Convert the answers into the given formats, and end by summarising the data
    you've collected and asking if it's correct.
    """,
]


def get_sleep_diary_description(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human asks what a sleep diary is. Summarise the
    numbered list of questions:"""
    return get_completion(
        memory,
        utterance,
        get_template(
            goal,
            get_sleep_diary_description.__doc__
            + DIARY_GOAL_PROMPTS[1]
            + "End by asking if they'd like the AI to help them keep a sleep diary.",
        ),
        model_name,
    )


TOOLS = [get_sleep_diary_description]
