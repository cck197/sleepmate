from pytest_bdd import given, scenarios, then, when

scenarios("../features/connect.feature")


@given("I'm an athlete")
@given("I'm struggling with sleep")
def test_connect():
    pass


@when("I say hi")
def test_say_hi(rails):
    new_message = rails.generate(messages=[{"role": "user", "content": "hi"}])
    print(new_message)
    assert new_message["role"] == "assistant"
    assert new_message["content"] == "Hey there!\nHow are you doing today?"


@then(
    "the agent should use listening statements, affirmations and open questions to make me feel heard"
)
def test_feel_heard():
    pass
