from langchain.memory import ReadOnlySharedMemory

from .mi import get_completion, get_template


def get_self_harm_advice(
    memory: ReadOnlySharedMemory, goal: str, utterance: str
) -> str:
    """Use this when the human is suggesting they might self-harm. Provide
    information about 988 Suicide and Crisis Lifeline:"""
    return get_completion(
        memory,
        utterance,
        get_template(goal, get_self_harm_advice.__doc__),
    )


def get_on_topic(memory: ReadOnlySharedMemory, goal: str, utterance: str) -> str:
    """Use this when the human asks about anything other than health and
    performance. Tell them you don't know anything about {input}."""

    return get_completion(
        memory,
        utterance,
        get_template(goal, get_on_topic.__doc__),
    )


# TOOLS = [get_self_harm_advice, get_on_topic]
