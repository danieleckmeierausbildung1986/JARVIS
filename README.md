# JARVIS

Ein lokaler, sprachgesteuerter persönlicher Assistent. Läuft auf deinem PC/Mac,
nutzt die Claude API als "Gehirn" und kann Smart-Home-Geräte steuern, Timer
stellen, das Wetter abfragen, Kalendertermine verwalten, Nachrichten vorlesen
und Aktienkurse abfragen/überwachen. Merkt sich Gespräche auch über einen
Neustart hinweg.

## Funktionsweise

1. Du aktivierst Jarvis entweder per Tastendruck oder per Aktivierungswort
   (siehe Modi unten) und sprichst deinen Befehl.
2. Die Sprache wird lokal per Mikrofon aufgenommen und über die
   Google-Spracherkennung in Text umgewandelt.
3. Der Text geht an Claude, das bei Bedarf Tools aufruft (Licht schalten,
   Timer stellen, Wetter/Nachrichten/Aktienkurse abfragen, Kalendertermine
   anlegen/lesen).
4. Die Antwort wird laut vorgelesen über Microsofts kostenlose Edge-TTS-Stimmen.
5. Der Gesprächsverlauf wird lokal gespeichert, damit sich Jarvis auch nach
   einem Neustart an frühere Unterhaltungen erinnert.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`PyAudio` benötigt auf manchen Systemen zusätzlich PortAudio:

- macOS: `brew install portaudio`
- Debian/Ubuntu: `sudo apt install portaudio19-dev python3-pyaudio`
- Windows: falls der Build fehlschlägt, "Desktop development with C++" über die
  [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  installieren

Danach die Konfiguration anlegen:

```bash
cp .env.example .env
```

Und in `.env` eintragen:

- `ANTHROPIC_API_KEY` – dein Claude-API-Key (erforderlich)
- `HOME_ASSISTANT_URL` / `HOME_ASSISTANT_TOKEN` – nur nötig, wenn du
  Smart-Home-Geräte steuern willst (Long-Lived Access Token aus deinem
  Home-Assistant-Profil)
- `JARVIS_WAKE_WORD` – Aktivierungswort für den Wake-Word-Modus (Standard: `jarvis`)
- `JARVIS_HOME` – Ordner für Gesprächsverlauf & Kalenderdaten (Standard: `~/.jarvis`)
- `JARVIS_MAX_HISTORY_TURNS` – wie viele Gesprächsrunden im Gedächtnis bleiben (Standard: `20`)
- `JARVIS_TTS_VOICE` – Edge-TTS-Stimme (Standard: `de-DE-KillianNeural`)
- `JARVIS_STOCK_POLL_SECONDS` – Abfrageintervall für Aktien-Beobachtungen (Standard: `60`)

Wetter-, Nachrichten- und Aktienabfragen nutzen kostenlose APIs ohne eigenen API-Key
(Open-Meteo, Tagesschau-RSS, Yahoo Finance).

## Starten

Push-to-talk (Enter drücken, dann sprechen):

```bash
python main.py
```

Wake-Word-Modus (dauerhaft zuhören, mit Aktivierungswort starten, z.B. "Jarvis, wie ist das Wetter"):

```bash
python main.py --mode wake
```

Hinweis: Der Wake-Word-Modus nutzt mangels lokaler On-Device-Engine
weiterhin die (kostenlose) Cloud-Spracherkennung im Dauerbetrieb – das
funktioniert gut als Prototyp, ist aber weniger sparsam als eine echte
On-Device-Wake-Word-Engine wie Porcupine.

## Beispielbefehle

- "Stell einen Timer über 10 Minuten für die Pasta"
- "Wie ist das Wetter in München?"
- "Was gibt es Neues in der Welt?" / "Lies mir die Nachrichten vor"
- "Wie steht die Apple-Aktie?"
- "Beobachte die Tesla-Aktie und sag Bescheid, wenn sie über 300 Dollar geht"
- "Leg einen Termin für morgen um 15 Uhr an: Zahnarzt"

## Projektstruktur

```
jarvis/
  config.py          # Lädt Umgebungsvariablen
  stt.py              # Spracherkennung (Mikrofon -> Text)
  tts.py              # Sprachausgabe über Edge-TTS, thread-sicher
  wake_word.py        # Kontinuierliches Zuhören + Aktivierungswort-Erkennung
  tools.py            # Tool-Definitionen für Claude + Dispatch
  timers.py           # Timer stellen/abbrechen
  weather.py          # Wetterabfrage via Open-Meteo
  news.py             # Nachrichten-Schlagzeilen via Tagesschau-RSS
  stocks.py           # Aktienkurse abfragen + Hintergrund-Überwachung mit Alarm
  calendar_store.py   # Lokale, dateibasierte Terminverwaltung
  assistant.py        # Konversationsschleife mit Claude, Tool-Use, Gedächtnis
main.py               # Einstiegspunkt (Push-to-talk / Wake-Word)
```

## Erweitern

Neue Fähigkeiten lassen sich hinzufügen, indem du in `jarvis/tools.py` eine
neue Tool-Definition plus Ausführungslogik ergänzt und sie in `execute_tool`
verdrahtest.
