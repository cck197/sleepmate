from typing import Optional

from langchain.pydantic_v1 import BaseModel, Field

from .structured import pydantic_to_mongoengine

######################################################################
# Basic User model
######################################################################


class User(BaseModel):
    name: Optional[str] = Field(description="name")
    email: Optional[str] = Field(description="email address")
    username: Optional[str] = Field(description="username")


DBUser = pydantic_to_mongoengine(User)


def get_user_from_email(email: str) -> DBUser:
    return DBUser.objects(email=email).first()


def get_user_from_id(db_user_id: str) -> DBUser:
    return DBUser.objects(id=db_user_id).first()


def get_user_from_username(
    username: str, name: str = None, email: str = None, create=True
) -> DBUser:
    db_user = DBUser.objects(username=username).first()
    if create and db_user is None:
        print(f"get_user_from_username creating {username=}")
        db_user = DBUser(name=name, username=username, email=email)
        db_user.save()
    return db_user
