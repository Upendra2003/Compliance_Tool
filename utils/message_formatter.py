"""
Standardized Message Formatter for DPDP Compliance Checks

Ensures all checks return consistent, structured messages showing:
- DPDP Rule/Requirement
- What the provider's policy says
- Evidence/Proof
- Score
"""

def format_check_message(
    dpdp_requirement: str,
    policy_statement: str = None,
    score: float = 0.0,
    retrieved_chunks: list = None
) -> str:
    """
    Format a standardized compliance check message.

    Args:
        dpdp_requirement: What DPDP Act requires
        policy_statement: What the provider's policy states
        score: Compliance score (0.0 to 1.0)
        retrieved_chunks: Top matching chunks from vector search

    Returns:
        HTML-formatted message string
    """

    sections = []

    # DPDP Requirement
    sections.append(f'<div class="msg-section msg-dpdp">'
                   f'<div class="msg-label">DPDP Requirement:</div>'
                   f'<div class="msg-content">{dpdp_requirement}</div>'
                   f'</div>')

    # Policy statement
    if policy_statement and policy_statement.strip():
        sections.append(f'<div class="msg-section msg-policy">'
                       f'<div class="msg-label">Provider\'s Policy:</div>'
                       f'<div class="msg-content">{policy_statement}</div>'
                       f'</div>')
    else:
        sections.append(f'<div class="msg-section msg-policy msg-missing">'
                       f'<div class="msg-label">Provider\'s Policy:</div>'
                       f'<div class="msg-content msg-empty">No relevant policy statement found</div>'
                       f'</div>')

    # Retrieved chunks (evidence from vector search)
    if retrieved_chunks and len(retrieved_chunks) > 0:
        chunks_html = '<div class="msg-chunks">'
        for i, chunk in enumerate(retrieved_chunks[:3], 1):
            chunk_preview = chunk[:300] + "..." if len(chunk) > 300 else chunk
            chunks_html += f'<div class="msg-chunk"><strong>[Evidence {i}]</strong> {chunk_preview}</div>'
        chunks_html += '</div>'

        sections.append(f'<div class="msg-section msg-retrieved">'
                       f'<div class="msg-label">Retrieved Evidence (Top Matches):</div>'
                       f'<div class="msg-content">{chunks_html}</div>'
                       f'</div>')
    else:
        sections.append(f'<div class="msg-section msg-retrieved msg-missing">'
                       f'<div class="msg-label">Retrieved Evidence:</div>'
                       f'<div class="msg-content msg-empty">No evidence chunks available</div>'
                       f'</div>')

    # Score
    score_percent = score * 100
    score_class = 'score-high' if score >= 0.75 else 'score-medium' if score >= 0.5 else 'score-low'
    sections.append(f'<div class="msg-section msg-score">'
                   f'<div class="msg-label">Compliance Score:</div>'
                   f'<div class="msg-content"><span class="{score_class}">{score_percent:.1f}%</span></div>'
                   f'</div>')

    return ''.join(sections)


def simple_format(
    dpdp_requirement: str,
    finding: str,
    score: float,
    has_evidence: bool = True
) -> str:
    """
    Simplified formatter for rule-based checks without AI analysis.

    Args:
        dpdp_requirement: What DPDP requires
        finding: What was found in the policy
        score: Compliance score
        has_evidence: Whether evidence was found

    Returns:
        HTML-formatted message string
    """

    evidence_text = finding if has_evidence else "No evidence found in policy"
    evidence_class = "" if has_evidence else "msg-missing"

    sections = []

    sections.append(f'<div class="msg-section msg-dpdp">'
                   f'<div class="msg-label">DPDP Requirement:</div>'
                   f'<div class="msg-content">{dpdp_requirement}</div>'
                   f'</div>')

    sections.append(f'<div class="msg-section msg-finding {evidence_class}">'
                   f'<div class="msg-label">Finding:</div>'
                   f'<div class="msg-content">{evidence_text}</div>'
                   f'</div>')

    score_percent = score * 100
    score_class = 'score-high' if score >= 0.75 else 'score-medium' if score >= 0.5 else 'score-low'
    sections.append(f'<div class="msg-section msg-score">'
                   f'<div class="msg-label">Compliance Score:</div>'
                   f'<div class="msg-content"><span class="{score_class}">{score_percent:.1f}%</span></div>'
                   f'</div>')

    return ''.join(sections)
