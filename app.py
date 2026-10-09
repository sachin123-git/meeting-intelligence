import json
import tempfile
from pathlib import Path
import streamlit as st
from src.transcribe import transcribe
from src.extract import extract
from src.rag import ask, build_index
from src.agent import run_agent

st.set_page_config(page_title="Meeting Intelligence", layout="wide")
st.title("AI Meeting Intelligence")
tab1, tab2, tab3 = st.tabs(["Analyze meeting", "Ask your meetings", "Push to boards"])

with tab1:
    f = st.file_uploader("Recording (mp3/wav/m4a/mp4) or transcript (.txt)",    type=["mp3", "wav", "m4a", "mp4", "txt", "json"])
    if f and st.button("Analyze"):
        with st.spinner("Transcribing + extracting..."):
            if f.name.endswith(".json"):
                text = json.loads(f.read())["text"]
            elif f.name.endswith(".txt"):
                text = f.read().decode()
            else:
                with tempfile.NamedTemporaryFile(suffix=Path(f.name).suffix, delete=False) as t:
                    t.write(f.read())
                text = transcribe(t.name)["text"]
            st.session_state["result"] = extract(text)
    r = st.session_state.get("result")
    if r:
        st.subheader("Summary"); st.write(r["summary"])
        c1, c2, c3 = st.columns(3)
        c1.subheader("Decisions"); c1.dataframe(r["decisions"], use_container_width=True)
        c2.subheader("Action items"); c2.dataframe(r["action_items"], use_container_width=True)
        c3.subheader("Risks"); c3.dataframe(r["risks"], use_container_width=True)

with tab2:
    if st.button("Rebuild index"):
        build_index(); st.success("Index rebuilt")
    q = st.text_input("Ask across all past meetings")
    if q:
        out = ask(q)
        st.write(out["answer"])
        with st.expander("Sources"): st.json(out["sources"])

with tab3:
    r = st.session_state.get("result")
    if not r:
        st.info("Analyze a meeting first.")
    else:
        target = st.radio("Target", ["both", "Notion", "Trello"], horizontal=True)
        dry = st.checkbox("Dry run (don't call APIs)", value=True)
        if st.button("Run agent"):
            for entry in run_agent(r["action_items"], target, dry_run=dry):
                st.json(entry)
