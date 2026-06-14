import os
import streamlit as st

from core.ai_client import AIClient, get_ollama_models
from core.prompts import get_system_prompt
from core.translations import LANGUAGES
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
    if "output_language" not in st.session_state:
        st.session_state.output_language = "English"

    language = st.selectbox(
        "Language",
        ["English", "Telugu", "Hindi"]
    )

    if st.session_state.output_language in ["English", "Telugu", "Hindi"]:
        if st.session_state.get("last_language") != language:
            st.session_state.output_language = language
            st.session_state.last_language = language

    t = LANGUAGES[language]

    st.toggle("🌙 Dark Mode", key="dark_mode_toggle")

    st.title(f"⚙️ {t['configuration']}")
    st.markdown("---")

    provider_option = st.selectbox(
        t["ai_provider"],
        ["Google Gemini", "Local (Ollama)", "OpenAI (BYOK)", "Anthropic (BYOK)"],
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

    elif provider_option == "Google Gemini":
        if not (st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")):
            st.warning(
                "⚠️ GEMINI_API_KEY not found. Set it in "
                "`.streamlit/secrets.toml` or as an environment variable."
            )
        model = st.selectbox(
            "Model",
            ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        )

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
    with st.expander(f"⚡ {t['gen_params']}", expanded=False):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
        max_tokens = st.slider("Max Tokens", 256, 4096, 2048, 64)

    st.markdown("---")
    if st.session_state.history:
        with st.expander(
            f"🕐 {t['history']} ({len(st.session_state.history)})", expanded=False
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
            if st.button(f"🗑️ {t['clear_history']}"):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()

# ─── Theme CSS ───────────────────────────────────────────────────────────────

if st.session_state.get("dark_mode_toggle", False):
    st.markdown("""
<style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 8px rgba(108, 99, 255, 0.3); }
        50% { box-shadow: 0 0 25px rgba(108, 99, 255, 0.6); }
    }

    .stApp {
        background: linear-gradient(-45deg, #0a0a1a, #0d1117, #111827, #0a0a1a) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 15s ease infinite;
        color: #e2e8f0;
    }
    .stApp::before {
        content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(108, 99, 255, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(0, 201, 255, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(255, 0, 128, 0.03) 0%, transparent 50%);
        pointer-events: none; z-index: 0;
    }
    .stApp header { background: rgba(10, 10, 26, 0.8) !important; backdrop-filter: blur(12px); border-bottom: 1px solid rgba(108, 99, 255, 0.15); }
    .stSidebar, section[data-testid="stSidebar"] { background: rgba(13, 17, 23, 0.95) !important; border-right: 1px solid rgba(108, 99, 255, 0.12); backdrop-filter: blur(16px); }
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #e2e8f0, #a78bfa, #6C63FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        font-weight: 700; letter-spacing: -0.02em;
    }
    .stMarkdown, .stText, p, li, span, label, .stCaption { color: #c8d0dc !important; }
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(17, 24, 39, 0.8) !important; color: #e2e8f0 !important;
        backdrop-filter: blur(8px); border: 1px solid rgba(108, 99, 255, 0.2) !important;
        border-radius: 12px !important; transition: all 0.3s ease;
    }
    .stTextArea textarea:focus { border-color: #6C63FF !important; box-shadow: 0 0 20px rgba(108, 99, 255, 0.15); }
    div.stButton button, div.stDownloadButton button {
        background: linear-gradient(135deg, #6C63FF, #a78bfa) !important; color: white !important;
        border: none !important; border-radius: 12px !important; padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important; transition: all 0.3s ease !important;
        animation: glowPulse 3s ease-in-out infinite;
    }
    div.stButton button:hover, div.stDownloadButton button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 0 35px rgba(108, 99, 255, 0.4) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(17, 24, 39, 0.6); backdrop-filter: blur(12px);
        border-radius: 14px; padding: 4px; gap: 4px; border: 1px solid rgba(108, 99, 255, 0.1);
    }
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; border-radius: 10px !important; transition: all 0.3s ease; padding: 0.5rem 1.2rem !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background: linear-gradient(135deg, rgba(108, 99, 255, 0.25), rgba(167, 139, 250, 0.15)); color: #e2e8f0 !important; }
    .stAlert, div[role="alert"] { background: rgba(17, 24, 39, 0.7) !important; backdrop-filter: blur(8px); border: 1px solid rgba(108, 99, 255, 0.15); border-radius: 12px; }
    div[data-testid="stExpander"] {
        background: rgba(17, 24, 39, 0.5) !important; backdrop-filter: blur(8px);
        border: 1px solid rgba(108, 99, 255, 0.12); border-radius: 14px; transition: all 0.3s ease;
    }
    .stFileUploader {
        background: rgba(17, 24, 39, 0.5) !important; backdrop-filter: blur(8px);
        border: 2px dashed rgba(108, 99, 255, 0.25) !important; border-radius: 16px !important; transition: all 0.3s ease;
    }
    .stFileUploader:hover { border-color: rgba(108, 99, 255, 0.5) !important; background: rgba(108, 99, 255, 0.05); }
    pre { background: rgba(13, 17, 23, 0.8) !important; backdrop-filter: blur(8px); border: 1px solid rgba(108, 99, 255, 0.12); border-radius: 12px; }
    code { color: #a78bfa !important; }
    .stSpinner > div > div { border-color: #6C63FF transparent transparent transparent !important; }
    .stMetric { background: rgba(17, 24, 39, 0.5); backdrop-filter: blur(8px); border: 1px solid rgba(108, 99, 255, 0.12); border-radius: 12px; padding: 1rem; }
    .stTextInput input { background: rgba(17, 24, 39, 0.8) !important; color: #e2e8f0 !important; border: 1px solid rgba(108, 99, 255, 0.2) !important; border-radius: 12px !important; transition: all 0.3s ease; }
    hr { border-color: rgba(108, 99, 255, 0.12); }
    .st-bb, .st-bt, .st-bl, .st-br { border-color: rgba(108, 99, 255, 0.12); }
</style>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<style>
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
    }

    .stApp {
        background: linear-gradient(135deg, #f8f9ff, #f0f2ff, #f8f9ff);
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite;
    }
    .stApp::before {
        content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse at 10% 10%, rgba(108, 99, 255, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 90%, rgba(167, 139, 250, 0.03) 0%, transparent 50%);
        pointer-events: none; z-index: 0;
    }
    .stApp header { background: rgba(255, 255, 255, 0.85) !important; backdrop-filter: blur(12px); border-bottom: 1px solid rgba(108, 99, 255, 0.1); }
    .stSidebar, section[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.92) !important; border-right: 1px solid rgba(108, 99, 255, 0.08); backdrop-filter: blur(16px); }
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #1a1a2e, #6C63FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        font-weight: 700; letter-spacing: -0.02em;
    }
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(108, 99, 255, 0.15) !important;
        border-radius: 12px !important; transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(108, 99, 255, 0.05);
    }
    .stTextArea textarea:focus { border-color: #6C63FF !important; box-shadow: 0 0 20px rgba(108, 99, 255, 0.12); }
    div.stButton button, div.stDownloadButton button {
        background: linear-gradient(135deg, #6C63FF, #8b7cf7) !important; color: white !important;
        border: none !important; border-radius: 12px !important; padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important; transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.25);
    }
    div.stButton button:hover, div.stDownloadButton button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 25px rgba(108, 99, 255, 0.35) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(12px);
        border-radius: 14px; padding: 4px; gap: 4px; border: 1px solid rgba(108, 99, 255, 0.1);
        box-shadow: 0 2px 10px rgba(108, 99, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background: linear-gradient(135deg, rgba(108, 99, 255, 0.12), rgba(167, 139, 250, 0.08)); color: #6C63FF !important; font-weight: 600; }
    .stAlert, div[role="alert"] { background: rgba(255, 255, 255, 0.9) !important; backdrop-filter: blur(8px); border: 1px solid rgba(108, 99, 255, 0.12); border-radius: 12px; }
    .stAlert { border-left: 4px solid #6C63FF !important; }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.6) !important; backdrop-filter: blur(8px);
        border: 1px solid rgba(108, 99, 255, 0.08); border-radius: 14px; transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(108, 99, 255, 0.04);
    }
    .stFileUploader {
        background: rgba(255, 255, 255, 0.6) !important; backdrop-filter: blur(8px);
        border: 2px dashed rgba(108, 99, 255, 0.2) !important; border-radius: 16px !important; transition: all 0.3s ease;
    }
    .stFileUploader:hover { border-color: rgba(108, 99, 255, 0.4) !important; background: rgba(108, 99, 255, 0.03); }
    pre { background: rgba(255, 255, 255, 0.8) !important; border: 1px solid rgba(108, 99, 255, 0.1); border-radius: 12px; }
    code { color: #6C63FF !important; }
    .stSpinner > div > div { border-color: #6C63FF transparent transparent transparent !important; }
    .stMetric { background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(8px); border: 1px solid rgba(108, 99, 255, 0.08); border-radius: 12px; padding: 1rem; }
    .stTextInput input { background: rgba(255, 255, 255, 0.9) !important; border: 1px solid rgba(108, 99, 255, 0.15) !important; border-radius: 12px !important; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(108, 99, 255, 0.05); }
    .stTextInput input:focus { border-color: #6C63FF !important; box-shadow: 0 0 20px rgba(108, 99, 255, 0.12); }
    hr { border-color: rgba(108, 99, 255, 0.1); }
</style>
""", unsafe_allow_html=True)

# ─── Main Content ───────────────────────────────────────────────────────────

st.title(f"🧠 {t['title']}")
st.markdown(t["tagline"])

analysis_options = t["analysis_options"]
ANALYSIS_KEYS = ["Full Analysis", "Summary", "Action Items", "Key Decisions"]

input_tab, upload_tab = st.tabs([f"📋 {t['paste_transcript']}", f"📁 {t['upload_file']}"])

transcript = ""
with input_tab:
    transcript = st.text_area(
        t["paste_label"],
        height=280,
        placeholder=t["paste_placeholder"],
    )

with upload_tab:
    uploaded_file = st.file_uploader(
        t["upload_label"],
        type=["txt", "md", "docx", "pdf"],
    )
    if uploaded_file is not None:
        with st.spinner("Reading file..."):
            transcript = read_file(uploaded_file)
        st.info(
            t["loaded_file"].format(name=uploaded_file.name, chars=len(transcript))
        )
        with st.expander(t["preview"], expanded=False):
            st.text(transcript[:3000] + ("..." if len(transcript) > 3000 else ""))

selected_analysis = st.selectbox(
    t["analysis_type"],
    analysis_options,
)
analysis_type = ANALYSIS_KEYS[analysis_options.index(selected_analysis)]

output_language = st.selectbox(
    t["output_language"],
    ["English", "Telugu", "Hindi"],
    index=["English", "Telugu", "Hindi"].index(
        st.session_state.output_language
    )
)

st.session_state.output_language = output_language

analyze_clicked = st.button(
    f"🚀 {t['analyze']}",
    type="primary",
    use_container_width=True
)

if analyze_clicked:
    if not transcript.strip():
        st.error(t["no_transcript"])
    elif provider_option not in ("Local (Ollama)", "Google Gemini") and not provider_config.get("api_key"):
        st.error(t["no_api_key"].format(provider=provider_option))
    else:
        client = AIClient(
            provider=provider_option,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **provider_config,
        )

    if transcript.strip() and (
        provider_option in ("Local (Ollama)", "Google Gemini") or provider_config.get("api_key")
    ):
        with st.spinner("🤖 Analyzing your transcript..."):
            try:
                system_prompt = get_system_prompt(
                    analysis_type,
                    output_language
                )
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
                st.error(t["analysis_failed"].format(error=e))
                st.info(
                    f"**{t['tips']}**  \n"
                    f"- {t['tip_ollama']}  \n"
                    f"- {t['tip_byok']}  \n"
                    f"- {t['tip_model']}"
                )

if st.session_state.current_result:
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"📊 {t['analysis_results']}")
        st.caption(
            f"**{t['provider']}:** {st.session_state.history[-1]['provider'] if st.session_state.history else provider_option}  ·  "
            f"**{t['model']}:** {st.session_state.history[-1]['model'] if st.session_state.history else model}  ·  "
            f"**{t['type']}:** {st.session_state.history[-1]['type'] if st.session_state.history else analysis_type}"
        )
    with col2:
        st.download_button(
            f"📥 {t['download_md']}",
            st.session_state.current_result,
            file_name="meeting_analysis.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col3:
        if st.button(f"🔄 {t['new_analysis']}", use_container_width=True):
            st.session_state.current_result = None
            st.rerun()

    st.markdown(st.session_state.current_result)

