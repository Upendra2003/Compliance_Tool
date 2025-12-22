# utils/vector_store/embedder.py

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Wrapper around sentence-transformers embedding model.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        device: str = "cpu"
    ):
        """
        Initialize the embedding model.

        Args:
            model_name (str): HuggingFace model name
            device (str): 'cpu' or 'cuda'
        """
        self.model = SentenceTransformer(model_name, device=device)

    def embed_texts(
        self,
        texts: List[str],
        batch_size: int = 16
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.

        Args:
            texts (List[str]): List of text chunks
            batch_size (int): Batch size for encoding

        Returns:
            np.ndarray: Shape (num_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        return np.array(embeddings)

    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.

        Args:
            text (str): Input text

        Returns:
            np.ndarray: Shape (embedding_dim,)
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return np.array(embedding)
