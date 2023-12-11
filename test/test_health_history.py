import logging

import pytest

from sleepmate.helpful_scripts import json_dumps
from sleepmate.history import get_last_health_history
from sleepmate.structured import get_objects_approximately_equal, get_text_correctness

from .helpful_scripts import get_X

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("user", "test_name")
class TestHealthHistory:
    def test_should_save_health_history(self, user, test_name):
        x = get_X(user, "health_history")
        assert x.goal.key == "health_history"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, mentions a health history "
            "questionnaire, ends with a question",
            llm_output,
        )
        assert result.correct
        x("sure")
        llm_output = x(
            """I'm a man, 
            born Feb 13 1976,
            software engineer by trade,
            work 7am to 6pm with breaks,
            non-smoker,
            drink some alcohol on the weekends,
            cyclist, surfer, lift weights,
            a typical day of eating is three eggs and sausages for breakfast, 
            salad and protein for lunch, meat and veg for dinner. 
            1g protein per lb of bodyweight,
            I supplement with creatine,
            I have some low back pain that often makes it hard to sleep,
            no family history of insomnia,
            no mental health conditions,
            no psychological treatment,
            live with family, three kids, in a house but sleep in a VW Eurovan,
            it's very rural and quiet,
            I'd like to sleep through the night, wake up feeling refreshed,
            getting enough daylight helped
            Ambien didn't help
            that's all"""
        )
        history = get_last_health_history(x, "")
        log.info(f"{history=}")
        check_object = {
            "date": "2023-04-06T00:00:00",
            "sex": "man",
            "date_of_birth": "1976-02-13T00:00:00",
            "occupation": "software engineer",
            "work_hours": "7am to 6pm with breaks",
            "smoking": "non-smoker",
            "alcohol": "some alcohol on the weekends",
            "physical_activity": "cyclist, surfer, lift weights",
            "diet": "three eggs and sausages for breakfast, salad and protein for lunch, meat and veg for dinner, 1g protein per lb of bodyweight",
            "medical_conditions": "some low back pain",
            "medications": "none",
            "supplements": "creatine",
            "family_history": "no family history of insomnia",
            "mental_health": "no mental health conditions",
            "psychological_treatment": "no psychological treatment",
            "living_with": "family, three kids",
            "residence_type": "house but sleep in a VW Eurovan",
            "noise_level": "very rural and quiet",
            "goal": "sleep through the night, wake up feeling refreshed",
            "helpful": "getting enough daylight",
            "unhelpful": "Ambien",
            "notes": "none",
        }
        assert get_objects_approximately_equal(
            json_dumps(check_object), history
        ).correct
