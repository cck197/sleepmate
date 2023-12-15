import os

# MAX_TOKENS = 8192
SLEEPMATE_SAMPLING_TEMPERATURE = float(
    os.environ.get("SLEEPMATE_SAMPLING_TEMPERATURE", 0.3)
)
# unfortunately, gpt-3.5-turbo just won't cut it
SLEEPMATE_DEFAULT_MODEL_NAME = os.environ.get(
    "SLEEPMATE_DEFAULT_MODEL_NAME", "gpt-4-1106-preview"
)
# for parsing output in memory to a JSON object
SLEEPMATE_PARSER_MODEL_NAME = os.environ.get(
    "SLEEPMATE_PARSER_MODEL_NAME", "gpt-4-1106-preview"
)
# fine tuned for selecting a function
SLEEPMATE_AGENT_MODEL_NAME = os.environ.get(
    "SLEEPMATE_AGENT_MODEL_NAME", "gpt-4-1106-preview"
)  # -0613")
SLEEPMATE_MEMORY_LENGTH = int(os.environ.get("SLEEPMATE_MEMORY_LENGTH", 30))
SLEEPMATE_DATADIR = os.environ.get("SLEEPMATE_DATADIR", "data")
SLEEPMATE_MAX_TOKENS = int(os.environ.get("SLEEPMATE_MAX_TOKENS", 8192))
DEBUG = os.environ.get("DEBUG", True)
SLEEPMATE_STOP_SEQUENCE = os.environ.get("SLEEPMATE_STOP_SEQUENCE", "###")
if DEBUG:
    import langchain

    langchain.verbose = True  # langchain.debug = True

MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
MONGODB_NAME = os.environ.get("MONGODB_NAME", "sleepmate")
MONGODB_PORT = os.environ.get("MONGODB_PORT", 27017)
MONGODB_URI = os.environ.get(
    "MONGODB_URI", f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_NAME}"
)

WHOOP_CLIENT_ID = os.environ.get("WHOOP_CLIENT_ID")
WHOOP_CLIENT_SECRET = os.environ.get("WHOOP_CLIENT_SECRET")
WHOOP_REDIRECT_URI = os.environ.get("WHOOP_REDIRECT_URI")
WHOOP_SCOPE = [
    "offline",
    "read:recovery",
    "read:cycles",
    "read:workout",
    "read:sleep",
    "read:profile",
    "read:body_measurement",
]

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

SLEEPMATE_DISCORD_CHANNEL_EXCLUDE = ["general"]

PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "sleepmate")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

DISCOURSE_USERNAME = os.environ.get("DISCOURSE_USERNAME", "sleepmate")
DISCOURSE_BASE_URL = os.environ.get(
    "DISCOURSE_BASE_URL", "https://forum.nourishbalancethrive.com"
)
DISCOURSE_API_KEY = os.environ.get("DISCOURSE_API_KEY")

ELEVEN_VOICE_ID = os.environ.get("ELEVEN_VOICE_ID")

SLEEPMATE_CONFIRMATION_WORDS = [
    "k",
    "okay",
    "ok",
    "yes",
    "y",
    "sure",
    "yeah",
    "yep",
    "ready",
]

# seconds
SLEEPMATE_NUDGE_TIME = 60 * 5
# SLEEPMATE_NUDGE_TIME = 10

# Simon pointed out that  in the future, clients might have the option to choose
# the tone of responses from their coaches to better align with their
# motivational requirements. Some individuals may prefer a kind, supportive, and
# non-judgmental approach, while others might benefit from a straightforward,
# stern demeanor akin to a drill instructor's style. We might also switch styles
# based on compliance.

SLEEPMATE_SYSTEM_DESCRIPTION = """You are a somewhat lighthearted AI clinician
skilled in Motivational Interviewing and Acceptance and Commitment Therapy. You
make very sparing use of British humour and the occasional self-deprecating
joke. Your clients are experts in AI and ethics, so they already know you're a
language model and your capabilities and limitations, so don't remind them of
that. They're under medical supervision and familiar with ethical issues in
general so you don't need to remind them about those either."""
