GOAL_HANDLERS = [
    {"all_for_now": lambda db_user_id: True},
]


GOALS = [
    {
        "all_for_now": """Say the following delimited by triple backticks (but
        don't include the backticks in your output): ```That's all I have for
        now. Let me know if you have any questions, I'm happy to help.
        Otherwise, I'll reach out to check in with you later.```""",
    }
]

# GOAL_OPTIONS = [{"all_for_now": {"rigid": True}}]
