import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging


class VectorStore:
    """
    FAISS-based vector store for semantic search.
    """
    
    def __init__(self, embedding_dim: int, index_path: str = None):
        """
        Initialize vector store.
        
        Args:
            embedding_dim: Dimension of embeddings
            index_path: Path to save/load index
        """
        self.logger = logging.getLogger("vector_store")
        self.embedding_dim = embedding_dim
        self.index_path = Path(index_path) if index_path else None
        
        # Initialize FAISS index (using L2 distance)
        self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Metadata storage (maps index -> document metadata)
        self.metadata = []
        
        self.logger.info(f"Vector store initialized with dimension: {embedding_dim}")
    
    def add(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Add embeddings and metadata to the store.
        
        Args:
            embeddings: Array of embeddings (n_docs, embedding_dim)
            metadata: List of metadata dicts for each embedding
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        
        # Store metadata
        self.metadata.extend(metadata)
        
        self.logger.info(f"Added {len(embeddings)} embeddings. Total: {self.index.ntotal}")
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        similarity_threshold: float = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            similarity_threshold: Optional threshold for filtering results
        
        Returns:
            List of (metadata, similarity_score) tuples
        """
        if self.index.ntotal == 0:
            self.logger.warning("Vector store is empty")
            return []
        
        # Ensure query is 2D and float32
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Convert distances to similarity scores (lower L2 distance = higher similarity)
        # Normalize: similarity = 1 / (1 + distance)
        similarities = 1 / (1 + distances[0])
        
        # Collect results
        results = []
        for idx, sim in zip(indices[0], similarities):
            if idx < len(self.metadata):
                # Apply threshold if specified
                if similarity_threshold is None or sim >= similarity_threshold:
                    results.append((self.metadata[idx], float(sim)))
        
        self.logger.info(f"Search returned {len(results)} results")
        return results
    
    def save(self, path: str = None):
        """
        Save index and metadata to disk.
        
        Args:
            path: Optional path override
        """
        save_path = Path(path) if path else self.index_path
        if not save_path:
            raise ValueError("No save path specified")
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = save_path / "faiss.index"
        faiss.write_index(self.index, str(index_file))
        
        # Save metadata
        metadata_file = save_path / "metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        self.logger.info(f"Vector store saved to {save_path}")
    
    def load(self, path: str = None):
        """
        Load index and metadata from disk.
        
        Args:
            path: Optional path override
        """
        load_path = Path(path) if path else self.index_path
        if not load_path:
            raise ValueError("No load path specified")
        
        # Load FAISS index
        index_file = load_path / "faiss.index"
        if index_file.exists():
            self.index = faiss.read_index(str(index_file))
            self.logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
        else:
            self.logger.warning(f"Index file not found: {index_file}")
        
        # Load metadata
        metadata_file = load_path / "metadata.pkl"
        if metadata_file.exists():
            with open(metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
            self.logger.info(f"Loaded {len(self.metadata)} metadata entries")
        else:
            self.logger.warning(f"Metadata file not found: {metadata_file}")
    
    def clear(self):
        """Clear all data from the store."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []
        self.logger.info("Vector store cleared")
    
    def get_count(self) -> int:
        """Get number of vectors in store."""
        return self.index.ntotal