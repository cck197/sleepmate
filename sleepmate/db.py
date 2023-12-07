import logging

from mongoengine import connect

from .config import MONGODB_NAME, MONGODB_URI

db = connect(host=MONGODB_URI)

log = logging.getLogger(__name__)


def get_collection_names(db_=None):
    if db_ is None:
        db_ = db.get_database(MONGODB_NAME)
    return [name for name in db_.list_collection_names()]


def clear_db(collection_names=None):
    """Clear the database."""
    db_ = db.get_database(MONGODB_NAME)
    if collection_names is None:
        collection_names = get_collection_names(db_)
    [db_.drop_collection(name) for name in collection_names]
