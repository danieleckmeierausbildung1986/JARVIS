import threading

import pyttsx3


class TextToSpeech:
    """Offline text-to-speech using the system's speech engine."""

    def __init__(self, rate: int = 175, voice_hint: str | None = "de"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self._lock = threading.Lock()

        if voice_hint:
            for voice in self.engine.getProperty("voices"):
                if voice_hint.lower() in voice.id.lower() or voice_hint.lower() in voice.name.lower():
                    self.engine.setProperty("voice", voice.id)
                    break

    def say(self, text: str) -> None:
        # Timer-Alarme können aus einem Hintergrund-Thread feuern, während die
        # Hauptschleife gerade spricht - der Lock serialisiert den Zugriff auf
        # die pyttsx3-Engine, die selbst nicht thread-sicher ist.
        with self._lock:
            self.engine.say(text)
            self.engine.runAndWait()
