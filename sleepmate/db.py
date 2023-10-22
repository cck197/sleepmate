from mongoengine import connect

from .config import (
    SLEEPMATE_MONGODB_HOST,
    SLEEPMATE_MONGODB_NAME,
    SLEEPMATE_MONGODB_PORT,
)

db = connect(
    db=SLEEPMATE_MONGODB_NAME, host=SLEEPMATE_MONGODB_HOST, port=SLEEPMATE_MONGODB_PORT
)


def clear_db(collection_names=None):
    db_ = db.get_database(SLEEPMATE_MONGODB_NAME)
    if collection_names is None:
        collection_names = [
            name for name in db_.list_collection_names() if name != "user"
        ]
    [db_.drop_collection(name) for name in collection_names]
