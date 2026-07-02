import argparse

from jarvis import config
from jarvis.assistant import Assistant
from jarvis.stt import SpeechToText
from jarvis.tts import TextToSpeech
from jarvis.wake_word import WakeWordListener


def run_push_to_talk(assistant: Assistant, stt: SpeechToText, tts: TextToSpeech) -> None:
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

        handle_command(assistant, tts, text)


def run_wake_word(assistant: Assistant, stt: SpeechToText, tts: TextToSpeech) -> None:
    listener = WakeWordListener(stt, config.WAKE_WORD)
    print(f"Jarvis hört zu. Sag '{config.WAKE_WORD}', gefolgt von deinem Befehl (Strg+C zum Beenden).")
    while True:
        try:
            text = listener.wait_for_command()
        except (KeyboardInterrupt, EOFError):
            print("\nBis bald!")
            break

        if not text:
            print("Nichts verstanden, versuch's nochmal.")
            continue

        handle_command(assistant, tts, text)


def handle_command(assistant: Assistant, tts: TextToSpeech, text: str) -> None:
    print(f"Du: {text}")
    reply = assistant.ask(text)
    print(f"Jarvis: {reply}")
    tts.say(reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis - persönlicher Sprachassistent")
    parser.add_argument(
        "--mode",
        choices=["ptt", "wake"],
        default="ptt",
        help="'ptt' = Enter drücken und sprechen (Standard), 'wake' = dauerhaft auf Aktivierungswort hören",
    )
    args = parser.parse_args()

    if not config.ANTHROPIC_API_KEY:
        raise SystemExit(
            "ANTHROPIC_API_KEY ist nicht gesetzt. Bitte .env anhand von .env.example anlegen."
        )

    stt = SpeechToText()
    tts = TextToSpeech()

    def on_alarm(message: str) -> None:
        print(f"\n⏰ {message}")
        tts.say(message)

    assistant = Assistant(on_alarm=on_alarm)

    if args.mode == "wake":
        run_wake_word(assistant, stt, tts)
    else:
        run_push_to_talk(assistant, stt, tts)


if __name__ == "__main__":
    main()
