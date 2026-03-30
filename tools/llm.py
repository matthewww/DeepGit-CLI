# tools/llm.py
"""
LLM factory for DeepGit-CLI-Lean.

Configuration via environment variables:
  DEEPGIT_LLM_MODEL     Model name (default: claude-haiku-4-5-20251001)
  DEEPGIT_LLM_BASE_URL  OpenAI-compatible base URL (e.g. Groq, Ollama, LM Studio)

Provider selection logic:
  - If DEEPGIT_LLM_BASE_URL is set → ChatOpenAI with that base URL (covers Groq, Ollama, etc.)
  - Else if model starts with "claude" → ChatAnthropic
  - Else → ChatOpenAI (standard OpenAI endpoint)

Required env vars per provider:
  Anthropic (default): ANTHROPIC_API_KEY
  OpenAI:              OPENAI_API_KEY
  Groq:                GROQ_API_KEY  (set DEEPGIT_LLM_BASE_URL=https://api.groq.com/openai/v1)
  Ollama:              no key needed  (set DEEPGIT_LLM_BASE_URL=http://localhost:11434/v1)
"""
import os
from typing import Optional


_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_DEFAULT_TEMPERATURE = 0.3
_DEFAULT_MAX_TOKENS = 512


def build_llm(model: Optional[str] = None, base_url: Optional[str] = None):
    """Return a LangChain chat model configured from arguments or env vars."""
    model = model or os.getenv("DEEPGIT_LLM_MODEL", _DEFAULT_MODEL)
    base_url = base_url or os.getenv("DEEPGIT_LLM_BASE_URL")

    if base_url:
        from langchain_openai import ChatOpenAI
        api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("GROQ_API_KEY")
            or os.getenv("DEEPGIT_LLM_API_KEY")
            or "none"  # Ollama and similar don't need a key
        )
        return ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=_DEFAULT_TEMPERATURE,
            max_tokens=_DEFAULT_MAX_TOKENS,
        )

    if model.startswith("claude"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=_DEFAULT_TEMPERATURE,
            max_tokens=_DEFAULT_MAX_TOKENS,
        )

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model,
        temperature=_DEFAULT_TEMPERATURE,
        max_tokens=_DEFAULT_MAX_TOKENS,
    )
