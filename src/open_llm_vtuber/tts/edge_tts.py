import sys
import os
import time

import edge_tts
from loguru import logger
from .tts_interface import TTSInterface

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


# Check out doc at https://github.com/rany2/edge-tts
# Use `edge-tts --list-voices` to list all available voices


class TTSEngine(TTSInterface):
    MAX_ATTEMPTS = 3
    RETRY_DELAYS = (0.5, 1.0)

    def __init__(self, voice="en-US-AvaMultilingualNeural"):
        self.voice = voice

        self.temp_audio_file = "temp"
        self.file_extension = "mp3"
        self.new_audio_dir = "cache"

        if not os.path.exists(self.new_audio_dir):
            os.makedirs(self.new_audio_dir)

    def generate_audio(self, text, file_name_no_ext=None):
        """
        Generate speech audio file using TTS.
        text: str
            the text to speak
        file_name_no_ext: str
            name of the file without extension


        Returns:
        str: the path to the generated audio file

        """
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                if os.path.exists(file_name):
                    os.remove(file_name)

                communicate = edge_tts.Communicate(text, self.voice)
                communicate.save_sync(file_name)

                if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
                    raise RuntimeError("Edge TTS generated an empty audio file")

                return file_name
            except Exception as e:
                if os.path.exists(file_name):
                    try:
                        os.remove(file_name)
                    except OSError:
                        pass

                if attempt == self.MAX_ATTEMPTS:
                    logger.critical(
                        f"\nError: edge-tts unable to generate audio after "
                        f"{self.MAX_ATTEMPTS} attempts: {e}"
                    )
                    logger.critical(
                        "It's possible that edge-tts is blocked in your region."
                    )
                    return None

                delay = self.RETRY_DELAYS[attempt - 1]
                logger.warning(
                    f"Edge TTS attempt {attempt}/{self.MAX_ATTEMPTS} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)

        return None


# en-US-AvaMultilingualNeural
# en-US-EmmaMultilingualNeural
# en-US-JennyNeural
