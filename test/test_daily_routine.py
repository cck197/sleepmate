import logging

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.knowledge import get_daily_routine_seen
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestDailyRoutine:
    def test_should_show_daily_routine(self, user, test_name):
        x = get_X(user, "daily_routine")
        assert x.goal.key == "daily_routine"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks about a daily routine",
            llm_output,
        )
        assert result.correct
        x("sure")
        daily_routine = json_loads(get_daily_routine_seen(x, ""))
        log.info(f"{daily_routine=}")
        date = daily_routine.pop("date")
        assert date is not None
