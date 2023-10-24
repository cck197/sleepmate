from datetime import datetime
from typing import List

from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .goal import goal_refused
from .helpful_scripts import Goal, get_date_fields, mongo_to_json, set_attribute
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

######################################################################
# StressAudit - a record of a stress audit
######################################################################


class StressAudit_(BaseModel):
    date: datetime = Field(description="date of entry")
    behaviours: List[str] = Field(description="behaviours")


date_fields = get_date_fields(StressAudit_)


class StressAudit(StressAudit_):
    @classmethod
    def schema(cls):
        return fix_schema(StressAudit_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, _):
        return datetime.now()


DBStressAudit = pydantic_to_mongoengine(
    StressAudit, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_stress_audit_from_memory(memory: BaseMemory) -> StressAudit:
    return get_parsed_output("summarise the stress audit", memory, StressAudit)


def save_stress_audit_to_db(user: str, entry: StressAudit) -> DBStressAudit:
    return DBStressAudit(**{"user": user, **entry.dict()}).save()


def get_json_stress_audit(entry: dict) -> str:
    """Returns the Stress Audit in JSON format"""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_stress_audit(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Saves Stress Audit to the database. Call *only* after all the Stress
    Audit questions have been answered."""
    entry = get_stress_audit_from_memory(memory)
    if entry is not None:
        print(f"save_stress_audit {entry=}")
        save_stress_audit_to_db(db_user_id, entry)


def get_current_stress_audit(db_user_id: str) -> DBStressAudit:
    """Returns current Stress Audit."""
    return DBStressAudit.objects(user=db_user_id).order_by("-id").first()


@set_attribute("return_direct", False)
def get_stress_audit(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Returns Stress Audit from the database."""
    entry = get_current_stress_audit(db_user_id)
    print(f"get_stress_audit {entry=}")
    if entry is not None:
        return get_json_stress_audit(entry.to_mongo().to_dict())


def stress_audit(db_user_id: str) -> bool:
    return (
        not goal_refused(db_user_id, "stress_audit")
        and DBStressAudit.objects(user=db_user_id).count() == 0
    )


GOAL_HANDLERS = [
    {
        "stress_audit": stress_audit,
    },
]

GOALS = [
    {
        "stress_audit": """
        Your goal is to help the human conduct a stress audit. created by Simon
        Marshall, PhD. Summarise the exercise described below.

        Coping is the purposeful ability to manage SENSATIONS, PERCEPTIONS,
        EMOTIONS, THOUGHTS & ACTIONS in response to your body's hard-wired
        neurochemical pathways (the "stress response") to DEMANDS placed on it.

        Resilience is the ability to cope positively ("adaptively") and
        consistently, regardless of the severity of the stress response.

        The Stress Audit is a tool to help you identify what you are currently
        doing when you're feeling stressed. List as many behaviours as you can.
        Once you're done we'll categorise them into the following categories:
        
        - Problem or solution-focused coping (behaviours that reduce the
        stressor itself)
        - Emotion-focused coping (behaviours that reduce the emotional impact of
        the stressor)

        We can further categorise these behaviours into the following categories:
        - Adaptive (behaviours that are helpful)
        - Maladaptive (behaviours that are unhelpful)
        
        Examples (E=Emotion-focused, P=Problem-focused, A=Adaptive, M=Maladaptive):
        - Working longer, working harder (esp. doing more research to feel
        prepared) (P, A)
        - Diarizing (also for time management) (P, A)
        - Drink more coffee (E, M) (P, M)
        - Tinkering - getting very detail oriented. (E, M) (P, M)
        - Exercising (e.g. Swimming, Biking, Running) (E, A) (P, A)
        - Asking for help/seeking assistance (P, A)
        - Seeking out information, education (P, A)
        - Using logic to avoid over exaggerating stressor (P, A)
        - Problem solving and selecting solutions (P, A)
        - Prioritizing and Segmenting (P, A)
        - Identifying controllable actions (P, A)
        - Assertiveness and communication skills (P, A)
        - Moaning, complaining, talking out loud. (esp. Brooding - taking on
        more but them complaining how unfair it is) (E, M)
        - Cleaning, Tidying (E, A)
        - Buying things on Amazon, mostly functional/easily justifiable (E, M) (E, A) 
        - Procrastinating (e.g., false prioritizing) (E, M)
        - Listening to rain on Spotify or YouTube (E, A)
        - Chimp purging (E, A)
        - Watching TV, especially the Olympic Channel (E, M)
        - Watching YouTube videos/TikTok (E, M)
        - Reading the news (BBC app, NYT) (E, M)
        - Drinking alcohol (E, M)
        - Eating simple carbohydrates (E, M)
        - Socializing with friends (E, A)
        - Having sex or masturbating (E, A)
        - Taking THC (E, A)
        - Playing the piano (E, A)
        - Going down Facebook/Twitter/YouTube rabbit holes (E, M)
        - Using humor and jokes (E, A)
        - Physiologic Sigh Breathing (E, A)
        - Progress Muscle Relaxation (E, A)

        As you can see from the examples, some behaviours can be both problem
        and emotion-focused.

        Once you've written down as many behaviours as you can, categorise them
        as either problem or emotion focused, and adaptive or maladaptive. What
        most people find is that there's an imbalance in the list, where people
        tend to over rely on one of the two categories. Often, women tend more
        towards emotion-based coping and men problem-based. Or as women often
        say, and men don't understand, "I don't need you to fix my problems, I
        just want you to listen to them."

        Resilient humans, those who perform well consistently tend to have a
        balanced list. They make use of BOTH problem and emotion-focused coping
        behaviours. They also tend to have more adaptive behaviours than
        maladaptive.

        Explain the purpose of the exercise, and walk the human through it, step
        by step. Once they are done listing stress-coping behaviours, categorise
        and summarise them. Ask if they're correct.

        If there's an imbalance in the list, ask if they can think of anything
        that might help balance the list. Give examples. 
        
        Only after they've confirmed, save the Stress Audit to the database.

        Explain you can help them try some new stress coping behaviours using
        the SEEDS exercise later.
        """
    }
]

TOOLS = [get_stress_audit, save_stress_audit]
