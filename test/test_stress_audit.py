import logging

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.stress import get_stress_audit
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestStressAudit:
    def test_should_be_able_to_save_stress_audit(self, user, test_name):
        x = get_X(user, "stress_audit")
        assert x.goal.key == "stress_audit"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions the Stress Audit",
            llm_output,
        )
        assert result.correct
        x("sure, can you give some new examples?")
        x("I do the 10 listed above")
        x("yep!")
        stress_audit = json_loads(get_stress_audit(x, ""))
        log.info(f"{stress_audit=}")
        for val in stress_audit.values():
            assert len(val) > 5
