import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

HOME_ASSISTANT_URL = os.environ.get("HOME_ASSISTANT_URL", "")
HOME_ASSISTANT_TOKEN = os.environ.get("HOME_ASSISTANT_TOKEN", "")

WAKE_WORD = os.environ.get("JARVIS_WAKE_WORD", "jarvis")

JARVIS_HOME = Path(os.environ.get("JARVIS_HOME", str(Path.home() / ".jarvis")))
HISTORY_PATH = JARVIS_HOME / "history.json"
CALENDAR_PATH = JARVIS_HOME / "calendar.json"
MAX_HISTORY_TURNS = int(os.environ.get("JARVIS_MAX_HISTORY_TURNS", "20"))

# Edge-TTS-Stimme (kostenlose Microsoft-Sprachstimmen). "de-DE-KillianNeural" ist eine
# ruhige, tiefe deutsche Männerstimme. Für den klassischen britischen "Film-Jarvis"-Klang
# könnte man z.B. "en-GB-RyanNeural" setzen - dann sollte aber auch der System-Prompt in
# assistant.py auf Englisch umgestellt werden, sonst spricht die Stimme Deutsch mit
# englischem Akzent aus.
TTS_VOICE = os.environ.get("JARVIS_TTS_VOICE", "de-DE-KillianNeural")

STOCK_POLL_SECONDS = int(os.environ.get("JARVIS_STOCK_POLL_SECONDS", "60"))
