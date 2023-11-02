from bson import ObjectId
from mongoengine import connect

from .config import MONGODB_HOST, MONGODB_NAME, MONGODB_PORT

db = connect(db=MONGODB_NAME, host=MONGODB_HOST, port=MONGODB_PORT)


def get_collection_names(db_=None):
    if db_ is None:
        db_ = db.get_database(MONGODB_NAME)
    return [name for name in db_.list_collection_names()]


def clear_db_for_user(db_user_id, skip=None):
    """Clear the database for a user."""
    if skip is None:
        skip = ["user"]
    key_map = {"message_store": "SessionId"}
    id_ = ObjectId(db_user_id)
    db_ = db.get_database(MONGODB_NAME)
    collection_names = get_collection_names(db_)
    for name in collection_names:
        if name not in skip:
            db_.get_collection(name).delete_many({key_map.get(name, "user"): id_})


def clear_db(collection_names=None):
    """Clear the database."""
    db_ = db.get_database(MONGODB_NAME)
    if collection_names is None:
        collection_names = get_collection_names(db_)
    [db_.drop_collection(name) for name in collection_names]
