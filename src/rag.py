"""Step 3: RAG over historical transcripts (FAISS + LangChain) with cited answers."""
import re
import json
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import TRANSCRIPTS, INDEX_DIR, EMBED_MODEL, MODEL

_emb = None
client = OpenAI()


def embeddings():
    global _emb
    if _emb is None:
        _emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return _emb


def build_index() -> FAISS:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    texts, metas = [], []
    for f in sorted(TRANSCRIPTS.glob("*.json")):
        d = json.loads(f.read_text())
        m = re.search(r"Project\s+[A-Za-z]+-\d+", d["text"])
        tag = m.group(0) if m else d["meeting_id"]
        for i, chunk in enumerate(splitter.split_text(d["text"])):
            texts.append(f"[{tag}] {chunk}")
            metas.append({"meeting_id": d["meeting_id"], "chunk": i, "project": tag})
    if not texts:
        raise ValueError(f"No transcripts found in {TRANSCRIPTS}")
    store = FAISS.from_texts(texts, embeddings(), metadatas=metas)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(INDEX_DIR))
    return store

def load_index() -> FAISS:
    if not (INDEX_DIR / "index.faiss").exists():
        return build_index()
    return FAISS.load_local(str(INDEX_DIR), embeddings(), allow_dangerous_deserialization=True)


def ask(question: str, k: int = 8) -> dict:
    docs = load_index().similarity_search(question, k=k)
    context = "\n\n".join(f"[{d.metadata['meeting_id']}#{d.metadata['chunk']}]\n{d.page_content}" for d in docs)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Answer ONLY from the provided meeting excerpts. Cite sources as [meeting_id#chunk]. If the excerpts don't contain the answer, say so."},
            {"role": "user", "content": f"<excerpts>\n{context}\n</excerpts>\n\nQuestion: {question}"},
        ],
    )
    return {"answer": resp.choices[0].message.content, "sources": [d.metadata for d in docs]}
