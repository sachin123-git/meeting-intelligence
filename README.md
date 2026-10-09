# AI Meeting Intelligence System

Turn raw meeting recordings into decisions, action items and risks, search across past meetings with cited answers, and push tasks to Notion and Trello automatically.

**Pipeline:** Whisper (speech-to-text) → GPT structured extraction → FAISS RAG over past transcripts → tool-calling agent → Notion / Trello → Streamlit UI

## Demo
| Analyze | Ask (with sources) |
|---|---|
| ![analyze](docs/analyze.png) | ![ask](docs/ask.png) |

| Notion | Trello |
|---|---|
| ![notion](docs/notion.png) | ![trello](docs/trello.png) |

## Features
- **Extraction:** forced function-calling returns schema-valid JSON (summary, decisions, action items with owner/due date/priority, risks).
- **RAG Q&A:** FAISS + LangChain over 55 transcripts; chunks are tagged with their project name, so answers carry citations like `[meeting_019#4]`.
- **Agent:** an OpenAI tool-calling loop creates Notion pages and Trello cards, with a dry-run mode and error handling.

## Evaluation
55 synthetic transcripts, each with one planted known-answer question. Scored by keyword-overlap matching: **89% (49/55)**. Tagging chunks with the project name and loosening the matcher moved the score from 62% to 89%. Note that the same questions were used for tuning, so treat this as a development score.

Run it yourself: `python -m src.gen_synthetic` then `python -m src.evaluate`.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt                     # also needs ffmpeg
cp .env.example .env                                # add your keys
streamlit run app.py
```

**Notion database columns:** Name (title), Owner (text), Priority (select), Due (date). Share the database with your integration.
**Trello:** needs an API key, token and the list ID of the target list.

## Stack
Python, OpenAI API, Whisper, LangChain, FAISS, sentence-transformers, Streamlit, Notion API, Trello API

## Limitations
Evaluated on synthetic data only; Whisper runs locally and is slow on CPU; no speaker diarization yet.