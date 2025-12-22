# utils/vector_store/query_index.py

import os
import pickle
from typing import List, Dict

import faiss
import numpy as np

from utils.vector_store.embedder import Embedder


# ========= CONFIG =========

INDEX_DIR = "utils/vector_store/index"
INDEX_FILE = "policy_index.faiss"
META_FILE = "policy_metadata.pkl"


class VectorStore:
    """
    Wrapper for querying the FAISS vector index.
    """

    def __init__(self):
        index_path = os.path.join(INDEX_DIR, INDEX_FILE)
        meta_path = os.path.join(INDEX_DIR, META_FILE)

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(
                "FAISS index or metadata not found. "
                "Run build_index.py first."
            )

        # Load FAISS index
        self.index = faiss.read_index(index_path)

        # Load metadata
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)

        # Load embedder
        self.embedder = Embedder()

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        policy_filter: str | None = None
    ) -> List[Dict]:
        """
        Query the vector store.

        Args:
            query_text (str): Semantic query (e.g., consent rule)
            top_k (int): Number of chunks to retrieve
            policy_filter (str, optional): Restrict to a specific policy

        Returns:
            List[Dict]: Retrieved chunks with metadata and scores
        """
        # Embed query
        query_vec = self.embedder.embed_single(query_text)
        query_vec = np.asarray([query_vec], dtype="float32")

        # Search FAISS
        scores, indices = self.index.search(query_vec, top_k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            # Optional policy filter
            if policy_filter and meta["policy"] != policy_filter:
                continue

            results.append({
                "policy": meta["policy"],
                "chunk_id": meta["chunk_id"],
                "text": meta["text"],
                "score": float(score),
            })

            if len(results) >= top_k:
                break

        return results

    def get_context(
        self,
        query_text: str,
        top_k: int = 5,
        policy_filter: str | None = None
    ) -> str:
        """
        Get concatenated context string from Top-K chunks.

        Returns:
            str: Combined text context
        """
        results = self.query(
            query_text=query_text,
            top_k=top_k,
            policy_filter=policy_filter
        )

        context = "\n\n".join(r["text"] for r in results)
        return context
