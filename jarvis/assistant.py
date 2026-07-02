import json
from datetime import datetime
from typing import Callable

import anthropic

from jarvis import config
from jarvis.calendar_store import CalendarStore
from jarvis.stocks import StockWatcher
from jarvis.timers import TimerManager
from jarvis.tools import TOOL_DEFINITIONS, HomeAssistantClient, ToolContext, execute_tool


def _system_prompt() -> str:
    now = datetime.now().strftime("%A, %d.%m.%Y %H:%M")
    return (
        "Du bist Jarvis, ein hilfsbereiter persönlicher Sprachassistent. "
        "Antworte kurz, klar und in gesprochener Sprache (keine Aufzählungszeichen, "
        "keine Markdown-Formatierung, da deine Antwort vorgelesen wird). "
        "Nutze die verfügbaren Tools, um Smart-Home-Geräte zu steuern, Timer zu stellen, "
        "das Wetter abzufragen, Kalendertermine zu verwalten, Nachrichten vorzulesen oder "
        "Aktienkurse abzufragen/zu überwachen, wenn der Nutzer danach fragt. "
        "Wenn du für ein Tool ein Datum/Uhrzeit im ISO-8601-Format brauchst, rechne relative "
        f"Angaben (z.B. 'morgen', 'in einer Stunde') anhand des aktuellen Zeitpunkts aus: {now}."
    )


def _serialize_content(content):
    if isinstance(content, str):
        return content
    return [block.model_dump() if hasattr(block, "model_dump") else block for block in content]


def _load_history() -> list[dict]:
    if not config.HISTORY_PATH.exists():
        return []
    try:
        return json.loads(config.HISTORY_PATH.read_text())
    except json.JSONDecodeError:
        return []


def _trim_to_turns(messages: list[dict], max_turns: int) -> list[dict]:
    turn_starts = [i for i, m in enumerate(messages) if m["role"] == "user" and isinstance(m["content"], str)]
    if len(turn_starts) <= max_turns:
        return messages
    cutoff = turn_starts[-max_turns]
    return messages[cutoff:]


class Assistant:
    def __init__(self, on_alarm: Callable[[str], None] | None = None):
        alarm_callback = on_alarm or (lambda message: print(f"\n⏰ {message}"))
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.ctx = ToolContext(
            ha_client=HomeAssistantClient(),
            timer_manager=TimerManager(alarm_callback),
            calendar=CalendarStore(),
            stock_watcher=StockWatcher(alarm_callback),
        )
        self.messages: list[dict] = _trim_to_turns(_load_history(), config.MAX_HISTORY_TURNS)

    def _save_history(self) -> None:
        config.HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        config.HISTORY_PATH.write_text(json.dumps(self.messages, ensure_ascii=False, indent=2))

    def ask(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        while True:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=1024,
                system=_system_prompt(),
                tools=TOOL_DEFINITIONS,
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": _serialize_content(response.content)})

            if response.stop_reason != "tool_use":
                self.messages = _trim_to_turns(self.messages, config.MAX_HISTORY_TURNS)
                self._save_history()
                return "".join(block.text for block in response.content if block.type == "text")

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                try:
                    result = execute_tool(block.name, block.input, self.ctx)
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
