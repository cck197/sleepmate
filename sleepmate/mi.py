import json
from dataclasses import asdict, dataclass

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage

model_name = "gpt-4"

SYSTEM_DESCRIPTION = "You are a clinician skilled in Motivational Interviewing."


@dataclass
class Translation:
    input: str
    output: str


def get_completion(
    utterance: str, template: ChatPromptTemplate, model_name=model_name
) -> str:
    llm = ChatOpenAI(model_name=model_name)
    return llm(template.format_messages(text=utterance)).content


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

affirmation_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                f"{SYSTEM_DESCRIPTION} "
                "Respond to the client text with an affirmation. "
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)


def get_affirmation(utterance: str, model_name=model_name) -> str:
    """Get an affirmation for utterance. Affirmation is less of a judgment, more
    of an appreciation of positive qualities and behaviors. It is more likely to
    lift motivation and inspire further achievement. Use this whenever the
    client talks about what they did with any positivity."""
    return get_completion(utterance, affirmation_template, model_name)


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


question_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                f"{SYSTEM_DESCRIPTION} "
                "Respond to the client text with an open question. "
                "In general, open questions begin with words like what, how, and why. "
                "It's critically important you keep it brief. Fewer words is better. "
                "Below are some examples in JSON format: "
                f"{json.dumps([asdict(t) for t in question_examples])}"
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)


def get_open_question(utterance: str, model_name=model_name) -> str:
    """Be brief, encourage people to say what they think and feel, and open the
    door to talking about change. Use this as a starting point for a
    conversation, or when the client makes a positive statement that you want to
    explore further. The input is a greeting, and the output is an open question."""
    return get_completion(utterance, question_template, model_name)


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

listening_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                f"{SYSTEM_DESCRIPTION} "
                "Translate the text from a client into a listening statement. "
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)


def get_listening_statement(utterance: str, model_name=model_name) -> str:
    """Hear what the client is saying, and respond with a listening statement
    (empathy) to motivate behaviour change. Use this whenever the client appears
    to be in distress. The input utterance should show signs of distress
    in the client, and the output is a listening statement."""
    return get_completion(utterance, listening_template, model_name)
