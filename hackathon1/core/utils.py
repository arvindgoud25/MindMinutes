import streamlit as st


def read_file(uploaded_file) -> str:
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""

    if ext == "txt" or ext == "md":
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if ext == "docx":
        try:
            from docx import Document
            doc = Document(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            st.warning("python-docx not installed. Install with: pip install python-docx")
            return uploaded_file.read().decode("utf-8", errors="ignore")

    if ext == "pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            st.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return uploaded_file.read().decode("utf-8", errors="ignore")

    return uploaded_file.read().decode("utf-8", errors="ignore")


def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    if "last_config" not in st.session_state:
        st.session_state.last_config = {}
    if "dark_mode_toggle" not in st.session_state:
        st.session_state.dark_mode_toggle = False
