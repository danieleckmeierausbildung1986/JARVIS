from dataclasses import dataclass

import requests

from jarvis import config, weather
from jarvis.calendar_store import CalendarStore
from jarvis.timers import TimerManager

TOOL_DEFINITIONS = [
    {
        "name": "control_device",
        "description": (
            "Schaltet ein Smart-Home-Gerät in Home Assistant ein oder aus "
            "(z.B. Lichter, Steckdosen, Schalter)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Home Assistant entity_id, z.B. 'light.wohnzimmer'",
                },
                "action": {
                    "type": "string",
                    "enum": ["turn_on", "turn_off", "toggle"],
                    "description": "Aktion, die ausgeführt werden soll",
                },
            },
            "required": ["entity_id", "action"],
        },
    },
    {
        "name": "get_device_state",
        "description": "Liest den aktuellen Status eines Home-Assistant-Geräts aus.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Home Assistant entity_id, z.B. 'sensor.wohnzimmer_temperatur'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "set_timer",
        "description": "Stellt einen Timer, der nach Ablauf eine Sprachbenachrichtigung auslöst.",
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "number",
                    "description": "Dauer des Timers in Sekunden",
                },
                "label": {
                    "type": "string",
                    "description": "Name/Zweck des Timers, z.B. 'Pasta' oder 'Eier kochen'",
                },
            },
            "required": ["seconds", "label"],
        },
    },
    {
        "name": "get_weather",
        "description": "Ruft das aktuelle Wetter für einen Ort ab.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Ortsname, z.B. 'Berlin' oder 'München'",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "add_calendar_event",
        "description": "Legt einen neuen Kalendertermin an.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Titel des Termins"},
                "when": {
                    "type": "string",
                    "description": "Zeitpunkt im ISO-8601-Format, z.B. '2026-07-05T15:00'",
                },
            },
            "required": ["title", "when"],
        },
    },
    {
        "name": "list_calendar_events",
        "description": "Listet Kalendertermine auf, optional gefiltert nach Datum.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Optionales Datum im Format YYYY-MM-DD, um nur diesen Tag zu filtern. "
                    "Wenn leer, werden alle zukünftigen Termine gelistet.",
                },
            },
            "required": [],
        },
    },
]


class HomeAssistantClient:
    def __init__(self, base_url: str = config.HOME_ASSISTANT_URL, token: str = config.HOME_ASSISTANT_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _require_config(self) -> None:
        if not self.base_url or not self.token:
            raise RuntimeError(
                "Home Assistant ist nicht konfiguriert. Bitte HOME_ASSISTANT_URL und "
                "HOME_ASSISTANT_TOKEN in der .env setzen."
            )

    def control_device(self, entity_id: str, action: str) -> str:
        self._require_config()
        domain = entity_id.split(".")[0]
        url = f"{self.base_url}/api/services/{domain}/{action}"
        response = requests.post(url, headers=self.headers, json={"entity_id": entity_id}, timeout=10)
        response.raise_for_status()
        return f"{entity_id}: {action} ausgeführt."

    def get_device_state(self, entity_id: str) -> str:
        self._require_config()
        url = f"{self.base_url}/api/states/{entity_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f"{entity_id} ist aktuell: {data.get('state')}"


@dataclass
class ToolContext:
    ha_client: HomeAssistantClient
    timer_manager: TimerManager
    calendar: CalendarStore


def execute_tool(name: str, tool_input: dict, ctx: ToolContext) -> str:
    if name == "control_device":
        return ctx.ha_client.control_device(tool_input["entity_id"], tool_input["action"])
    if name == "get_device_state":
        return ctx.ha_client.get_device_state(tool_input["entity_id"])
    if name == "set_timer":
        return ctx.timer_manager.set_timer(tool_input["seconds"], tool_input["label"])
    if name == "get_weather":
        return weather.get_weather(tool_input["location"])
    if name == "add_calendar_event":
        return ctx.calendar.add_event(tool_input["title"], tool_input["when"])
    if name == "list_calendar_events":
        return ctx.calendar.list_events(tool_input.get("date"))
    raise ValueError(f"Unbekanntes Tool: {name}")
