import logging

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.sleep50 import get_last_sleep50_entry
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestSleep50:
    def test_should_save_sleep50(self, user, test_name):
        x = get_X(user, "sleep50")
        assert x.goal.key == "sleep50"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions sleep questionnaire "
            "contains a question",
            llm_output,
        )
        assert result.correct
        for section in (
            "apnea",
            "insomnia",
            "narcolepsy",
            "restless legs",
            "circadian",
            "sleep walking",
            "nightmares",
            "factors",
            "impact",
        ):
            print(f"{section=}")
            x(f"the answer to the {section} section is 2")
        x("I rate my sleep as 5 and I sleep 6 hours from 10pm to 4am")
        x("that's right")
        sleep50 = json_loads(get_last_sleep50_entry(x, ""))
        log.info(f"{sleep50=}")
        date = sleep50.pop("date", None)
        assert date is not None
        check_object = {
            "sleep_apnea_1": 2,
            "sleep_apnea_2": 2,
            "sleep_apnea_3": 2,
            "sleep_apnea_4": 2,
            "sleep_apnea_5": 2,
            "sleep_apnea_6": 2,
            "sleep_apnea_7": 2,
            "sleep_apnea_8": 2,
            "insomnia_9": 2,
            "insomnia_10": 2,
            "insomnia_11": 2,
            "insomnia_12": 2,
            "insomnia_13": 2,
            "insomnia_14": 2,
            "insomnia_15": 2,
            "insomnia_16": 2,
            "narcolepsy_17": 2,
            "narcolepsy_18": 2,
            "narcolepsy_19": 2,
            "narcolepsy_20": 2,
            "narcolepsy_21": 2,
            "restless_legs_22": 2,
            "restless_legs_23": 2,
            "restless_legs_24": 2,
            "restless_legs_25": 2,
            "circadian_rhythm_26": 2,
            "circadian_rhythm_27": 2,
            "circadian_rhythm_28": 2,
            "sleepwalking_29": 2,
            "sleepwalking_30": 2,
            "sleepwalking_31": 2,
            "nightmares_32": 2,
            "nightmares_33": 2,
            "nightmares_34": 2,
            "nightmares_35": 2,
            "nightmares_36": 2,
            "factors_37": 2,
            "factors_38": 2,
            "factors_39": 2,
            "factors_40": 2,
            "factors_41": 2,
            "factors_42": 2,
            "factors_43": 2,
            "impact_44": 2,
            "impact_45": 2,
            "impact_46": 2,
            "impact_47": 2,
            "impact_48": 2,
            "impact_49": 2,
            "impact_50": 2,
            "additional_a": 5,
            "additional_b": 6,
        }
        assert sleep50 == check_object
