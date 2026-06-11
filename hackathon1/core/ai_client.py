import requests
import streamlit as st
from typing import Optional


class AIClient:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(self, system_prompt: str, user_message: str) -> str:
        if "Ollama" in self.provider:
            return self._chat_ollama(system_prompt, user_message)
        elif "OpenAI" in self.provider:
            return self._chat_openai(system_prompt, user_message)
        elif "Anthropic" in self.provider:
            return self._chat_anthropic(system_prompt, user_message)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _chat_ollama(self, system_prompt: str, user_message: str) -> str:
        url = f"{self.api_base.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
            "stream": False,
        }
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        if "message" in data:
            return data["message"]["content"]
        if "response" in data:
            return data["response"]
        raise ValueError(f"Unexpected Ollama response format: {data}")

    def _chat_openai(self, system_prompt: str, user_message: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

    def _chat_anthropic(self, system_prompt: str, user_message: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.content[0].text


@st.cache_data(ttl=30)
def get_ollama_models(api_base: str = "http://localhost:11434") -> list[str]:
    try:
        response = requests.get(
            f"{api_base.rstrip('/')}/api/tags", timeout=5
        )
        response.raise_for_status()
        models = response.json().get("models", [])
        return [m["name"] for m in models]
    except requests.exceptions.ConnectionError:
        return []
    except Exception:
        return []
