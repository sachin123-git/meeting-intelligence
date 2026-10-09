import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts"
INDEX_DIR = ROOT / "data" / "faiss_index"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
