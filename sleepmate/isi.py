ISI_GOAL_PROMPTS = [
    """
    Your goal is to survey the human for their Insomnia Severity Index (ISI)
    using the standard 7-item questionnaire. Ask if now would be a good time
    then the following questions:
    
    1. Difficulty falling asleep.
    2. Difficulty staying asleep.
    3. Problems waking up too early.
    4. How satisfied/dissatisfied are you with your current sleep pattern?
    5. How noticeable to others do you think your sleep problem is in terms of
    impairing the quality of your life?
    6. How worried/distressed are you about your current sleep problem?
    7. To what extent do you consider your sleep problem to interfere with your
    daily functioning (e.g., daytime fatigue, ability to function at work/daily
    chores, concentration, memory, mood, etc.)?

    Be sure to ask the questions with their corresponding labels as shown below.
    
    Questions 1-3 are rated on a 5-point scale from 0 to 4:
    0: None
    1: Mild
    2: Moderate
    3: Severe
    4: Very severe

    Question 4 is rated on a 5-point scale from 0 to 4:
    0: Very satisfied
    1: Satisfied
    2: Moderately satisfied
    3: Dissatisfied
    4: Very dissatisfied

    Questions 5-7 are rated on a 5-point scale from 0 to 4:
    0: Not at all
    1: A little bit
    2: Moderately
    3: Quite a bit
    4: Very much

    When you've got the answer to all seven questions, summarise and ask if
    they're correct. Then add them up and report the total, which should be
    between 0 and 28. Add the following interpretation:
    0-7: No clinically significant insomnia
    8-14: Subthreshold insomnia
    15-21: Clinical insomnia (moderate severity)
    22-28: Clinical insomnia (severe)
    """
]

TOOLS = []
