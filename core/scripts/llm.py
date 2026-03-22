"""
OHARA — LLM Client
Provider-agnostic. Swap via LLM_PROVIDER in .env.
Aktuell: google-genai SDK mit gemini-2.5-flash-lite
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

LLM_PROVIDER         = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")
EXTRACTION_MODEL     = os.getenv("LLM_EXTRACTION_MODEL", "gemini-2.5-flash-lite")
REASONING_MODEL      = os.getenv("LLM_REASONING_MODEL", "gemini-2.5-flash-lite")

def model_info() -> dict:
    return {
        "provider": LLM_PROVIDER,
        "extraction_model": EXTRACTION_MODEL,
        "reasoning_model": REASONING_MODEL,
    }

def _call_gemini(prompt: str, model: str) -> str:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text

def extract(prompt: str) -> str:
    if LLM_PROVIDER == "gemini":
        return _call_gemini(prompt, EXTRACTION_MODEL)
    raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")

def reason(prompt: str) -> str:
    if LLM_PROVIDER == "gemini":
        return _call_gemini(prompt, REASONING_MODEL)
    raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")

def parse_json_response(text: str) -> list | dict:
    text = text.strip()
    # Strip markdown fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON array from text
        import re
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
