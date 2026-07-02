import threading
from typing import Callable

import requests

from jarvis import config

QUOTE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _fetch_price(symbol: str) -> tuple[float, str, str]:
    response = requests.get(
        QUOTE_URL.format(symbol=symbol),
        params={"interval": "1d", "range": "1d"},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    result = response.json().get("chart", {}).get("result")
    if not result:
        raise ValueError(f"Kein Kurs für '{symbol}' gefunden.")

    meta = result[0]["meta"]
    return meta["regularMarketPrice"], meta.get("currency", ""), meta.get("symbol", symbol)


def get_stock_price(symbol: str) -> str:
    try:
        price, currency, name = _fetch_price(symbol)
    except (ValueError, KeyError, requests.RequestException):
        return f"Ich konnte keinen Kurs für '{symbol}' finden."
    return f"{name} steht aktuell bei {price} {currency}."


class StockWatcher:
    """Überwacht periodisch einen Aktienkurs und meldet per Callback, wenn eine
    Ziel-Schwelle über- bzw. unterschritten wird."""

    def __init__(self, on_alert: Callable[[str], None], poll_seconds: float = config.STOCK_POLL_SECONDS):
        self._on_alert = on_alert
        self._poll_seconds = poll_seconds
        self._lock = threading.Lock()
        self._watches: dict[str, dict] = {}

    def watch(self, symbol: str, direction: str, target_price: float, label: str | None = None) -> str:
        label = label or symbol
        with self._lock:
            self._watches[label] = {
                "symbol": symbol,
                "direction": direction,
                "target_price": target_price,
            }
        self._schedule_check(label)
        richtung = "über" if direction == "above" else "unter"
        return f"Beobachte {symbol}: Alarm, wenn der Kurs {richtung} {target_price} geht."

    def cancel(self, label: str) -> str:
        with self._lock:
            existed = self._watches.pop(label, None) is not None
        return f"Beobachtung '{label}' beendet." if existed else f"Keine laufende Beobachtung namens '{label}' gefunden."

    def _schedule_check(self, label: str) -> None:
        timer = threading.Timer(self._poll_seconds, self._check, args=(label,))
        timer.daemon = True
        timer.start()

    def _check(self, label: str) -> None:
        with self._lock:
            watch = self._watches.get(label)
        if watch is None:
            return  # wurde zwischenzeitlich abgebrochen

        try:
            price, currency, _ = _fetch_price(watch["symbol"])
        except (ValueError, KeyError, requests.RequestException):
            self._schedule_check(label)
            return

        crossed = (
            (watch["direction"] == "above" and price >= watch["target_price"])
            or (watch["direction"] == "below" and price <= watch["target_price"])
        )
        if crossed:
            with self._lock:
                self._watches.pop(label, None)
            self._on_alert(
                f"{watch['symbol']} hat {price} {currency} erreicht "
                f"(Zielschwelle: {watch['target_price']})."
            )
        else:
            self._schedule_check(label)
