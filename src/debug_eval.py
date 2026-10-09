import json
from .config import ROOT
from .rag import ask, load_index

cases = json.loads((ROOT / "tests" / "known_answers.json").read_text())
store = load_index()
retr_miss = fmt_miss = 0
for c in cases:
    ans = ask(c["question"])["answer"]
    if all(k.lower() in ans.lower() for k in c["must_contain"]):
        continue
    chunks = " ".join(d.page_content for d in store.similarity_search(c["question"], k=5)).lower()
    in_chunks = all(k.lower() in chunks for k in c["must_contain"])
    if in_chunks: fmt_miss += 1
    else: retr_miss += 1
    print("\nQ:", c["question"])
    print("EXPECTED:", c["must_contain"], "| keyword in retrieved chunks:", in_chunks)
    print("ANSWER:", ans[:200])
print(f"\nretrieval misses: {retr_miss} | answer/format misses: {fmt_miss}")