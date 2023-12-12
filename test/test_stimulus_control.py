import logging

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.stimulus import get_stimulus_control_seen
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestStimulus:
    def test_should_be_able_to_save_stimulus_control(self, user, test_name):
        x = get_X(user, "stimulus_control")
        assert x.goal.key == "stimulus_control"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks what activities they do in bed",
            llm_output,
        )
        assert result.correct
        x("sure, reading, watching tv, and playing games")
        llm_output = x("sure")
        result = get_text_correctness(
            "mentions getting out of bed if after unable to sleep for 20 minutes",
            llm_output,
        )
        assert result.correct
        x("ok")
        seen = json_loads(get_stimulus_control_seen(x, ""))
        log.info(f"{seen=}")
        assert seen["date"] is not None
