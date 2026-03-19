"""
OHARA — LLM Client
Provider-agnostic wrapper. Swap Gemini ↔ Anthropic via .env LLM_PROVIDER.
All calls go through this module. Never import provider SDKs directly elsewhere.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

PROVIDER       = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_KEY     = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_EXTRACT  = os.getenv("LLM_MODEL_EXTRACTION", "gemini-1.5-flash")
MODEL_REASON   = os.getenv("LLM_MODEL_REASONING", "gemini-1.5-pro")

# ============================================================
# GEMINI CLIENT
# ============================================================

def _gemini_call(prompt: str, model: str, temperature: float = 0.2) -> str:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)
    m = genai.GenerativeModel(
        model,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=2048,
        )
    )
    response = m.generate_content(prompt)
    return response.text

# ============================================================
# ANTHROPIC CLIENT (ready for Phase 3+ swap)
# ============================================================

def _anthropic_call(prompt: str, model: str, temperature: float = 0.2) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# ============================================================
# PUBLIC INTERFACE
# ============================================================

def extract(prompt: str, temperature: float = 0.2) -> str:
    """Call the extraction-tier model."""
    if PROVIDER == "gemini":
        return _gemini_call(prompt, MODEL_EXTRACT, temperature)
    elif PROVIDER == "anthropic":
        return _anthropic_call(prompt, MODEL_EXTRACT, temperature)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")

def reason(prompt: str, temperature: float = 0.3) -> str:
    """Call the reasoning-tier model (skeptic, validator)."""
    if PROVIDER == "gemini":
        return _gemini_call(prompt, MODEL_REASON, temperature)
    elif PROVIDER == "anthropic":
        return _anthropic_call(prompt, MODEL_REASON, temperature)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")

def parse_json_response(raw: str) -> list | dict:
    """
    Safely parse JSON from LLM output.
    LLMs often wrap JSON in markdown fences — strip them.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)

def model_info() -> dict:
    return {
        "provider": PROVIDER,
        "extraction_model": MODEL_EXTRACT,
        "reasoning_model": MODEL_REASON,
    }
