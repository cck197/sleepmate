from langchain.chat_models import ChatAnthropic, ChatOpenAI

from .config import SLEEPMATE_DEFAULT_MODEL_NAME, SLEEPMATE_SAMPLING_TEMPERATURE

MODELS = {
    "claude": ChatAnthropic(temperature=SLEEPMATE_SAMPLING_TEMPERATURE),
    "gpt": ChatOpenAI(
        model_name=SLEEPMATE_DEFAULT_MODEL_NAME,
        temperature=SLEEPMATE_SAMPLING_TEMPERATURE,
    ),
}
