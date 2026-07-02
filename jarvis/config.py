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
