"""Step 2: transcript -> decisions, action items, risks (Claude, forced tool call = guaranteed JSON)."""
from openai import OpenAI
import json
from .config import MODEL

client = OpenAI()

SCHEMA = {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "description": "3-4 sentence summary"},
            "decisions": {
                "type": "array",
                "items": {"type": "object", "properties": {
                    "decision": {"type": "string"},
                    "rationale": {"type": "string"},
                }, "required": ["decision"]},
            },
            "action_items": {
                "type": "array",
                "items": {"type": "object", "properties": {
                    "task": {"type": "string"},
                    "owner": {"type": "string", "description": "Person named, else 'Unassigned'"},
                    "due_date": {"type": "string", "description": "ISO date if stated, else empty"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                }, "required": ["task", "owner"]},
            },
            "risks": {
                "type": "array",
                "items": {"type": "object", "properties": {
                    "risk": {"type": "string"},
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "mitigation": {"type": "string"},
                }, "required": ["risk"]},
            },
        },
        "required": ["summary", "decisions", "action_items", "risks"],
}

SYSTEM = (
    "You extract meeting intelligence. Only include items actually supported by the transcript. "
    "Never invent owners or dates; use 'Unassigned' / empty string when not stated."
)


def extract(transcript_text: str) -> dict:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"<transcript>\n{transcript_text}\n</transcript>"},
        ],
        tools=[{"type": "function", "function": {
            "name": "record_meeting",
            "description": "Record structured intelligence extracted from a meeting transcript.",
            "parameters": SCHEMA}}],
        tool_choice={"type": "function", "function": {"name": "record_meeting"}},
    )
    return json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
