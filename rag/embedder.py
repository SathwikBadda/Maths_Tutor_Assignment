from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging


class Embedder:
    """
    Text embedder using all-MiniLM-L6-v2.
    Uses HuggingFace cache (Streamlit-safe).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.logger = logging.getLogger("embedder")
        self.logger.info(f"Loading embedding model from HuggingFace: {model_name}")

        # ✅ DO NOT use local paths
        # ✅ Let HF cache handle it
        self.model = SentenceTransformer(
            model_name,
            device="cpu"
        )

        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.logger.info(f"Embedder initialized with dimension: {self.embedding_dim}")

    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        self.logger.info(f"Embedding {len(texts)} texts")
        return self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    def get_dimension(self) -> int:
        return self.embedding_dim
