import anthropic

from jarvis import config
from jarvis.tools import TOOL_DEFINITIONS, HomeAssistantClient, execute_tool

SYSTEM_PROMPT = (
    "Du bist Jarvis, ein hilfsbereiter persönlicher Sprachassistent. "
    "Antworte kurz, klar und in gesprochener Sprache (keine Aufzählungszeichen, "
    "keine Markdown-Formatierung, da deine Antwort vorgelesen wird). "
    "Nutze die verfügbaren Tools, um Smart-Home-Geräte zu steuern oder deren Status abzufragen, "
    "wenn der Nutzer danach fragt."
)


class Assistant:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.ha_client = HomeAssistantClient()
        self.messages: list[dict] = []

    def ask(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        while True:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return "".join(block.text for block in response.content if block.type == "text")

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                try:
                    result = execute_tool(block.name, block.input, self.ha_client)
                except Exception as e:  # noqa: BLE001 - surface any tool failure back to the model
                    result = f"Fehler: {e}"
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

            self.messages.append({"role": "user", "content": tool_results})
