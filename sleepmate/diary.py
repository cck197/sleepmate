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
    now is a good time to record a diary entry. Then guide them through the
    following questions one at a time. Don't give all the questions at once.
    Wait for them to answer each question.

    1. Date of the night you're recording
    2. Sleep quality, one of the following: "very good", "good", "okay", "bad",
    "very bad"
    3. Time you went to bed
    4. Time you tried to fall asleep
    5. How long it took you to fall asleep
    6. How many times you woke up during the night
    7. Total time you were awake during the night
    8. Final wake up time
    9. Time you got out of bed

    Convert the answers into the given formats, and end with a summary of the
    data you've collected and asking if it's correct. Include sleep efficiency
    as a percentage. Sleep efficiency is the percentage of time spent asleep
    while in bed.
    """,
]


def get_sleep_diary_description(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human asks what a sleep diary is. Summarise the
    numbered list of questions only:"""
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
