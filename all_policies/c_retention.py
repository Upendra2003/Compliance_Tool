'''
retention
    - retention periods specified
    - specific timeframe is mentioned or not
'''

import re
from utils.message_formatter import simple_format
from utils.vector_store.query_index import VectorStore
from models.ai_functions.c_retention_verify import ai_retention_review

PASS_THRESHOLD = 0.5

CHECKS = [
    {
        "id": "retention_period",
        "section": "retention",
        "description": "Entity must provide a retention period to the users",
    },
    {
        "id": "specific_timeframe",
        "section": "retention",
        "description": "",
    }
]

def check_retention_period(doc):
    """
    Check data retention using vector embeddings + AI analysis.

    Flow:
    1. Semantic search for retention-related sections
    2. Rule-based scoring on retrieved context
    3. AI analysis with final decision

    Returns:
        score (float), passed (bool), message (str)
    """
    vector_store = VectorStore()

    query = (
        "data retention retention period storage period "
        "how long data is kept delete data after"
    )

    # Get detailed results from vector search
    results = vector_store.query(
        query_text=query,
        top_k=5,
        policy_filter=doc["policy"]
    )

    # Extract chunks
    retrieved_chunks = [r["text"] for r in results]
    context = "\n\n".join(retrieved_chunks)

    # Fallback if no relevant context
    if not context.strip():
        return 0.0, False, simple_format(
            dpdp_requirement="Data must only be retained for as long as necessary for the purpose (DPDP Act Section 8)",
            finding="No retention policy documentation found",
            score=0.0,
            has_evidence=False
        )

    # Rule-based evaluation on context
    text = context.lower()

    retention_keywords = [
        "retain",
        "retention",
        "stored for",
        "storage period",
        "data is kept",
        "we keep your data",
    ]

    vague_phrases = [
        "as long as necessary",
        "for as long as needed",
        "as required by law",
    ]

    found_retention = any(k in text for k in retention_keywords)
    found_vague_only = any(p in text for p in vague_phrases)

    if found_retention and not found_vague_only:
        rule_score = 1.0
        rationale = "Policy clearly mentions data retention practices"
    elif found_retention and found_vague_only:
        rule_score = 0.5
        rationale = "Policy mentions retention but uses vague language"
    else:
        rule_score = 0.0
        rationale = "Policy does not mention retention practices"

    # AI analysis
    passed, message, meta = ai_retention_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]
    )

    return meta["final_score"], passed, message


def check_specific_timeframe(doc):
    """
    Check specific retention timeframes using vector embeddings + AI.

    Returns:
        score (float), passed (bool), message (str)
    """
    vector_store = VectorStore()

    query = (
        "retention period days months years specific timeframe "
        "delete after account closure purpose fulfilled"
    )

    results = vector_store.query(
        query_text=query,
        top_k=5,
        policy_filter=doc["policy"]
    )

    retrieved_chunks = [r["text"] for r in results]
    context = "\n\n".join(retrieved_chunks)

    if not context.strip():
        return 0.0, False, simple_format(
            dpdp_requirement="Specific retention periods must be documented (DPDP Act Section 8)",
            finding="No specific timeframe documentation found",
            score=0.0,
            has_evidence=False
        )

    text = context.lower()

    # Detect timeframes
    timeframe_patterns = [
        r"\b\d+\s*(day|days|month|months|year|years)\b",
        r"within\s+\d+\s*(day|days|month|months|year|years)",
    ]

    conditional_phrases = [
        "upon account deletion",
        "after account closure",
        "when the purpose is fulfilled",
    ]

    has_explicit = any(re.search(p, text) for p in timeframe_patterns)
    has_conditional = any(p in text for p in conditional_phrases)

    if has_explicit:
        rule_score = 1.0
        rationale = "Policy specifies concrete retention timeframes"
    elif has_conditional:
        rule_score = 0.6
        rationale = "Policy specifies conditional retention limits"
    else:
        rule_score = 0.2
        rationale = "No specific timeframes found"

    passed, message, meta = ai_retention_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]
    )

    return meta["final_score"], passed, message

IMPLEMENTATIONS = {
    "retention_period": check_retention_period,
    "specific_timeframe": check_specific_timeframe,
}