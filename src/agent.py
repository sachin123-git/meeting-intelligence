"""Step 4: tool-calling agent that routes action items to Notion / Trello."""
import json
from openai import OpenAI
from .config import MODEL
from .integrations import push_to_notion, push_to_trello

client = OpenAI()

_item = {
    "type": "object",
    "properties": {
        "task": {"type": "string"}, "owner": {"type": "string"},
        "due_date": {"type": "string"}, "priority": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["task"],
}
TOOLS = [
    {"type": "function", "function": {"name": "push_to_notion", "description": "Create a task in the team's Notion database (best for documentation-heavy / long-term tasks).", "parameters": _item}},
    {"type": "function", "function": {"name": "push_to_trello", "description": "Create a card on the team's Trello board (best for short, sprint-style tasks).", "parameters": _item}},
]
REGISTRY = {"push_to_notion": push_to_notion, "push_to_trello": push_to_trello}

SYSTEM = (
    "You file meeting action items into task boards. For each item call the appropriate tool exactly once. "
    "If the user names a target (Notion/Trello/both), obey it. Skip duplicates. "
    "When finished, give a one-line summary."
)


def run_agent(action_items: list[dict], target: str = "both", dry_run: bool = False) -> list[dict]:
    log: list[dict] = []
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Target: {target}\nAction items:\n{json.dumps(action_items, indent=2)}"},
    ]
    for _ in range(10):  # hard cap on loop
        msg = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            log.append({"final": msg.content})
            return log
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            try:
                out = {"ok": True, "dry_run": True} if dry_run else REGISTRY[call.function.name](**args)
            except Exception as e:
                out = {"ok": False, "error": str(e)}
            log.append({"tool": call.function.name, "input": args, "result": out})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(out)})
    return log
