'''
deletion
    - deletion mechanism documented or not
    - offers deletion
'''

import re
from utils.message_formatter import simple_format
from utils.vector_store.query_index import VectorStore
from models.ai_functions.d_deletion_verify import ai_deletion_review

PASS_THRESHOLD = 0.5

CHECKS = [
    {
        "id": "deletion_doc",
        "section": "deletion",
        "description": "Deletion must be documented",
    },
    {
        "id": "offers_deletion",
        "section": "deletion",
        "description": "Is the provider offering the deletion option or not(both chats and account)",
    }
]

import re

PASS_THRESHOLD = 0.5


def deletion_doc(doc):
    """
    Check deletion mechanism using vector embeddings + AI.

    Returns:
        score (float), passed (bool), message (str)
    """
    vector_store = VectorStore()

    query = (
        "delete data deletion erasure remove data "
        "right to delete right to erasure delete account"
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
            dpdp_requirement="Users must have the right to delete their personal data (DPDP Act Section 12)",
            finding="No deletion mechanism documentation found",
            score=0.0,
            has_evidence=False
        )

    text = context.lower()

    deletion_keywords = [
        "delete your data",
        "data deletion",
        "erase",
        "erasure",
        "right to delete",
    ]

    found_deletion = any(k in text for k in deletion_keywords)

    if found_deletion:
        rule_score = 0.8
        rationale = "Policy documents deletion mechanism"
    else:
        rule_score = 0.0
        rationale = "No deletion mechanism found"

    passed, message, meta = ai_deletion_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]
    )

    return meta["final_score"], passed, message


def offers_deletion(doc):
    """
    Check deletion options using vector embeddings + AI.

    Returns:
        score (float), passed (bool), message (str)
    """
    vector_store = VectorStore()

    query = (
        "delete account account deletion close account "
        "delete chat delete conversations delete messages account settings"
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
            dpdp_requirement="Users must be able to delete their account and data easily (DPDP Act Section 12)",
            finding="No deletion options documented",
            score=0.0,
            has_evidence=False
        )

    text = context.lower()

    account_phrases = ["delete your account", "account deletion", "close your account"]
    data_phrases = ["delete chat", "delete conversations", "delete messages"]

    has_account = any(p in text for p in account_phrases)
    has_data = any(p in text for p in data_phrases)

    if has_account and has_data:
        rule_score = 1.0
        rationale = "Offers both account and data deletion"
    elif has_account or has_data:
        rule_score = 0.6
        rationale = "Offers partial deletion options"
    else:
        rule_score = 0.2
        rationale = "Limited deletion options"

    passed, message, meta = ai_deletion_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]
    )

    return meta["final_score"], passed, message

IMPLEMENTATIONS = {
    "deletion_doc": deletion_doc,
    "offers_deletion": offers_deletion,
}
