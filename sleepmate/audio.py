import os

from elevenlabs import Voice, generate
from elevenlabs import play as eleven_play

from .config import ELEVEN_VOICE_ID


def play(utterance: str) -> None:
    audio = generate(text=utterance, voice=Voice.from_id(ELEVEN_VOICE_ID))
    eleven_play(audio)
