from datetime import datetime, timedelta

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .helpful_scripts import Goal, get_date_fields, get_start_end, parse_date
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


def goal_refused(goal: str, days: int = 1) -> DBGoalRefusal:
    """Returns the last goal refusal for the given goal and user within the last
    `days` days."""
    kwargs = {"goal": goal, "user": get_current_user()}
    if days is not None:
        kwargs["date__gte"] = datetime.now() - timedelta(days=days)
    return DBGoalRefusal.objects(**kwargs).first()


def add_goal_refused(goal: str) -> DBGoalRefusal:
    return DBGoalRefusal(
        **{"user": get_current_user(), "goal": goal, "date": datetime.now()}
    ).save()
