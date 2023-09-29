Feature: Connect with athlete
    As an athlete struggling with sleep,
    I want to connect with an expert
    So I can feel more energetic during the day and less worried at night

    Scenario Outline: Connect with the athlete
        Given I'm an athlete
        And I'm struggling with sleep

        When I say hi

        Then the agent should use listening statements, affirmations and open questions to make me feel heard

