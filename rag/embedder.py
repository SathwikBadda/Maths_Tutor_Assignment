from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging
from pathlib import Path
import os


class Embedder:
    """
    Text embedder using mixedbread-ai/mxbai-embed-large-v1.
    Checks for model in rag/embedding_model, downloads if not present.
    """

    def __init__(self, model_name: str = "mixedbread-ai/mxbai-embed-large-v1"):
        """
        Initialize embedder.

        Args:
            model_name: HuggingFace model name (default: mixedbread-ai/mxbai-embed-large-v1)
        """
        self.logger = logging.getLogger("embedder")
        self.logger.info(f"Initializing embedding model: {model_name}")

        # Path to local embedding model directory
        local_model_dir = Path(__file__).parent / "embedding_model" / model_name.replace("/", "-")
        local_model_dir = local_model_dir.resolve()

        if local_model_dir.exists():
            self.logger.info(f"Loading embedding model from local path: {local_model_dir}")
            self.model = SentenceTransformer(str(local_model_dir))
        else:
            self.logger.info(f"Model not found locally. Downloading from HuggingFace: {model_name}")
            # Download and save model to local_model_dir
            self.model = SentenceTransformer(model_name)
            local_model_dir.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(local_model_dir))
            self.logger.info(f"Model downloaded and saved to: {local_model_dir}")

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
