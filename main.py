from jarvis import config
from jarvis.assistant import Assistant
from jarvis.stt import SpeechToText
from jarvis.tts import TextToSpeech


def main() -> None:
    if not config.ANTHROPIC_API_KEY:
        raise SystemExit(
            "ANTHROPIC_API_KEY ist nicht gesetzt. Bitte .env anhand von .env.example anlegen."
        )

    assistant = Assistant()
    stt = SpeechToText()
    tts = TextToSpeech()

    print("Jarvis ist bereit. Drücke Enter und sprich danach deinen Befehl (Strg+C zum Beenden).")

    while True:
        try:
            input("\n[Enter drücken, dann sprechen] ")
        except (KeyboardInterrupt, EOFError):
            print("\nBis bald!")
            break

        print("Höre zu...")
        text = stt.listen_and_transcribe()
        if not text:
            print("Nichts verstanden, versuch's nochmal.")
            continue

        print(f"Du: {text}")
        reply = assistant.ask(text)
        print(f"Jarvis: {reply}")
        tts.say(reply)


if __name__ == "__main__":
    main()
