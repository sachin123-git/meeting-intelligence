"""python -m src.evaluate  (token-overlap match, >=50% of expected tokens must appear)"""
import json, re
from pathlib import Path
from .rag import ask

def norm(s):
    s = s.lower().replace(",", "")
    s = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", s)
    return re.findall(r"[a-z0-9]+", s)

def match(expected, answer):
    ans = set(norm(answer))
    toks = [t for k in expected for t in norm(k)]
    return bool(toks) and sum(t in ans for t in toks) / len(toks) >= 0.5

def main():
    cases = json.loads((Path(__file__).resolve().parent.parent / "tests" / "known_answers.json").read_text())
    passed = 0
    for c in cases:
        ok = match(c["must_contain"], ask(c["question"])["answer"])
        passed += ok
        print(("PASS" if ok else "FAIL"), "-", c["question"])
    print(f"\n{passed}/{len(cases)} passed ({100*passed/len(cases):.0f}%)")

if __name__ == "__main__":
    main()