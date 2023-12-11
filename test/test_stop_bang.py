from datetime import datetime

import pytest

from sleepmate.bmi import DBBodyMeasures
from sleepmate.helpful_scripts import json_loads
from sleepmate.history import DBHealthHistory
from sleepmate.stopbang import calculate_stop_bang, get_last_stop_bang
from sleepmate.structured import get_text_correctness

from .helpful_scripts import get_X


@pytest.fixture(scope="class")
def x(user):
    x = get_X(user, "stop_bang")
    DBHealthHistory(
        user=x.db_user_id,
        date=datetime.now(),
        sex="male",
        date_of_birth=datetime(1976, 2, 13),
        occupation="",
        work_hours="",
        smoking="",
        alcohol="",
        physical_activity="",
        diet="",
        medical_conditions="hypertension",
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
    DBBodyMeasures(
        user=x.db_user_id, date=datetime.now(), height=1.75, weight=68.04
    ).save()
    return x


@pytest.mark.usefixtures("x", "test_name")
class TestStopBang:
    @pytest.mark.dependency()
    def test_should_save_stop_bang(self, x, test_name):
        assert x.goal.key == "stop_bang"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions a STOP-Bang Questionnaire "
            "and apnea contains a question",
            llm_output,
        )
        assert result.correct
        x(
            "I snore loudly, am tired during the day, I haven't been "
            "observed not breathing, my neck is 38cm"
        )
        x("that's right")
        stop_bang = json_loads(get_last_stop_bang(x, ""))
        score = calculate_stop_bang(x, "")
        print(f"{stop_bang=}")
        date = stop_bang.pop("date")
        assert date is not None
        check_object = {
            "snoring": True,
            "tired": True,
            "observed": False,
            "neck": 38.0,
        }
        assert stop_bang == check_object
        assert score == 4
