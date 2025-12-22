"""
AI-powered verification for Deletion compliance checks
"""

import json
import re
from typing import Tuple, Dict, Any, List

from models.llm_client import _chunk_text, _call_groq
from utils.message_formatter import format_check_message


def ai_deletion_review(
    text: str,
    rule_score: float,
    rationale: str,
    retrieved_chunks: list = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    AI-based review for data deletion rights.

    Returns:
        (passed, message, metadata)
    """

    chunks = _chunk_text(text)
    scores = []
    all_responses = []

    for chunk in chunks:
        data = _call_groq(chunk, cfg="deletion_review")

        if "final_score" in data:
            scores.append(float(data["final_score"]))

        all_responses.append(data)

    # Aggregate AI opinion
    ai_score = sum(scores) / len(scores) if scores else rule_score

    # Conservative merge
    final_score = round((rule_score * 0.6 + ai_score * 0.4), 2)

    passed = final_score >= 0.5

    # Build message
    best_response = all_responses[0] if all_responses else {}

    dpdp_req = best_response.get("dpdp_requirement", "Right to delete personal data with clear mechanism")
    policy_stmt = best_response.get("policy_statement", "Policy statement not clearly identified")

    final_message = format_check_message(
        dpdp_requirement=dpdp_req,
        policy_statement=policy_stmt,
        score=final_score,
        retrieved_chunks=retrieved_chunks
    )

    metadata = {
        "rule_score": rule_score,
        "ai_score": round(ai_score, 2),
        "final_score": final_score,
        "dpdp_requirement": dpdp_req,
        "policy_statement": policy_stmt
    }

    return passed, final_message, metadata
