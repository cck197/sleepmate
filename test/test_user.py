import pytest


@pytest.mark.usefixtures("user", "unique_username", "test_name", "test_email")
class TestUser:
    def test_should_be_able_create_user(
        self, user, unique_username, test_name, test_email
    ):
        assert user is not None
        assert user.username == unique_username
        assert user.name == test_name
        assert user.email == test_email
