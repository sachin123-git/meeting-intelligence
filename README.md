# AI Meeting Intelligence System

Whisper -> GPT (structured extraction) -> FAISS RAG -> tool-calling agent -> Notion/Trello, Streamlit UI.

## Run
```bash
pip install -r requirements.txt   # also needs ffmpeg installed
cp .env.example .env              # fill in keys
streamlit run app.py
```
## Notion DB properties required
Name (title), Owner (text), Priority (select), Due (date).

## Evaluate RAG
Put 50+ transcripts in data/transcripts/ (JSON from `transcribe`), edit tests/known_answers.json, then:
`python -m src.evaluate`
