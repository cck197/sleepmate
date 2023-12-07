import logging
from typing import Optional

from bson import ObjectId
from langchain.pydantic_v1 import BaseModel, Field

from .db import MONGODB_NAME, db, get_collection_names
from .structured import pydantic_to_mongoengine

log = logging.getLogger(__name__)


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
        db_user = DBUser(name=name, username=username, email=email)
        db_user.save()
        log.info(f"get_user_from_username creating {username=} {db_user.id=}")
    return db_user


def clear_db_for_user(db_user_id, skip=None):
    """Clear the database for a user."""
    if skip is None:
        skip = ["user"]
    key_map = {"message_store": "SessionId"}
    id_ = ObjectId(db_user_id)
    db_ = db.get_database(MONGODB_NAME)
    collection_names = get_collection_names(db_)
    log.info(f"clear_db_for_user deleting {db_user_id=}")
    for name in collection_names:
        if name in skip:
            continue
        collection = db_.get_collection(name)
        if name == "user":
            collection.delete_one({"_id": id_})
        else:
            collection.delete_many({key_map.get(name, "user"): id_})
