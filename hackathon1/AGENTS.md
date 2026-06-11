# MindMinutes - AI Meeting Notes Summarizer

Hackathon project: AI-powered meeting transcript analysis with local + BYOK support.

## Stack
- **Frontend/App**: Streamlit
- **AI Providers**: Ollama (local), OpenAI BYOK, Anthropic BYOK

## Project Structure
```
hackathon1/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── AGENTS.md           # This file
├── core/
│   ├── __init__.py
│   ├── ai_client.py    # AI provider abstraction (Ollama, OpenAI, Anthropic)
│   ├── prompts.py      # System prompts for each analysis type
│   └── utils.py        # File reading, session state helpers
└── .streamlit/
    └── config.toml     # Streamlit theme/settings
```

## Commands
- Run app: `streamlit run app.py`
- Install deps: `pip install -r requirements.txt`

## Key Design Decisions
- Single AIClient class handles all providers via duck typing
- Ollama models auto-discovered from running server
- BYOK keys entered via password field (never stored to disk)
- History kept in session state only (not persistent)
- Supported uploads: .txt, .md, .docx, .pdf
