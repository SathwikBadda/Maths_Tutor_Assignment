from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging
from pathlib import Path
import os


class Embedder:
    """
    Text embedder using mixedbread-ai/mxbai-embed-large-v1.
    Uses local model if already downloaded.
    """

    def __init__(self, model_name: str = "mixedbread-ai/mxbai-embed-large-v1"):
        """
        Initialize embedder.

        Args:
            model_name: Local model path OR HuggingFace model name
        """
        self.logger = logging.getLogger("embedder")
        self.logger.info(f"Initializing embedding model: {model_name}")

        # 🔒 Force offline mode (prevents re-download)
        os.environ["HF_HUB_OFFLINE"] = "1"

        # Resolve path safely
        model_path = Path(model_name).expanduser()

        if model_path.exists():
            self.logger.info(f"Loading embedding model from local path: {model_path}")
            self.model = SentenceTransformer(str(model_path))
        else:
            # Model already cached in HF cache → load without download
            self.logger.info(
                f"Loading embedding model from HuggingFace cache (offline): {model_name}"
            )
            self.model = SentenceTransformer(model_name)

        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.logger.info(f"Embedder initialized with dimension: {self.embedding_dim}")

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text."""
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed multiple texts in batches."""
        self.logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}")
        return self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim
