import os

# MAX_TOKENS = 8192
SLEEPMATE_SAMPLING_TEMPERATURE = os.environ.get("SLEEPMATE_SAMPLING_TEMPERATURE", 0)
SLEEPMATE_MEMORY_PATH = os.environ.get("SLEEPMATE_MEMORY_PATH")
# unfortunately, gpt-3.5-turbo just won't cut it
SLEEPMATE_DEFAULT_MODEL_NAME = os.environ.get("SLEEPMATE_DEFAULT_MODEL_NAME", "gpt-4")
# for parsing output in memory to a JSON object
SLEEPMATE_PARSER_MODEL_NAME = os.environ.get("SLEEPMATE_PARSER_MODEL_NAME", "gpt-4")
# fine tuned for selecting a function
SLEEPMATE_AGENT_MODEL_NAME = os.environ.get("SLEEPMATE_AGENT_MODEL_NAME", "gpt-4-0613")
SLEEPMATE_DATADIR = os.environ.get("SLEEPMATE_DATADIR", "data")
SLEEPMATE_MAX_TOKENS = os.environ.get("SLEEPMATE_MAX_TOKENS", 8192)
DEBUG = os.environ.get("DEBUG", False)
if DEBUG:
    import langchain

    langchain.verbose = True  # langchain.debug = True

SLEEPMATE_SYSTEM_DESCRIPTION = """
You are a somewhat lighthearted AI clinician skilled in Motivational
Interviewing and Acceptance and Commitment Therapy. You make very sparing use of
British humour and the occasional self-deprecating joke. Your users are experts
in AI and ethics, so they already know you're a language model and your
capabilities and limitations, so don't remind them of that. They're familiar
with ethical issues in general so you don't need to remind them about those
either.
"""
