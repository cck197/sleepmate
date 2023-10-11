from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import BaseMemory
from mongoengine import Document, StringField

from .structured import get_parsed_output, pydantic_to_mongoengine


class User(BaseModel):
    name: str = Field(description="name")
    email: str = Field(description="email address")


DBUser = pydantic_to_mongoengine(User)


def get_user(memory: BaseMemory) -> User:
    return get_parsed_output("what are the human's details", memory, User)
