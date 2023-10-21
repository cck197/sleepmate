from mongoengine import connect

from .config import (
    SLEEPMATE_MONGODB_HOST,
    SLEEPMATE_MONGODB_NAME,
    SLEEPMATE_MONGODB_PORT,
)

db = connect(
    db=SLEEPMATE_MONGODB_NAME, host=SLEEPMATE_MONGODB_HOST, port=SLEEPMATE_MONGODB_PORT
)
