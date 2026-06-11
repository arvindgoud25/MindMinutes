import streamlit as st

from core.ai_client import AIClient, get_ollama_models
from core.prompts import get_system_prompt
from core.utils import read_file, init_session_state

st.set_page_config(
    page_title="MindMinutes - AI Meeting Notes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

# ─── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    provider_option = st.selectbox(
        "AI Provider",
        ["Local (Ollama)", "OpenAI (BYOK)", "Anthropic (BYOK)"],
    )

    provider_config = {}

    if provider_option == "Local (Ollama)":
        api_base = st.text_input(
            "Ollama API URL",
            value="http://localhost:11434",
            help="URL where Ollama server is running",
        )
        available_models = get_ollama_models(api_base)
        if not available_models:
            st.warning(
                "⚠️ No models found. Is Ollama running? Pull a model with "
                "`ollama pull llama3.2` and try again."
            )
            model = st.text_input("Model name", value="llama3.2")
        else:
            model = st.selectbox("Model", available_models)
        provider_config["api_base"] = api_base

    elif provider_option == "OpenAI (BYOK)":
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="sk-...  Your API key is used only for this session",
        )
        model = st.selectbox(
            "Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo"],
        )
        provider_config["api_key"] = api_key

    elif provider_option == "Anthropic (BYOK)":
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="sk-ant-...  Your API key is used only for this session",
        )
        model = st.selectbox(
            "Model",
            [
                "claude-3-5-sonnet-20241022",
                "claude-3-haiku-20240307",
                "claude-3-opus-20240229",
            ],
        )
        provider_config["api_key"] = api_key

    st.markdown("---")
    with st.expander("Generation Parameters", expanded=False):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
        max_tokens = st.slider("Max Tokens", 256, 4096, 2048, 64)

    st.markdown("---")
    if st.session_state.history:
        with st.expander(
            f"📚 History ({len(st.session_state.history)})", expanded=False
        ):
            for i, item in enumerate(st.session_state.history):
                cols = st.columns([3, 1])
                cols[0].caption(
                    f"{item['type']} · {item['provider']} · {item['model']}"
                )
                if cols[1].button("📋", key=f"view_hist_{i}"):
                    st.session_state.current_result = item["result"]
                    st.rerun()
                st.markdown("---")
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()

# ─── Main Content ───────────────────────────────────────────────────────────

st.title("📝 MindMinutes")
st.markdown("Paste a meeting transcript or upload a file to get AI-powered analysis.")

input_tab, upload_tab = st.tabs(["📄 Paste Transcript", "📁 Upload File"])

transcript = ""
with input_tab:
    transcript = st.text_area(
        "Paste your meeting transcript below:",
        height=280,
        placeholder="Paste the meeting transcript here...",
    )

with upload_tab:
    uploaded_file = st.file_uploader(
        "Upload a transcript file",
        type=["txt", "md", "docx", "pdf"],
    )
    if uploaded_file is not None:
        with st.spinner("Reading file..."):
            transcript = read_file(uploaded_file)
        st.info(
            f"Loaded **{uploaded_file.name}** ({len(transcript)} characters)"
        )
        with st.expander("Preview", expanded=False):
            st.text(transcript[:3000] + ("..." if len(transcript) > 3000 else ""))

analysis_type = st.selectbox(
    "Analysis Type",
    ["Full Analysis", "Summary", "Action Items", "Key Decisions"],
)

analyze_clicked = st.button("🚀 Analyze", type="primary", use_container_width=True)

if analyze_clicked:
    if not transcript.strip():
        st.error("Please provide a transcript to analyze.")
    elif provider_option != "Local (Ollama)" and not provider_config.get("api_key"):
        st.error(f"Please enter your API key for {provider_option}.")
    else:
        client = AIClient(
            provider=provider_option,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **provider_config,
        )

    if transcript.strip() and (
        provider_option == "Local (Ollama)" or provider_config.get("api_key")
    ):
        with st.spinner("🤖 Analyzing your transcript..."):
            try:
                system_prompt = get_system_prompt(analysis_type)
                result = client.chat(system_prompt, transcript)

                st.session_state.current_result = result
                st.session_state.history.append(
                    {
                        "type": analysis_type,
                        "provider": provider_option,
                        "model": model,
                        "result": result,
                    }
                )
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.info(
                    "**Tips:**  \n"
                    "- For Ollama, ensure the server is running (`ollama serve`)  \n"
                    "- For BYOK, verify your API key is correct  \n"
                    "- Check that the model name is valid"
                )

if st.session_state.current_result:
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("📊 Analysis Results")
        st.caption(
            f"**Provider:** {st.session_state.history[-1]['provider'] if st.session_state.history else provider_option}  ·  "
            f"**Model:** {st.session_state.history[-1]['model'] if st.session_state.history else model}  ·  "
            f"**Type:** {st.session_state.history[-1]['type'] if st.session_state.history else analysis_type}"
        )
    with col2:
        st.download_button(
            "📥 Download MD",
            st.session_state.current_result,
            file_name="meeting_analysis.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col3:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.current_result = None
            st.rerun()

    st.markdown(st.session_state.current_result)

st.markdown("---")
st.caption(
    "Built for Hackathon · "
    "Supports **Local AI** (Ollama) & **BYOK** (OpenAI / Anthropic) · "
    "Your API keys stay client-side and are never stored"
)
