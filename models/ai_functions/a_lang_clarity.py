import json
import re
from typing import Tuple, Dict, Any, List

from models.llm_client import _chunk_text, _call_groq

def evaluate_lang_clarity_ai(text: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Evaluate clarity of a policy using Groq LLM.
    Returns:
        (passed: bool, message: str, meta: dict)
    """
    chunks = _chunk_text(text, max_words=800)

    total_score = 0.0
    results = []
    unclear_count = 0

    for chunk in chunks:
        data = _call_groq(chunk,cfg="clear_language")
        score = float(data.get("score", 50))
        verdict = data.get("verdict", "Unclear")
        reasons = data.get("reasons", "")

        total_score += score
        results.append({
            "score": score,
            "verdict": verdict,
            "reasons": reasons,
        })

        if verdict.lower() != "clear":
            unclear_count += 1

    avg_score = total_score / max(len(chunks), 1)
    overall_clear = avg_score >= 60 and unclear_count <= len(chunks) // 2

    if overall_clear:
        msg = f"Language clarity score with AI {avg_score:.1f}/100 — Policy language is mostly clear."
    else:
        msg = f"Language clarity score with AI  {avg_score:.1f}/100 — Policy language may be hard to understand."

    meta = {
        "avg_score": avg_score,
        "chunks": results,
        "unclear_chunks": unclear_count,
        "total_chunks": len(chunks),
    }

    return overall_clear, msg, meta