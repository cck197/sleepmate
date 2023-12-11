import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.knowledge import get_daily_routine_seen
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X


@pytest.fixture(scope="class")
def x(user):
    x = get_X(user, "daily_routine")
    return x


@pytest.mark.usefixtures("x", "test_name")
class TestDailyRoutine:
    @pytest.mark.dependency()
    def test_should_show_daily_routine(self, x, test_name):
        assert x.goal.key == "daily_routine"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks about a daily routine",
            llm_output,
        )
        assert result.correct
        x("sure")
        daily_routine = json_loads(get_daily_routine_seen(x, ""))
        print(f"{daily_routine=}")
        date = daily_routine.pop("date")
        assert date is not None
