from jarvis.stt import SpeechToText


class WakeWordListener:
    """Kontinuierliches Zuhören ohne externe Wake-Word-Engine.

    Nimmt kurze Sprachfetzen auf und prüft, ob sie mit dem Aktivierungswort
    beginnen. Falls ja, wird der Rest des Satzes als Befehl zurückgegeben
    (oder, falls leer, im Anschluss separat aufgenommen). Braucht keinen
    zusätzlichen API-Key, nutzt aber laufend die Spracherkennung und ist
    daher weniger sparsam als eine echte On-Device-Wake-Word-Engine.
    """

    def __init__(self, stt: SpeechToText, wake_word: str):
        self.stt = stt
        self.wake_word = wake_word.lower().strip()

    def wait_for_command(self) -> str | None:
        """Blockiert, bis das Aktivierungswort erkannt wurde, und gibt den
        anschließenden Befehl zurück (kann bei Bedarf erneut zuhören, falls
        nach dem Wake-Word noch nichts gesagt wurde)."""
        while True:
            text = self.stt.listen_and_transcribe()
            if not text:
                continue

            lowered = text.lower().strip()
            if not lowered.startswith(self.wake_word):
                continue

            command = text[len(self.wake_word):].strip(" ,.:!")
            if command:
                return command

            follow_up = self.stt.listen_and_transcribe()
            return follow_up
