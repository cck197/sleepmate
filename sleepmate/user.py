from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import BaseMemory

from .structured import get_parsed_output, pydantic_to_mongoengine


class User(BaseModel):
    name: str = Field(description="name")
    email: str = Field(description="email address")


DBUser = pydantic_to_mongoengine(User)


def get_user(memory: BaseMemory) -> User:
    return get_parsed_output("what are the human's details", memory, User)


def get_user_from_email(email: str) -> DBUser:
    db_user = DBUser.objects(email=email).first()
    return db_user if db_user is not None else get_current_user()


def get_current_user():  # TODO
    db_user = DBUser.objects.first()
    if db_user is None:
        db_user = DBUser(name="Chris", email="chris@nourishbalancethrive.com")
        db_user.save()
    return db_user
