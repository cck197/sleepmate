import logging
from datetime import datetime

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.nightmare import get_nightmare_seen
from sleepmate.sleep50 import DBSleep50Entry
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestNightmares:
    @pytest.fixture(autouse=True)
    def sleep50(self):
        DBSleep50Entry(
            user=x.db_user_id,
            date=datetime.now(),
            sleep_apnea_1=1,
            sleep_apnea_2=1,
            sleep_apnea_3=1,
            sleep_apnea_4=1,
            sleep_apnea_5=1,
            sleep_apnea_6=1,
            sleep_apnea_7=1,
            sleep_apnea_8=1,
            insomnia_9=1,
            insomnia_10=1,
            insomnia_11=1,
            insomnia_12=1,
            insomnia_13=1,
            insomnia_14=1,
            insomnia_15=1,
            insomnia_16=1,
            narcolepsy_17=1,
            narcolepsy_18=1,
            narcolepsy_19=1,
            narcolepsy_20=1,
            narcolepsy_21=1,
            restless_legs_22=1,
            restless_legs_23=1,
            restless_legs_24=1,
            restless_legs_25=1,
            circadian_rhythm_26=1,
            circadian_rhythm_27=1,
            circadian_rhythm_28=1,
            sleepwalking_29=1,
            sleepwalking_30=1,
            sleepwalking_31=1,
            nightmares_32=2,  # Have frightening dreams
            nightmares_33=2,  # Wake up from these dreams
            nightmares_34=2,  # Remember the content of these dreams
            nightmares_35=2,  # Can orientate quickly after these dreams
            nightmares_36=2,  # Have physical symptoms during or after these dreams
            factors_37=1,
            factors_38=1,
            factors_39=1,
            factors_40=1,
            factors_41=1,
            factors_42=1,
            factors_43=1,
            impact_44=1,
            impact_45=1,
            impact_46=1,
            impact_47=1,
            impact_48=1,
            impact_49=1,
            impact_50=1,
            additional_a=1,
            additional_b=1,
        ).save()

    def test_should_show_nightmare_intervention(self, user, test_name):
        x = get_X(user, "nightmare")
        assert x.goal.key == "nightmare"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks about nightmares contains a question",
            llm_output,
        )
        assert result.correct
        x("sure, I've been having bad dreams since I was a child")
        x(
            "sure, I woke up from a dream with anxious fears "
            "of a friend or myself having cancer"
        )
        x(
            "maybe the diagnosis was a mistake, and the "
            "problem wasn't cancer after all"
        )
        x("no that's it, sounds good")
        nightmares = json_loads(get_nightmare_seen(x, ""))
        log.info(f"{nightmares=}")
        date = nightmares.pop("date")
        assert date is not None
