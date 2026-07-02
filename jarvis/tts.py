import asyncio
import os
import tempfile
import threading
from pathlib import Path

import edge_tts
from playsound import playsound

from jarvis import config


class TextToSpeech:
    """Sprachausgabe über Microsofts kostenlose Edge-TTS-Stimmen (klingt deutlich
    natürlicher als lokale Offline-TTS-Engines, braucht aber eine Internetverbindung)."""

    def __init__(self, voice: str = config.TTS_VOICE):
        self.voice = voice
        # Timer-/Aktienalarme können aus einem Hintergrund-Thread feuern, während die
        # Hauptschleife gerade spricht - der Lock verhindert überlappende Wiedergabe.
        self._lock = threading.Lock()

    def say(self, text: str) -> None:
        with self._lock:
            audio_path = self._synthesize(text)
            try:
                playsound(str(audio_path))
            finally:
                audio_path.unlink(missing_ok=True)

    def _synthesize(self, text: str) -> Path:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        audio_path = Path(path)
        asyncio.run(edge_tts.Communicate(text, self.voice).save(str(audio_path)))
        return audio_path
