import os

from elevenlabs import Voice, generate
from elevenlabs import play as eleven_play

VOICE_ID = os.environ["ELEVEN_VOICE_ID"]


def play(utterance: str) -> None:
    audio = generate(text=utterance, voice=Voice.from_id(VOICE_ID))
    eleven_play(audio)
