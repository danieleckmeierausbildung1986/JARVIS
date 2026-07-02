import speech_recognition as sr


class SpeechToText:
    """Wraps SpeechRecognition for microphone capture + transcription."""

    def __init__(self, language: str = "de-DE"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = language
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

    def listen_and_transcribe(self) -> str | None:
        """Records one utterance from the microphone and returns the transcript,
        or None if nothing could be understood."""
        with self.microphone as source:
            audio = self.recognizer.listen(source)

        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            raise RuntimeError(f"Spracherkennungs-Dienst nicht erreichbar: {e}") from e
