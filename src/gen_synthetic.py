import json, random
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from .config import MODEL, TRANSCRIPTS, ROOT

client = OpenAI()
NATO = "Alpha Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliet Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform Victor Whiskey Xray Yankee Zulu".split()
TOPICS = ["product launch", "vendor contract", "hiring plan", "security audit", "budget review",
          "customer churn", "sprint planning", "data migration", "marketing campaign", "incident postmortem"]
PROMPT = """Write a realistic 600-900 word meeting transcript with speaker labels and 4 named people.
Project codename: {code}. Topic: {topic}.
Include 2 decisions, 3 action items (owner + due date), 1 risk.
Then write ONE factual question that mentions the codename and is answerable only from this transcript,
plus a short distinctive answer keyword (a name or a date).
Return JSON: {{"transcript": str, "question": str, "keyword": str}}"""

def one(i):
    code = f"Project {NATO[i % 26]}-{i // 26 + 1}"
    r = client.chat.completions.create(
        model=MODEL, response_format={"type": "json_object"}, temperature=1.0,
        messages=[{"role": "user", "content": PROMPT.format(code=code, topic=random.choice(TOPICS))}])
    d = json.loads(r.choices[0].message.content)
    mid = f"meeting_{i:03d}"
    (TRANSCRIPTS / f"{mid}.json").write_text(json.dumps({"meeting_id": mid, "text": d["transcript"], "segments": []}))
    return {"question": d["question"], "must_contain": [d["keyword"]]}

if __name__ == "__main__":
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(8) as ex:
        cases = list(ex.map(one, range(55)))
    (ROOT / "tests" / "known_answers.json").write_text(json.dumps(cases, indent=2))
    print("done:", len(cases))