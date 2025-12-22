import json
import re
from typing import Tuple, Dict, Any, List

from models.llm_client import _chunk_text, _call_groq
from utils.message_formatter import format_check_message


def ai_opt_in_or_opt_out_review(
    text: str,
    rule_score: float,
    rationale: str,
    retrieved_chunks: List[str] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Enhanced AI review for consent mechanisms with detailed evidence-based analysis.

    Returns structured output showing:
    - DPDP requirements
    - Policy statements
    - Evidence from retrieved chunks
    - Gap analysis
    """

    chunks = _chunk_text(text)
    scores = []
    all_responses = []

    for chunk in chunks:
        data = _call_groq(chunk, cfg="consent_opt_in_review")

        if "final_score" in data:
            scores.append(float(data["final_score"]))

        all_responses.append(data)

    # Aggregate AI opinion
    ai_score = sum(scores) / len(scores) if scores else rule_score

    # Bias control: AI can adjust only moderately
    final_score = round((rule_score + ai_score) / 2, 2)

    passed = final_score >= 0.6

    # Build detailed message with DPDP vs Policy comparison
    best_response = all_responses[0] if all_responses else {}

    dpdp_req = best_response.get("dpdp_requirement", "Explicit, free, specific, informed, and unambiguous consent with clear affirmative action")
    policy_stmt = best_response.get("policy_statement", "Policy statement not clearly identified")

    # Format detailed message using standardized formatter
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

def ai_consent_for_training_review(
    text: str,
    rule_score: float,
    rationale: str,
    retrieved_chunks: List[str] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Enhanced AI review for separate consent for AI training.
    Provides detailed evidence-based analysis comparing DPDP requirements vs policy.
    """

    chunks = _chunk_text(text)
    scores = []
    all_responses = []

    for chunk in chunks:
        data = _call_groq(chunk, cfg="consent_training_review")

        if "final_score" in data:
            scores.append(float(data["final_score"]))

        all_responses.append(data)

    ai_score = sum(scores) / len(scores) if scores else rule_score

    # Conservative merge (rule-based still dominant)
    final_score = round((rule_score * 0.6 + ai_score * 0.4), 2)

    passed = final_score >= 0.6

    # Build detailed message with DPDP vs Policy comparison
    best_response = all_responses[0] if all_responses else {}

    dpdp_req = best_response.get("dpdp_requirement", "Purpose-specific consent for AI training, separate from general terms, with clear opt-out mechanism")
    policy_stmt = best_response.get("policy_statement", "Policy statement about training not clearly identified")

    # Format detailed message using standardized formatter
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
