# utils/vector_store/chunker.py

import re
from typing import List, Dict

from utils.utils import get_policy_doc

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using simple regex.
    Works reasonably well for legal / policy text.
    """
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Clean sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    return sentences


def chunk_sentences(
    sentences: List[str],
    policy_name: str,
    min_sentences: int = 2,
    max_sentences: int = 4
) -> List[Dict]:
    """
    Group sentences into chunks of 2–4 sentences.

    Returns a list of chunks with metadata.
    """
    chunks = []
    chunk_id = 0
    i = 0

    while i < len(sentences):
        chunk_size = min(max_sentences, len(sentences) - i)

        if chunk_size < min_sentences:
            break

        chunk_text = " ".join(sentences[i:i + chunk_size])

        chunks.append({
            "chunk_id": chunk_id,
            "policy": policy_name,
            "text": chunk_text
        })

        chunk_id += 1
        i += chunk_size

    return chunks


def chunk_policy_text(text: str, policy_name: str) -> List[Dict]:
    """
    Full pipeline: text → sentences → chunks
    """
    sentences = split_into_sentences(text)
    chunks = chunk_sentences(sentences, policy_name)
    return chunks
