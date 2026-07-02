import threading
from typing import Callable


class TimerManager:
    """Verwaltet einfache Countdown-Timer und ruft bei Ablauf einen Callback auf."""

    def __init__(self, on_alarm: Callable[[str], None]):
        self._on_alarm = on_alarm
        self._lock = threading.Lock()
        self._timers: dict[str, threading.Timer] = {}

    def set_timer(self, seconds: float, label: str = "Timer") -> str:
        with self._lock:
            existing = self._timers.get(label)
            if existing is not None:
                existing.cancel()

            timer = threading.Timer(seconds, self._fire, args=(label,))
            timer.daemon = True
            self._timers[label] = timer
            timer.start()

        minutes = seconds / 60
        if minutes >= 1:
            return f"Timer '{label}' gestellt: {minutes:.1f} Minuten."
        return f"Timer '{label}' gestellt: {seconds:.0f} Sekunden."

    def _fire(self, label: str) -> None:
        with self._lock:
            self._timers.pop(label, None)
        self._on_alarm(f"Timer '{label}' ist abgelaufen.")

    def cancel_timer(self, label: str) -> str:
        with self._lock:
            timer = self._timers.pop(label, None)
        if timer is None:
            return f"Kein laufender Timer namens '{label}' gefunden."
        timer.cancel()
        return f"Timer '{label}' abgebrochen."
