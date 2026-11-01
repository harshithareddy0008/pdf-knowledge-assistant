"""Streamlit UI for the PDF Knowledge Assistant (per-browser session workspace)."""
from uuid import uuid4

import streamlit as st

from frontend.api_client import APIError, request_api

st.set_page_config(page_title="PDF Knowledge Assistant | RAG", page_icon="📚", layout="wide")

if "workspace" not in st.session_state:
    st.session_state.workspace = str(uuid4())
if "chat" not in st.session_state:
    st.session_state.chat = []

st.title("📚 PDF Knowledge Assistant")
st.caption("Project 02 · Gemini LLM + RAG · LangChain · ChromaDB · FastAPI")
st.info("Upload text-based PDFs, then ask questions. Answers use retrieved passages with PDF/page references. Don't upload sensitive documents to a public demo.")

with st.sidebar:
    st.header("📄 Your PDF workspace")
    uploads = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True, help="Up to 4 per upload, 8 MB and 80 pages each.")
    if st.button("📥 Process PDFs", use_container_width=True, type="primary"):
        if not uploads:
            st.warning("First choose at least one PDF.")
        elif len(uploads) > 4:
            st.error("Please choose at most 4 PDFs per upload.")
        else:
            with st.spinner("Extracting, chunking and embedding PDF pages..."):
                try:
                    result = request_api(
                        "POST", "/upload", st.session_state.workspace,
                        files=[("files", (f.name, f.getvalue(), "application/pdf")) for f in uploads],
                    )
                    for item in result["results"]:
                        st.success(f"{item['file']}: {item['status']} · {item['chunks']} chunks")
                    st.session_state.indexed_docs = request_api(
                        "GET", "/documents", st.session_state.workspace
                    )["documents"]
                except APIError as exc:
                    st.error(str(exc))
    st.divider()
    if st.button("🔄 Refresh indexed PDFs", use_container_width=True):
        try:
            st.session_state.indexed_docs = request_api("GET", "/documents", st.session_state.workspace)["documents"]
        except APIError as exc:
            st.error(str(exc))
    for doc in st.session_state.get("indexed_docs", []):
        st.caption(f"📄 {doc['file']} · {doc['pages']} pages · {doc['chunks']} chunks")
    if st.button("🗑️ Clear my documents", use_container_width=True):
        try:
            request_api("DELETE", "/documents", st.session_state.workspace)
            st.session_state.chat = []
            st.session_state.indexed_docs = []
            st.success("Workspace cleared.")
        except APIError as exc:
            st.error(str(exc))
    st.divider()
    st.caption("Documents are indexed per browser session, not a login account. Chroma data is stored on the API server. Render free storage may reset on restart.")

col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("💬 Ask your documents")
with col2:
    if st.button("Clear chat", use_container_width=True):
        st.session_state.chat = []
        st.rerun()

for turn in st.session_state.chat:
    with st.chat_message(turn["role"]):
        st.markdown(turn["text"])
        if turn.get("sources"):
            with st.expander("📎 Retrieved PDF sources"):
                for source in turn["sources"]:
                    st.markdown(f"**[{source['number']}] {source['file']} — page {source['page']}**")
                    st.caption(source["excerpt"])

question = st.chat_input("Example: What is supervised learning according to my PDF?")
if question:
    st.session_state.chat.append({"role": "user", "text": question})
    with st.spinner("Searching PDFs and generating answer..."):
        try:
            result = request_api("POST", "/ask", st.session_state.workspace, json={"question": question})
        except APIError as exc:
            st.session_state.chat.append({"role": "assistant", "text": f"⚠️ {exc}", "sources": []})
        else:
            st.session_state.chat.append({"role": "assistant", "text": result["answer"], "sources": result["sources"]})
    st.rerun()

st.divider()
with st.expander("ℹ️ How this RAG app works"):
    st.markdown("**PDF → PyMuPDF extraction → LangChain text chunks → Gemini Embeddings → ChromaDB → retrieval → Gemini answer + cited passages.**\n\nThis is a learning/demo application. It has no user login, no OCR for scanned PDFs, and no guarantee that generated answers are correct. Review the quoted source passages.")
