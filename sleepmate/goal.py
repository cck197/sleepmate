from datetime import datetime

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .helpful_scripts import get_date_fields, get_start_end, parse_date
from .structured import fix_schema, pydantic_to_mongoengine
from .user import DBUser, get_current_user


class GoalRefusal_(BaseModel):
    date: datetime = Field(description="date of refusal")
    goal: str = Field(description="goal refused")


date_fields = get_date_fields(GoalRefusal_)


class GoalRefusal(GoalRefusal_):
    @classmethod
    def schema(cls):
        return fix_schema(GoalRefusal_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value)


DBGoalRefusal = pydantic_to_mongoengine(
    GoalRefusal, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def goal_refused(goal: str, start=None, end=None) -> DBGoalRefusal:
    if start is None or end is None:
        (start_, end_) = get_start_end()
        if start is None:
            start = start_
        if end is None:
            end = end_
    return DBGoalRefusal.objects(
        goal=goal, user=get_current_user(), date__gte=start, date__lte=end
    ).first()


def set_goal_refused(goal: str) -> DBGoalRefusal:
    return DBGoalRefusal(
        **{"user": get_current_user(), "goal": goal, "date": datetime.now()}
    ).save()
