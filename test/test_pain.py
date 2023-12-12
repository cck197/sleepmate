import logging
from datetime import datetime

import pytest

from sleepmate.helpful_scripts import json_loads
from sleepmate.history import DBHealthHistory
from sleepmate.pain import get_back_pain_seen
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestPain:
    @pytest.fixture(autouse=True)
    def history(self, user):
        DBHealthHistory(
            user=user,
            date=datetime.now(),
            sex="male",
            date_of_birth=datetime(1976, 2, 13),
            occupation="",
            work_hours="",
            smoking="",
            alcohol="",
            physical_activity="",
            diet="",
            medical_conditions="low back pain",
            medications="",
            supplements="",
            family_history="",
            mental_health="",
            psychological_treatment="",
            living_with="",
            residence_type="",
            noise_level="",
            goal="",
            helpful="",
            unhelpful="",
            notes="",
        ).save()

    def test_should_be_able_to_save_back_pain(self, user, test_name):
        x = get_X(user, "back_pain")
        assert x.goal.key == "back_pain"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, asks to talk about back pain",
            llm_output,
        )
        assert result.correct
        llm_output = x("sure")
        result = get_text_correctness(
            f"includes a numbered list of interventions for managing low back "
            "pain including the Big Three exercises",
            llm_output,
        )
        assert result.correct
        x("ok")
        pain_seen = json_loads(get_back_pain_seen(x, ""))
        log.info(f"{pain_seen=}")
        assert pain_seen["date"] is not None
