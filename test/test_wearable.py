import json

import pytest

from sleepmate.structured import get_text_correctness
from sleepmate.wearable import get_wearables

from .helpful_scripts import get_X


@pytest.fixture(scope="class")
def x(user):
    return get_X(user, "wearable_probe")


@pytest.mark.usefixtures("x", "test_name")
class TestWearable:
    @pytest.mark.dependency()
    def test_should_greet_new_user_with_wearable_question(self, x, test_name):
        assert x.goal.key == "wearable_probe"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, contains a bullet list of wearable "
            "health tracking devices",
            llm_output,
        )
        assert result.correct


@pytest.mark.usefixtures("x")
class TestWearableSkip:
    def test_should_skip_correctly(self, x):
        x("hey")
        x("none of the above")
        wearables = json.loads(get_wearables(x, ""))
        print(wearables)
        for val in wearables.values():
            if isinstance(val, bool):
                assert not val


class TestWearableWhoop:
    def test_should_be_able_to_add_whoop(self, x):
        x("hey")
        x("I have a WHOOP strap")
        wearables = json.loads(get_wearables(x, ""))
        whoop = wearables.pop("whoop")
        assert whoop
        for val in wearables.values():
            if isinstance(val, bool):
                assert not val
