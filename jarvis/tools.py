import requests

from jarvis import config

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


def execute_tool(name: str, tool_input: dict, ha_client: HomeAssistantClient) -> str:
    if name == "control_device":
        return ha_client.control_device(tool_input["entity_id"], tool_input["action"])
    if name == "get_device_state":
        return ha_client.get_device_state(tool_input["entity_id"])
    raise ValueError(f"Unbekanntes Tool: {name}")
