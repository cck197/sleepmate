import logging

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.isi import get_last_isi_entry
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestISI:
    def test_should_save_isi(self, user, test_name):
        x = get_X(user, "insomnia_severity_index")
        assert x.goal.key == "insomnia_severity_index"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions the Insomnia Severity Index "
            "questionnaire contains a question",
            llm_output,
        )
        assert result.correct
        x("yes, all the answers are 2")
        x("yep!")
        isi_entry = json_loads(get_last_isi_entry(x, ""))
        log.info(f"{isi_entry=}")
        date = isi_entry.pop("date", None)
        assert date is not None
        check_object = {
            "difficulty_falling_asleep": 2,
            "difficulty_staying_asleep": 2,
            "problems_waking_up_too_early": 2,
            "sleep_pattern_satisfaction": 2,
            "sleep_problem_noticeability": 2,
            "sleep_problem_worry": 2,
            "sleep_problem_interference": 2,
        }
        assert isi_entry == check_object
