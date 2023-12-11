import pytest

from sleepmate.bmi import get_last_body_measures
from sleepmate.helpful_scripts import json_dumps, json_loads
from sleepmate.structured import get_objects_approximately_equal, get_text_correctness

from .helpful_scripts import get_X


@pytest.fixture(scope="class")
def x(user):
    return get_X(user, "bmi")


@pytest.mark.usefixtures("x", "test_name")
class TestBMI:
    @pytest.mark.dependency()
    def test_should_save_body_measures(self, x, test_name):
        assert x.goal.key == "bmi"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions height and/or weight "
            "ends with a question",
            llm_output,
        )
        assert result.correct
        x("175cm and 68kg")
        bmi = json_loads(get_last_body_measures(x, ""))
        print(f"{bmi=}")
        date = bmi.pop("date", None)
        assert date is not None
        check_object = {"height": 1.75, "weight": 68.0}
        assert get_objects_approximately_equal(
            json_dumps(check_object), json_dumps(bmi)
        ).correct
