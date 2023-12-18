import logging

import pytest

from sleepmate.diary import get_last_sleep_diary_entry
from sleepmate.helpful_scripts import json_loads
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestSleepDiary:
    def test_should_record_sleep_diary_entry(self, user, test_name):
        x = get_X(user, "diary_entry")
        assert x.goal.key == "diary_entry"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks about a sleep diary entry",
            llm_output,
        )
        assert result.correct
        x(
            """sure, went to bed at 9:15, try to fall asleep at 9:15, fell
            asleep at 9:20, woke up once, don't know what time, awake for 20
            mins, final wake up 6:45 got up right away no meds, sleep was good,
            had some bad dreams"""
        )
        x("yes, that's right")
        x("correct")
        diary_entry = json_loads(get_last_sleep_diary_entry(x, ""))
        log.info(f"{diary_entry=}")
        date = diary_entry.pop("date")
        assert date is not None
        assert (
            diary_entry["sleep_efficiency"] >= 94
            and diary_entry["sleep_efficiency"] <= 96
        )
