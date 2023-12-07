import pytest

from sleepmate.structured import get_text_correctness


@pytest.mark.usefixtures("x", "test_name")
class TestWearable:
    @pytest.mark.dependency()
    def test_should_greet_new_user_with_wearable_question(self, x, test_name):
        assert x.get_next_goal().key == "wearable_probe"
        llm_output = x("hey")
        result = get_text_correctness(
            f"greet {test_name} by name, contains a bullet list of wearable "
            "health tracking devices",
            llm_output,
        )
        assert result.correct

    @pytest.mark.dependency(
        depends=["TestWearable::test_should_greet_new_user_with_wearable_question"]
    )
    def test_should_skip_correctly(self, x):
        llm_output = x("none of the above")
        assert llm_output
