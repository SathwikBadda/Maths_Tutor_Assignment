from pathlib import Path
from typing import List, Dict, Any
import logging
import re

from rag.embedder import Embedder
from rag.vector_store import VectorStore


class Retriever:
    """
    RAG retrieval component that combines embedder and vector store.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize retriever.
        
        Args:
            config: RAG configuration
        """
        self.config = config
        self.logger = logging.getLogger("retriever")
        
        # Initialize embedder
        embedding_model = config.get('embedding_model')
        self.embedder = Embedder(embedding_model)
        
        # Initialize vector store
        vector_db_path = config.get('vector_db_path')
        self.vector_store = VectorStore(
            embedding_dim=self.embedder.get_dimension(),
            index_path=vector_db_path
        )
        
        # Load existing index if available
        if Path(vector_db_path).exists():
            try:
                self.vector_store.load()
                self.logger.info(f"Loaded vector store with {self.vector_store.get_count()} vectors")
            except Exception as e:
                self.logger.warning(f"Failed to load vector store: {e}")
        
        self.top_k = config.get('top_k', 5)
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results (overrides config)
        
        Returns:
            List of retrieved documents with metadata
        """
        k = top_k if top_k is not None else self.top_k
        
        self.logger.info(f"Retrieving top-{k} documents for query: {query[:50]}...")
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            k=k,
            similarity_threshold=self.similarity_threshold
        )
        
        # Format results
        retrieved_docs = []
        for metadata, score in results:
            doc = {
                "content": metadata.get("content", ""),
                "source": metadata.get("source", "unknown"),
                "topic": metadata.get("topic", ""),
                "subtopic": metadata.get("subtopic", ""),
                "similarity_score": score
            }
            retrieved_docs.append(doc)
        
        self.logger.info(
            f"Retrieved {len(retrieved_docs)} documents, "
            f"top score: {retrieved_docs[0]['similarity_score']:.3f if retrieved_docs else 0}"
        )
        
        return retrieved_docs
    
    def retrieve_for_problem(self, parsed_problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve documents based on parsed problem structure.
        
        Args:
            parsed_problem: Parsed problem from parser agent
        
        Returns:
            Dictionary with retrieved context and metadata
        """
        # Build query from problem components
        query_parts = [parsed_problem.get("problem_text", "")]
        
        # Add topic/subtopic for better retrieval
        if "topic" in parsed_problem:
            query_parts.append(parsed_problem["topic"])
        if "subtopic" in parsed_problem:
            query_parts.append(parsed_problem["subtopic"])
        
        query = " ".join(query_parts)
        
        # Retrieve documents
        retrieved_docs = self.retrieve(query)
        
        # Calculate retrieval confidence
        if retrieved_docs:
            avg_score = sum(d["similarity_score"] for d in retrieved_docs) / len(retrieved_docs)
            retrieval_confidence = avg_score
        else:
            retrieval_confidence = 0.0
        
        # Extract unique sources
        sources = list(set(d["source"] for d in retrieved_docs))
        
        return {
            "retrieved_context": retrieved_docs,
            "retrieval_confidence": retrieval_confidence,
            "retrieval_sources": sources,
            "retrieval_query": query
        }
    
    def build_index_from_knowledge_base(self, kb_path: str):
        """
        Build vector index from knowledge base markdown files.
        
        Args:
            kb_path: Path to knowledge base directory
        """
        self.logger.info(f"Building index from knowledge base: {kb_path}")
        
        kb_dir = Path(kb_path)
        if not kb_dir.exists():
            raise ValueError(f"Knowledge base path not found: {kb_path}")
        
        # Clear existing index
        self.vector_store.clear()
        
        # Process all markdown files
        all_chunks = []
        all_metadata = []
        
        for topic_dir in kb_dir.iterdir():
            if not topic_dir.is_dir():
                continue
            
            topic = topic_dir.name
            self.logger.info(f"Processing topic: {topic}")
            
            for md_file in topic_dir.glob("*.md"):
                chunks, metadata = self._process_markdown_file(md_file, topic)
                all_chunks.extend(chunks)
                all_metadata.extend(metadata)
        
        self.logger.info(f"Total chunks: {len(all_chunks)}")
        
        # Embed all chunks
        embeddings = self.embedder.embed_batch(all_chunks)
        
        # Add to vector store
        self.vector_store.add(embeddings, all_metadata)
        
        # Save index
        self.vector_store.save()
        
        self.logger.info("Index building complete")
    
    def _process_markdown_file(
        self,
        file_path: Path,
        topic: str
    ) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        Process a markdown file into chunks.
        
        Args:
            file_path: Path to markdown file
            topic: Topic name
        
        Returns:
            Tuple of (chunks, metadata)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract subtopic from filename
        subtopic = file_path.stem
        
        # Split by headers (## Level 2 headers)
        sections = re.split(r'\n## ', content)
        
        chunks = []
        metadata = []
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Add header back if not first section
            if i > 0:
                section = "## " + section
            
            # Create chunks (simple split for now, can be improved)
            chunk_size = self.config.get('chunk_size', 512)
            words = section.split()
            
            for j in range(0, len(words), chunk_size):
                chunk = " ".join(words[j:j + chunk_size])
                
                chunks.append(chunk)
                metadata.append({
                    "content": chunk,
                    "source": str(file_path.name),
                    "topic": topic,
                    "subtopic": subtopic,
                    "chunk_index": j // chunk_size
                })
        
        return chunks, metadata