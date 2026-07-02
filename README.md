# JARVIS

Ein lokaler, sprachgesteuerter persönlicher Assistent. Läuft auf deinem PC/Mac,
nutzt die Claude API als "Gehirn" und kann über Home Assistant Smart-Home-Geräte
steuern.

## Funktionsweise

1. Du drückst Enter und sprichst deinen Befehl.
2. Die Sprache wird lokal per Mikrofon aufgenommen und über die
   Google-Spracherkennung in Text umgewandelt.
3. Der Text geht an Claude, das bei Bedarf Tools aufruft (z.B. Licht
   einschalten, Gerätestatus abfragen).
4. Die Antwort wird laut vorgelesen (offline, per `pyttsx3`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`PyAudio` benötigt auf manchen Systemen zusätzlich PortAudio:

- macOS: `brew install portaudio`
- Debian/Ubuntu: `sudo apt install portaudio19-dev python3-pyaudio`

Danach die Konfiguration anlegen:

```bash
cp .env.example .env
```

Und in `.env` eintragen:

- `ANTHROPIC_API_KEY` – dein Claude-API-Key (erforderlich)
- `HOME_ASSISTANT_URL` / `HOME_ASSISTANT_TOKEN` – nur nötig, wenn du
  Smart-Home-Geräte steuern willst (Long-Lived Access Token aus deinem
  Home-Assistant-Profil)

## Starten

```bash
python main.py
```

## Projektstruktur

```
jarvis/
  config.py      # Lädt Umgebungsvariablen
  stt.py         # Spracherkennung (Mikrofon -> Text)
  tts.py         # Sprachausgabe (Text -> Sprache)
  tools.py       # Home-Assistant-Client + Tool-Definitionen für Claude
  assistant.py   # Konversationsschleife mit Claude, inkl. Tool-Use
main.py          # Einstiegspunkt (Push-to-Talk-Loop)
```

## Erweitern

Neue Fähigkeiten (z.B. Kalender, Timer, Web-Suche) lassen sich hinzufügen,
indem du in `jarvis/tools.py` eine neue Tool-Definition plus Ausführungslogik
ergänzt und sie in `execute_tool` verdrahtest.
