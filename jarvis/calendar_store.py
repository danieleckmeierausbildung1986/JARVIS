import json
from datetime import datetime

from jarvis import config


class CalendarStore:
    """Lokale, dateibasierte Terminverwaltung (kein externer Kalender-Account nötig)."""

    def __init__(self, path=config.CALENDAR_PATH):
        self.path = path

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text())
        except json.JSONDecodeError:
            return []

    def _save(self, events: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        events.sort(key=lambda e: e["when"])
        self.path.write_text(json.dumps(events, ensure_ascii=False, indent=2))

    def add_event(self, title: str, when_iso: str) -> str:
        try:
            when = datetime.fromisoformat(when_iso)
        except ValueError:
            return f"Ungültiges Datumsformat: '{when_iso}'. Erwartet wird ISO 8601, z.B. 2026-07-05T15:00."

        events = self._load()
        events.append({"title": title, "when": when.isoformat()})
        self._save(events)
        return f"Termin '{title}' am {when.strftime('%d.%m.%Y um %H:%M')} Uhr gespeichert."

    def list_events(self, date: str | None = None) -> str:
        events = self._load()

        if date:
            events = [e for e in events if e["when"].startswith(date)]
        else:
            now = datetime.now().isoformat()
            events = [e for e in events if e["when"] >= now]

        if not events:
            return "Keine Termine gefunden."

        lines = []
        for event in events:
            when = datetime.fromisoformat(event["when"])
            lines.append(f"{when.strftime('%d.%m.%Y %H:%M')} Uhr: {event['title']}")
        return "; ".join(lines)
