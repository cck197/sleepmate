import logging
import uuid

import pytest

from sleepmate.executor import X
from sleepmate.helpful_scripts import display_rich_markdown
from sleepmate.user import clear_db_for_user, get_user_from_username


@pytest.fixture(scope="class")
def user(unique_username, test_name, test_email):
    user = get_user_from_username(unique_username, name=test_name, email=test_email)
    yield user
    clear_db_for_user(user.id, skip=[])


@pytest.fixture(scope="class")
def x(user):
    return X(
        username=user.username,
        hello=None,
        display_func=display_rich_markdown,
        log_=logging.getLogger("sleepmate.executor"),
    )


@pytest.fixture(scope="class")
def unique_username():
    return f"user_{uuid.uuid4()}"


@pytest.fixture(scope="session")
def test_name():
    return "Sleepy"


@pytest.fixture(scope="session")
def test_email():
    return "chris@nourishbalancethrive.com"
