import logging

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.seeds import get_seed_pod, get_seeds_diary_entry_score
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestSeeds:
    def test_should_be_able_to_save_seed_pod(self, user, test_name):
        x = get_X(user, "seeds_probe")
        assert x.goal.key == "seeds_probe"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions the SEEDS exercise",
            llm_output,
        )
        assert result.correct
        x("sure, can you give some new examples, three for each category?")
        x("that's great, let's go with all those exactly as you gave them")
        x("perfect")
        seed_pod = json_loads(get_seed_pod(x, ""))
        log.info(f"{seed_pod=}")
        for val in seed_pod.values():
            assert len(val) > 5

    def test_should_be_able_to_save_diary_entry(self, user, test_name):
        x = get_X(user, "seeds_entry")
        assert x.goal.key == "seeds_entry"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions a SEEDS diary entry",
            llm_output,
        )
        assert result.correct
        x("sure, I got all 15 tasks done")
        x("yep")
        score = get_seeds_diary_entry_score(x, "")
        assert score == 15
