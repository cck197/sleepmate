from langchain.memory import ReadOnlySharedMemory

from .mi import get_completion, get_template

model_name = "gpt-4"


def get_self_harm_advice(
    memory: ReadOnlySharedMemory, utterance: str, model_name=model_name
) -> str:
    """Use this when the human is suggesting they might self-harm. Provide
    information about 988 Suicide and Crisis Lifeline:"""
    return get_completion(
        memory,
        utterance,
        get_template(get_self_harm_advice.__doc__),
        model_name,
    )


def get_on_topic(
    memory: ReadOnlySharedMemory, utterance: str, model_name=model_name
) -> str:
    """Use this when the human asks about health and performance. Tell them you don't know
    anything about {input}."""

    return get_completion(
        memory,
        utterance,
        get_template(get_on_topic.__doc__),
        model_name,
    )


TOOLS = [get_self_harm_advice, get_on_topic]
