import logging

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import ChatPromptTemplate

from .agent import BaseAgent
from .models import MODELS
from .prompt import get_template

log = logging.getLogger(__name__)


def get_completion(
    memory: ReadOnlySharedMemory,
    utterance: str,
    template: ChatPromptTemplate,
    model_name: str = "gpt",
) -> str:
    chain = LLMChain(llm=MODELS[model_name], prompt=template, memory=memory)
    return chain.run(utterance)


def get_capabilities(x: BaseAgent, utterance: str) -> str:
    """Use this when the human asks about your capabilities or what you can do.
    Tell them that you can help them deal with unwanted thoughts and feelings
    and find motivation to consistently engage in the health behaviours
    conducive to satisfying and restorative sleep."""
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x, get_capabilities.__doc__),
    )


def get_greeting(x: BaseAgent, utterance: str) -> str:
    """Use this when the human says hello. Greet them by name."""
    return get_completion(x.ro_memory, utterance, get_template(x, get_greeting.__doc__))


def get_greeting_no_memory(x: BaseAgent, utterance: str) -> str:
    """Reach out and great the human by name after a short break. Be brief.
    Fewer words are better."""
    return get_completion(
        ReadOnlySharedMemory(
            memory=ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
        ),
        utterance,
        get_template(x, get_greeting_no_memory.__doc__),
    )


def get_affirmation(x: BaseAgent, utterance: str) -> str:
    """Use this whenever the human talks about what they did with any
    positivity. Affirmation is less of a judgement, more of an appreciation of
    positive qualities and behaviors. It is more likely to lift motivation and
    inspire further achievement. Praise the process, NOT the outcome. Be brief,
    fewer words are better.
    """
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x, get_affirmation.__doc__),
    )


def get_open_question(x: BaseAgent, utterance: str) -> str:
    """Use this when the human makes a positive statement that you want to
    explore further and move towards your main goal. Encourage people to say
    what they think and feel, and open the door to talking about change. In
    general, open questions begin with words like what, how, and why. It's
    critically important that you're brief, fewer words are better. Open
    question:
    """
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x, get_open_question.__doc__),
    )


def get_refusal_acknowledgement(x: BaseAgent, utterance: str) -> str:
    """Use this when the human refuses to do something. Acknowledge their
    refusal and say that's ok, we can always come back to that later if you
    like. Be brief, fewer words are better."""
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x, get_refusal_acknowledgement.__doc__),
    )


def get_listening_statement(x: BaseAgent, utterance: str) -> str:
    """Use this when the human is in distress. Hear what they are saying, and
    respond with a listening statement (empathy) to motivate behaviour change.
    Respond to the last thing said below with a listening statement naming the
    emotion and justifying it in context. Be brief, fewer words are better.
    Avoid saying "I hear you" instead say, "it sounds like".
    """
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x, get_listening_statement.__doc__),
    )


TOOLS = [
    get_listening_statement,
    get_open_question,
    get_affirmation,
    get_greeting,
    get_capabilities,
    get_refusal_acknowledgement,
]
