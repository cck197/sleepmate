from dataclasses import dataclass

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

model_name = "gpt-4"

SYSTEM_DESCRIPTION = "You are an AI clinician skilled in Motivational Interviewing."


def get_completion(
    memory: ReadOnlySharedMemory,
    utterance: str,
    template: ChatPromptTemplate,
    model_name=model_name,
) -> str:
    llm = ChatOpenAI(model_name=model_name)
    chain = LLMChain(llm=llm, prompt=template, memory=memory)
    return chain.run(utterance)


def get_template(goal: str, prompt: str) -> ChatPromptTemplate:
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                f"{SYSTEM_DESCRIPTION}\n{goal}\n{prompt}"
            ),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )


def get_greeting(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human says hello. Get their name from the conversation
    below. If you don't their name, ask.  Otherwise, greet them by name and ask
    them how they're feeling. Then move along to your main goal.
    """
    return get_completion(
        memory, utterance, get_template(goal, get_greeting.__doc__), model_name
    )


def get_affirmation(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this whenever the human talks about what they did with any
    positivity. Affirmation is less of a judgment, more of an appreciation of
    positive qualities and behaviors. It is more likely to lift motivation and
    inspire further achievement. Praise the process, NOT the outcome. Be brief,
    fewer words are better.
    """
    return get_completion(
        memory, utterance, get_template(goal, get_affirmation.__doc__), model_name
    )


def get_open_question(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human makes a positive statement that you want to
    explore further and move towards your main goal. Encourage people to say
    what they think and feel, and open the door to talking about change. In
    general, open questions begin with words like what, how, and why. It's
    critically important that you're brief, fewer words are better. Open
    question:
    """
    return get_completion(
        memory, utterance, get_template(goal, get_open_question.__doc__), model_name
    )


def get_listening_statement(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human is in distress. Hear what they are saying, and
    respond with a listening statement (empathy) to motivate behaviour change.
    Respond to the last thing said below with a listening statement naming the
    emotion and justifying it in context. Be brief, fewer words are better.
    """
    return get_completion(
        memory,
        utterance,
        get_template(goal, get_listening_statement.__doc__),
        model_name,
    )


@dataclass
class Translation:
    input: str
    output: str


affirmation_examples = [
    Translation(
        "I managed to go to the gym twice this week, but it's not like it's a habit yet.",
        "It's great that you've taken the first steps by going to the gym. Starting is often the hardest part.",
    ),
    Translation(
        "I've been trying to eat better, but I had a couple of cheat days.",
        "The fact that you're making an effort to eat better is commendable. No one is perfect, and cheat days are part of the journey.",
    ),
    Translation(
        "I haven't had a drink in five days, which is a big deal for me.",
        "Five days without a drink is a significant accomplishment, especially given how challenging it can be.",
    ),
    Translation(
        "I've been feeling really stressed but managed not to smoke.",
        "That's impressive self-control, managing stress without relying on smoking.",
    ),
    Translation(
        "I'm trying to be more active, but I only took the stairs at work a few times this week.",
        "Choosing to take the stairs is a positive step, even if it's just a few times. Every effort counts.",
    ),
    Translation(
        "I wanted to spend less time on my phone, and I did, but just for a day.",
        "A day with less screen time is a step in the right direction, and it shows you can make the change.",
    ),
    Translation(
        "I've been journaling to cope with my feelings, though I missed a couple of days.",
        "Journaling is a healthy way to process emotions. It's okay to miss days; what's important is that you've started.",
    ),
    Translation(
        "I've started meditating, but I can only manage a few minutes at a time.",
        "Meditation, even for a few minutes, can be beneficial. It's great that you're giving it a try.",
    ),
    Translation(
        "I've been trying to reach out and reconnect with old friends, but it's hard.",
        "The effort to reconnect shows courage and a desire for meaningful relationships.",
    ),
    Translation(
        "I've started cooking at home instead of eating out, even if it's just simple meals.",
        "Cooking at home is a significant change and a positive step toward better health, regardless of the meal's complexity.",
    ),
]

listening_examples = [
    Translation(
        "I'm finding it really hard to stick to a diet with all the stress at work.",
        "It sounds like your work stress is making it difficult to focus on your diet.",
    ),
    Translation(
        "I want to quit smoking, but I don't know if I can.",
        "It sounds like you're eager to quit but uncertain about your ability to do so.",
    ),
    Translation(
        "I've been trying to exercise more, but it's tough with my busy schedule.",
        "I hear you. Your schedule makes it challenging to find time for exercise.",
    ),
    Translation(
        "Sometimes I feel like my friends don't understand what I'm going through.",
        "It seems like you're feeling isolated in your experience.",
    ),
    Translation(
        "I want to be more positive, but it's hard with so much negativity around me.",
        "It sounds like your environment is making it challenging for you to maintain a positive outlook.",
    ),
    Translation(
        "I haven't been sleeping well lately, and it's affecting my mood.",
        "It sounds like your sleep patterns are closely connected to how you're feeling.",
    ),
    Translation(
        "I've tried to cut back on drinking, but social events make it difficult.",
        "It seems that social settings are a stumbling block for you in reducing your alcohol intake.",
    ),
    Translation(
        "I know I should be saving money, but I just love shopping.",
        "I hear you. The enjoyment you get from shopping seems to conflict with your goal of saving money.",
    ),
    Translation(
        "I can't focus on my work with all the distractions at home.",
        "It sounds like your home environment is affecting your work concentration.",
    ),
    Translation(
        "I feel so tired all the time, even when I get enough sleep.",
        "You're getting sleep, yet it doesn't seem to alleviate your tiredness. That must be frustrating.",
    ),
]

question_examples = [
    Translation("Hey", "How's it going?"),
    Translation("Hey", "How can I help?"),
    Translation("Hi", "How are you today?"),
    Translation(
        "Good. I'm OK—not quite ready to go yet.",
        "What sort of practice have you been doing?",
    ),
    Translation(
        "I keep trying what you said, but I can’t improve my time in the freestyle.",
        "What would be the ideal outcome here? What are you shooting for?",
    ),
    Translation("Yeah.", "How are you doing?"),
]

TOOLS = [get_listening_statement, get_open_question, get_affirmation, get_greeting]
