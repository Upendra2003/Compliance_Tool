'''
data_minimization
    - collecting and processing only the minimum personal data that is necessary for a specific purpose
'''

import re
from utils.message_formatter import simple_format
from utils.vector_store.query_index import VectorStore
from models.ai_functions.e_data_min_verify import ai_data_minimization_review

PASS_THRESHOLD = 0.5

CHECKS = [
    {
        "id": "data_min",
        "section": "data_minimization",
        "description": "collecting and processing only the minimum personal data that is necessary for a specific purpose",
    }
]

import re

PASS_THRESHOLD = 0.5


import re

PASS_THRESHOLD = 0.5


def data_minimization_rule(doc):
    """
    Check data minimization using vector embeddings + AI.

    Returns:
        score (float), passed (bool), message (str)
    """
    vector_store = VectorStore()

    query = (
        "data collection minimum data necessary data "
        "data minimization only collect what is necessary limited data"
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
            dpdp_requirement="Only necessary personal data should be collected for specified purposes (DPDP Act Section 3)",
            finding="No data collection practices documented",
            score=0.0,
            has_evidence=False
        )

    text = context.lower()

    minimization_phrases = [
        "only necessary",
        "only what is necessary",
        "minimum amount of data",
        "data minimization",
    ]

    excessive_phrases = [
        "including but not limited to",
        "may collect additional information",
        "any information",
    ]

    has_minimization = any(p in text for p in minimization_phrases)
    has_excessive = any(p in text for p in excessive_phrases)

    if has_minimization and not has_excessive:
        rule_score = 1.0
        rationale = "Policy indicates data minimization"
    elif has_minimization and has_excessive:
        rule_score = 0.6
        rationale = "Policy claims minimization but has excessive language"
    else:
        rule_score = 0.3
        rationale = "No clear data minimization principles"

    passed, message, meta = ai_data_minimization_review(
        text=context,
        rule_score=rule_score,
        rationale=rationale,
        retrieved_chunks=retrieved_chunks[:3]
    )

    return meta["final_score"], passed, message



IMPLEMENTATIONS = {
    "data_min": data_minimization_rule,
}
