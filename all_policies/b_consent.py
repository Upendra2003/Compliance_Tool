'''
Consent
    - Opt-in vs Opt-out mechanism
    - Separate consent for training (Y/N)
'''

from models.ai_functions.b_consent_verify import ai_opt_in_or_opt_out_review, ai_consent_for_training_review
from utils.vector_store.query_index import VectorStore

CHECKS = [
    {
        "id": "opt_in_or_opt_out",
        "section": "Consent",
        "description": "Entity must provide a privacy notice to the data principal",
    },
    {
        "id": "consent_for_training",
        "section": "Consent",
        "description": "Notice should be in clear and plain language",
    }
]

def rule_opt_in_or_opt_out(doc):
    text = doc.get("text", "").lower()

    # Signal buckets
    explicit_opt_in_signals = [
        "explicit consent",
        "affirmative action",
        "checkbox",
        "tick the box",
        "you choose to agree",
        "opt in",
        "actively consent"
    ]

    opt_out_signals = [
        "opt out",
        "disable",
        "withdraw consent",
        "manage preferences",
        "turn off"
    ]

    implicit_consent_signals = [
        "by using our service",
        "by using this service",
        "continued use constitutes consent",
        "your continued use",
        "use of the service means you agree"
    ]

    found_explicit = any(p in text for p in explicit_opt_in_signals)
    found_opt_out = any(p in text for p in opt_out_signals)
    found_implicit = any(p in text for p in implicit_consent_signals)

    # Scoring logic
    if found_explicit and not found_implicit:
        score = 1.0
        rationale = "Policy describes explicit opt-in consent through clear affirmative action."

    elif found_explicit and found_opt_out:
        score = 0.7
        rationale = "Policy provides user choice with opt-in and opt-out mechanisms."

    elif found_implicit and found_opt_out:
        score = 0.4
        rationale = "Consent appears implicit, with opt-out mechanisms available."

    elif found_opt_out and not found_explicit:
        score = 0.3
        rationale = "Consent relies primarily on opt-out rather than explicit opt-in."

    elif found_implicit:
        score = 0.4
        rationale = "Consent is implied through service usage without clear affirmative action."

    else:
        score = 0.0
        rationale = "No clear consent mechanism detected in the policy."

    return score, rationale


def rule_consent_for_training(doc):
    """
    Rule-based detection of separate consent for AI training or model improvement.

    Returns:
        (score: float, rationale: str)
    """
    text = doc.get("text", "").lower()

    training_keywords = [
        "training",
        "model improvement",
        "improve our models",
        "machine learning",
        "ai systems",
        "research and development",
        "learning algorithms"
    ]

    consent_keywords = [
        "consent",
        "opt in",
        "opt out",
        "permission",
        "your choice",
        "manage preferences"
    ]

    implicit_usage_signals = [
        "we may use your data to improve",
        "used to enhance our services",
        "help improve our products"
    ]

    found_training = any(k in text for k in training_keywords)
    found_consent_nearby = any(k in text for k in consent_keywords)
    found_implicit = any(p in text for p in implicit_usage_signals)

    # Scoring logic
    if found_training and found_consent_nearby:
        score = 0.6
        rationale = (
            "Policy mentions use of data for AI training with user choice, "
            "but consent appears bundled with general consent."
        )

    elif found_training and found_implicit:
        score = 0.2
        rationale = (
            "Policy implies use of data for AI training without explicit or separate consent."
        )

    elif found_training:
        score = 0.4
        rationale = (
            "Policy mentions AI training or model improvement but does not clearly describe user consent."
        )

    else:
        score = 0.0
        rationale = "Policy does not mention use of data for AI training or model improvement."

    return score, rationale


def check_opt_in_or_opt_out(doc):
    """
    DPDP Consent Check with Vector Embeddings + AI Analysis

    Flow:
    1. Semantic search for consent-related sections
    2. Rule-based scoring on retrieved context
    3. AI analysis with DPDP vs Policy comparison
    4. Evidence-based detailed report
    """
    vector_store = VectorStore()

    query = (
        "opt-in consent opt-out consent user agreement "
        "acceptance by continuing use consent mechanism"
    )

    # Get detailed results (not just concatenated text)
    results = vector_store.query(
        query_text=query,
        top_k=6,
        policy_filter=doc["policy"]
    )

    # Extract chunks for evidence
    retrieved_chunks = [r["text"] for r in results]
    context = "\n\n".join(retrieved_chunks)

    # Fallback if no relevant context found
    if not context.strip():
        return 0.0, False, (
            "**ERROR:** No consent mechanism documentation found in policy. "
            "DPDP Act requires explicit consent mechanisms to be clearly documented."
        )

    # Rule-based evaluation on retrieved context
    context_doc = {
        "policy": doc["policy"],
        "text": context
    }

    rule_score, rationale = rule_opt_in_or_opt_out(context_doc)

    # AI analysis with evidence
    passed, message, meta = ai_opt_in_or_opt_out_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]  # Top 3 for evidence display
    )

    return meta["final_score"], passed, message


def check_consent_for_training(doc):
    """
    DPDP Consent Check with Vector Embeddings + AI Analysis
    Focus: Separate consent for AI model training

    Flow:
    1. Semantic search for training-related sections
    2. Rule-based scoring on retrieved context
    3. AI analysis with DPDP vs Policy comparison
    4. Evidence-based detailed report
    """

    vector_store = VectorStore()

    # Semantic query tuned for training consent
    query = (
        "training data machine learning model improvement "
        "use of personal data for training opt-out training consent"
    )

    # Get detailed results (not just concatenated text)
    results = vector_store.query(
        query_text=query,
        top_k=5,
        policy_filter=doc["policy"]
    )

    # Extract chunks for evidence
    retrieved_chunks = [r["text"] for r in results]
    context = "\n\n".join(retrieved_chunks)

    # Fallback if no relevant context found
    if not context.strip():
        return 0.0, False, (
            "**ERROR:** No documentation found about data usage for AI training. "
            "DPDP Act requires purpose-specific consent disclosure for AI model training."
        )

    # Rule-based evaluation on retrieved context
    rule_score, rationale = rule_consent_for_training({
        "text": context
    })

    # AI analysis with evidence
    passed, message, meta = ai_consent_for_training_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]  # Top 3 for evidence display
    )

    final_score = meta.get("final_score", rule_score)

    return final_score, passed, message

IMPLEMENTATIONS = {
    "opt_in_or_opt_out": check_opt_in_or_opt_out,
    "consent_for_training": check_consent_for_training,
}