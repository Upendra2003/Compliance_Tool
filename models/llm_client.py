import os
from pathlib import Path
from typing import Tuple, Dict, Any, List
import json
import re

import yaml
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_PATH = BASE_DIR / "prompts.yaml"

with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

PROMPTS = CONFIG.get("prompts", {})
MODEL_CONFIG = CONFIG.get("models", {})

_groq_client = None

def get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def get_prompt(name: str) -> dict:
    """
    Return a prompt config dict, e.g. PROMPTS['clear_language'].
    """
    if name not in PROMPTS:
        raise KeyError(f"Prompt '{name}' not found in prompts.yaml")
    return PROMPTS[name]

def get_model_name(purpose: str) -> str:
    """
    Get model name for a given purpose, e.g. 'clarity'.
    """
    cfg = MODEL_CONFIG.get(purpose, {})
    model = cfg.get("model")
    if not model:
        raise KeyError(f"No model configured for purpose '{purpose}' in prompts.yaml")
    return model

def _chunk_text(text: str, max_words: int = 800) -> List[str]:
    """
    Split text into chunks of ~max_words words.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def _call_groq(chunk: str, cfg: str) -> Dict[str, Any]:
    """
    Call Groq API for a single chunk and return parsed JSON response.
    """
    client = get_groq_client()
    prompt_cfg = get_prompt(cfg)
    model_name = get_model_name("clarity")

    system_msg = prompt_cfg["system"]
    user_template = prompt_cfg["user_template"]
    user_msg = user_template.replace("{{text}}", chunk)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.0,
    )

    content = response.choices[0].message.content.strip()

    # Attempt to parse JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to extract with regex if model added extra text
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse JSON from model output: {content}")
        data = json.loads(match.group(0))

    return data
