import logging

import pytest

from sleepmate.act import get_last_exercise_entry, get_vlq_entry
from sleepmate.helpful_scripts import json_loads
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestExercise:
    @pytest.fixture
    def confirmations(self):
        return 7

    def test_should_perform_open_focus_exercise(
        self, user, test_name, exercise_name, confirmations
    ):
        x = get_X(user, exercise_name)
        assert x.goal.key == exercise_name
        verbose_name = exercise_name.replace("_", " ").title()
        log.info(f"{verbose_name=}, {confirmations=}")
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions the {verbose_name} exercise",
            llm_output,
        )
        assert result.correct
        for _ in range(confirmations):
            x("ok")
        x("better!")
        x("yep! that's right")
        exercise = json_loads(get_last_exercise_entry(x, ""))
        log.info(f"{exercise=}")
        date = exercise.pop("date")
        assert date is not None


class TestLeavesOnAStream(TestExercise):
    @pytest.fixture
    def confirmations(self):
        return 5

    @pytest.fixture
    def exercise_name(self):
        return "leaves_on_a_stream"


class TestOpenFocus(TestExercise):
    @pytest.fixture
    def exercise_name(self):
        return "open_focus"


@pytest.mark.usefixtures("user", "test_name")
class TestValuedLiving:
    def test_should_perform_valued_living_exercise(self, user, test_name):
        x = get_X(user, "valued_living")
        assert x.goal.key == "valued_living"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks the Valued Living questionnaire",
            llm_output,
        )
        assert result.correct
        x("the answers to all the questions in all the categories are: 10 and 10")
        x("yep! that's right")
        vlq = json_loads(get_vlq_entry(x, ""))
        print(f"{vlq=}")
        date = vlq.pop("date")
        assert date is not None
        check_object = {
            "family_relations": [10, 10],
            "marriage": [10, 10],
            "parenting": [10, 10],
            "friendships": [10, 10],
            "work": [10, 10],
            "education": [10, 10],
            "recreation": [10, 10],
            "spirituality": [10, 10],
            "citizenship": [10, 10],
            "physical_self_care": [10, 10],
            "environmental_issues": [10, 10],
            "art": [10, 10],
        }
        assert vlq == check_object
