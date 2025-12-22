# utils/vector_store/build_index.py

import os
import pickle
from typing import List, Dict

import faiss
import numpy as np

from utils.vector_store.chunker import chunk_policy_text
from utils.vector_store.embedder import Embedder


# ========= CONFIG =========

POLICIES_DIR = "policies_txt"   # folder with .md/.txt files
INDEX_DIR = "utils/vector_store/index"
INDEX_FILE = "policy_index.faiss"
META_FILE = "policy_metadata.pkl"

EMBEDDING_DIM = 768  # mpnet-base-v2


def load_policy_files(policies_dir: str) -> List[Dict]:
    """
    Load all policy files from directory.
    """
    policies = []

    for filename in os.listdir(policies_dir):
        if filename.endswith(".md") or filename.endswith(".txt"):
            policy_name = os.path.splitext(filename)[0]
            path = os.path.join(policies_dir, filename)

            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            policies.append({
                "policy": policy_name,
                "text": text
            })

    return policies


def build_index():
    """
    Build FAISS index from policy files.
    """
    os.makedirs(INDEX_DIR, exist_ok=True)

    print("[INFO] Loading policy files...")
    policies = load_policy_files(POLICIES_DIR)

    all_chunks = []
    metadata = []

    print("[INFO] Chunking policies...")
    for policy in policies:
        chunks = chunk_policy_text(
            text=policy["text"],
            policy_name=policy["policy"]
        )

        for chunk in chunks:
            all_chunks.append(chunk["text"])
            metadata.append({
                "policy": chunk["policy"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"]
            })

    print(f"[INFO] Total chunks created: {len(all_chunks)}")

    if not all_chunks:
        raise ValueError("No chunks created. Check policy files.")

    print("[INFO] Loading embedding model...")
    embedder = Embedder()

    print("[INFO] Generating embeddings...")
    embeddings = embedder.embed_texts(all_chunks)
    embeddings = np.asarray(embeddings, dtype="float32")

    print("[INFO] Building FAISS index...")
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)

    print(f"[SUCCESS] FAISS index size: {index.ntotal}")

    # Save index
    index_path = os.path.join(INDEX_DIR, INDEX_FILE)
    faiss.write_index(index, index_path)

    # Save metadata
    meta_path = os.path.join(INDEX_DIR, META_FILE)
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)

    print("[SUCCESS] Index and metadata saved successfully")
    print(f"   - Index: {index_path}")
    print(f"   - Metadata: {meta_path}")


if __name__ == "__main__":
    build_index()
