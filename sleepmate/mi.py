from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory
from langchain.prompts import ChatPromptTemplate

from .config import SLEEPMATE_DEFAULT_MODEL_NAME, SLEEPMATE_SAMPLING_TEMPERATURE
from .helpful_scripts import Goal
from .prompt import get_template


def get_completion(
    memory: ReadOnlySharedMemory,
    utterance: str,
    template: ChatPromptTemplate,
) -> str:
    llm = ChatOpenAI(
        model_name=SLEEPMATE_DEFAULT_MODEL_NAME,
        temperature=SLEEPMATE_SAMPLING_TEMPERATURE,
    )
    chain = LLMChain(llm=llm, prompt=template, memory=memory)
    return chain.run(utterance)


def get_capabilities(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
) -> str:
    """Use this when the human asks about your capabilities or what you can do.
    Tell them that you can help them deal with unwanted thoughts and feelings
    and find motivation to consistently engage in the health behaviours
    conducive to satisfying and restorative sleep."""
    return get_completion(
        memory, utterance, get_template(goal, db_user_id, get_capabilities.__doc__)
    )


def get_greeting(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
) -> str:
    """Use this when the human says hello. Greet them by name. Occasionally ask
    them how they're feeling right now, in this moment.
    """
    return get_completion(
        memory, utterance, get_template(goal, db_user_id, get_greeting.__doc__)
    )


def get_affirmation(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
) -> str:
    """Use this whenever the human talks about what they did with any
    positivity. Affirmation is less of a judgment, more of an appreciation of
    positive qualities and behaviors. It is more likely to lift motivation and
    inspire further achievement. Praise the process, NOT the outcome. Be brief,
    fewer words are better.
    """
    return get_completion(
        memory, utterance, get_template(goal, db_user_id, get_affirmation.__doc__)
    )


def get_open_question(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
) -> str:
    """Use this when the human makes a positive statement that you want to
    explore further and move towards your main goal. Encourage people to say
    what they think and feel, and open the door to talking about change. In
    general, open questions begin with words like what, how, and why. It's
    critically important that you're brief, fewer words are better. Open
    question:
    """
    return get_completion(
        memory, utterance, get_template(goal, db_user_id, get_open_question.__doc__)
    )


def get_listening_statement(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
) -> str:
    """Use this when the human is in distress. Hear what they are saying, and
    respond with a listening statement (empathy) to motivate behaviour change.
    Respond to the last thing said below with a listening statement naming the
    emotion and justifying it in context. Be brief, fewer words are better.
    Avoid saying "I hear you" instead say, "it sounds like".
    """
    return get_completion(
        memory,
        utterance,
        get_template(goal, db_user_id, get_listening_statement.__doc__),
    )


TOOLS = [
    get_listening_statement,
    get_open_question,
    get_affirmation,
    get_greeting,
    get_capabilities,
]
