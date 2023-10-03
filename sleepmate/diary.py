from langchain.memory import ReadOnlySharedMemory

model_name = "gpt-4"


def get_sleep_diary_question(
    memory: ReadOnlySharedMemory, utterance: str, model_name=model_name
) -> str:
    """Use this if the client has expressed dissatisfaction with their sleep,
    has confirmed the accuracy of a listening statement, and has not answered
    the question before.
    """
    return "Have you ever kept a sleep diary?"
