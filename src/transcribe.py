"""Step 1: audio/video -> transcript (Whisper)."""
import json
from functools import lru_cache
from pathlib import Path
import whisper
from .config import TRANSCRIPTS, WHISPER_MODEL


@lru_cache(maxsize=1)
def _model():
    return whisper.load_model(WHISPER_MODEL)


def transcribe(audio_path: str | Path, save: bool = True) -> dict:
    audio_path = Path(audio_path)
    res = _model().transcribe(str(audio_path))
    out = {
        "meeting_id": audio_path.stem,
        "text": res["text"].strip(),
        "segments": [
            {"start": round(s["start"], 1), "end": round(s["end"], 1), "text": s["text"].strip()}
            for s in res["segments"]
        ],
    }
    if save:
        TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
        (TRANSCRIPTS / f"{out['meeting_id']}.json").write_text(json.dumps(out, indent=2))
    return out
