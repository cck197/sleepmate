import pytest

from sleepmate.structured import get_text_correctness


@pytest.fixture
def llm_output():
    return (
        "Hello Dave,\n\nI hope you're finding a moment to recharge "
        "in the midst of your busy schedule. I was wondering if you "
        "might have a wearable device that you'd like to integrate "
        "for a more objective look at your health data. Here's a "
        "list of devices we can work with:\n\n- WHOOP Strap\n- "
        "Fitbit Devices (e.g., Fitbit Charge, Fitbit Versa, Fitbit "
        "Sense)\n- Apple Watch\n- Garmin Wearables (e.g., Garmin "
        "Vivosmart, Garmin Fenix)\n- Samsung Galaxy Watch\n- Oura "
        "Ring\n- Xiaomi Mi Band\n- Polar Watches (e.g., Polar Vantage,"
        " Polar Ignite)\n- Withings Sleep Tracking Mat\n- Amazfit "
        "Smartwatches\n- Other (please specify)\n- None of the above "
        "(skip)\n\nDo you have any of these devices, or perhaps a "
        "different one you're using?"
    )


def test_should_be_able_to_check_incorrect_llm_output(llm_output):
    result = get_text_correctness(
        "greet a person by name, contains a bullet list of cities, ends with question",
        llm_output,
    )
    assert result.correct == False


def test_should_be_able_to_check_correct_llm_output(llm_output):
    result = get_text_correctness(
        "greet a person by name, contains a bullet list wearable"
        " health tracking devices, ends with question",
        llm_output,
    )
    assert result.correct
