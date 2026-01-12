import math
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re
from collections import Counter

from rag.embedder import Embedder
from rag.vector_store import VectorStore


class BM25Retriever:
    """
    Simple local BM25 implementation for hybrid search.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.logger = logging.getLogger("bm25")
        
        self.corpus_size = 0
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.corpus = [] 
        self.metadata = [] 
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase and alphanumeric."""
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens

    def fit(self, chunks: List[str], metadata: List[Dict[str, Any]]):
        """Build BM25 index from text chunks."""
        self.logger.info(f"Fitting BM25 on {len(chunks)} documents...")
        
        self.corpus_size = len(chunks)
        self.metadata = metadata
        self.doc_len = []
        self.doc_freqs = []
        
        total_length = 0
        
        for text in chunks:
            tokens = self._tokenize(text)
            self.doc_len.append(len(tokens))
            total_length += len(tokens)
            
            frequencies = Counter(tokens)
            self.doc_freqs.append(frequencies)
            
        self.avgdl = total_length / self.corpus_size if self.corpus_size > 0 else 0
        
        self.idf = {}
        all_tokens = set()
        for d in self.doc_freqs:
            all_tokens.update(d.keys())
            
        for token in all_tokens:
            freq = sum(1 for d in self.doc_freqs if token in d)
            self.idf[token] = math.log(((self.corpus_size - freq + 0.5) / (freq + 0.5)) + 1)
            
        self.logger.info("BM25 fit complete.")

    def search(self, query: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Search for query in corpus."""
        if self.corpus_size == 0:
            return []
            
        tokens = self._tokenize(query)
        scores = [0.0] * self.corpus_size
        
        for token in tokens:
            if token not in self.idf:
                continue
                
            idf = self.idf[token]
            
            for index, doc_freqs in enumerate(self.doc_freqs):
                freq = doc_freqs.get(token, 0)
                if freq == 0:
                    continue
                    
                doc_len = self.doc_len[index]
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                scores[index] += idf * (numerator / denominator)
        
        results = list(enumerate(scores))
        results.sort(key=lambda x: x[1], reverse=True)
        
        top_results = []
        for idx, score in results[:k]:
            if score > 0:
                top_results.append((self.metadata[idx], score))
                
        return top_results

    def save(self, path: str):
        """Save BM25 index to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        self.logger.info(f"BM25 index saved to {path}")

    @staticmethod
    def load(path: str) -> 'BM25Retriever':
        """Load BM25 index from disk."""
        with open(path, 'rb') as f:
            return pickle.load(f)


TYPE_PRIORITY = {
    "solution_template": 1.0,
    "formulas": 0.9,
    "theorems": 0.7,
    "general": 0.4
}


class Retriever:
    """
    Math-safe RAG retrieval component with normalization + reranking.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("retriever")

        # ---- Embedder ----
        embedding_model = config.get("embedding_model")
        self.embedder = Embedder(embedding_model)

        # ---- Vector Store ----
        vector_db_path = config.get("vector_db_path")
        self.vector_store = VectorStore(
            embedding_dim=self.embedder.get_dimension(),
            index_path=vector_db_path
        )
        
        # ---- BM25 Retriever ----
        # User requested to store in same path. vector_db_path usually points to the storage location.
        # If vector_db_path is a directory (like faiss_index/), we save bm25.pkl inside it.
        # If it's undefined, we fallback.
        if vector_db_path:
            self.bm25_path = Path(vector_db_path) / "bm25.pkl"
        else:
            self.bm25_path = Path("rag/vector_store/bm25.pkl")
            
        self.bm25 = BM25Retriever()

        try:
            if Path(vector_db_path).exists():
                self.vector_store.load()
                self.logger.info(
                    f"Loaded vector store with {self.vector_store.get_count()} vectors"
                )
                
                # Load BM25
                if self.bm25_path.exists():
                    self.bm25 = BM25Retriever.load(self.bm25_path)
                    self.logger.info("Loaded BM25 index")
                else:
                    self.logger.warning("BM25 index not found. Will need rebuild.")
            else:
                self.logger.warning("No existing index found. Auto-building.")
                self._auto_build_if_needed()
        except Exception as e:
            self.logger.error(f"Index load failed: {e}")
            self._auto_build_if_needed()

        self.top_k = config.get("top_k", 5)

        # ⚠️ CRITICAL: math-safe threshold
        self.similarity_threshold = config.get("similarity_threshold", 0.25)

    # ------------------------------------------------------------------
    # QUERY NORMALIZATION (CRITICAL FOR MATH)
    # ------------------------------------------------------------------

    def _normalize_query(self, query: str) -> str:
        q = query.lower().replace(" ", "")

        if re.search(r"x\^2.*=.*0", q):
            return "quadratic equation ax^2 + bx + c formula roots discriminant"

        if "quadratic" in query.lower():
            return "quadratic equation formula roots discriminant"

        return query

    # ------------------------------------------------------------------
    # AUTO BUILD INDEX
    # ------------------------------------------------------------------

    def _auto_build_if_needed(self):
        kb_path = self.config.get("knowledge_base_path", "./rag/knowledge_base")
        kb_dir = Path(kb_path)

        if kb_dir.exists() and any(kb_dir.rglob("*.md")):
            self.logger.info("Building index from knowledge base...")
            self.build_index_from_knowledge_base(kb_path)

    # ------------------------------------------------------------------
    # RETRIEVAL
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        k = top_k or self.top_k
        normalized_query = self._normalize_query(query)
        self.logger.info(f"Retrieval query (normalized): {normalized_query}")

        # 1. Vector Search
        if self.vector_store.get_count() > 0:
            query_embedding = self.embedder.embed_text(normalized_query)
            vector_results = self.vector_store.search(query_embedding, k=k*2)
        else:
            vector_results = []

        # 2. BM25 Search
        # Try both original and normalized for BM25 to catch specific terms
        bm25_results_norm = self.bm25.search(normalized_query, k=k*2)
        
        # 3. Hybrid Fusion
        fused_results = self._rank_fusion(vector_results, bm25_results_norm, k=k)
        
        self.logger.info(f"Retrieved {len(fused_results)} documents after hybrid fusion")
        return fused_results

    def _rank_fusion(self, vector_results, bm25_results, k: int) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion (RRF) of Vector and BM25 results."""
        doc_scores = {}
        
        # Normalize vector scores (they are 0-1)
        # RRF: score = 1 / (const + rank)
        
        # Process Vector Results
        for rank, (metadata, score) in enumerate(vector_results):
            content = metadata.get("content")
            if content not in doc_scores:
                doc_scores[content] = {"metadata": metadata, "score": 0.0}
            doc_scores[content]["score"] += 1.0 / (60 + rank)
            
        # Process BM25 Results
        for rank, (metadata, score) in enumerate(bm25_results):
            content = metadata.get("content")
            if content not in doc_scores:
                doc_scores[content] = {"metadata": metadata, "score": 0.0}
            doc_scores[content]["score"] += 1.0 / (60 + rank)
            
        # Convert to list
        final_results = []
        for content, data in doc_scores.items():
            doc = data["metadata"].copy()
            doc["similarity_score"] = data["score"]
            final_results.append(doc)
            
        final_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return final_results[:k]

    # ------------------------------------------------------------------
    # PROBLEM-BASED RETRIEVAL
    # ------------------------------------------------------------------

    def retrieve_for_problem(self, parsed_problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve documents based on parsed problem structure.
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
        
        # Calculate retrieval confidence (simple average of top scores)
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
    
    # ------------------------------------------------------------------
    # RERANKER (DETERMINISTIC, MATH-SAFE)
    # ------------------------------------------------------------------

    def _rerank(self, results, query: str) -> List[Dict[str, Any]]:
        reranked = []

        for metadata, score in results:
            chunk_type = metadata.get("chunk_type", "general")
            type_score = TYPE_PRIORITY.get(chunk_type, 0.3)

            final_score = (
                0.6 * score +
                0.4 * type_score
            )

            reranked.append({
                "content": metadata.get("content", ""),
                "source": metadata.get("source", "unknown"),
                "topic": metadata.get("topic", ""),
                "subtopic": metadata.get("subtopic", ""),
                "chunk_type": chunk_type,
                "similarity_score": final_score
            })

        reranked.sort(key=lambda x: x["similarity_score"], reverse=True)
        return reranked

    # ------------------------------------------------------------------
    # INDEX BUILDING
    # ------------------------------------------------------------------

    def build_index_from_knowledge_base(self, kb_path: str):
        kb_dir = Path(kb_path)
        self.vector_store.clear()

        all_chunks = []
        all_metadata = []

        for topic_dir in kb_dir.iterdir():
            if not topic_dir.is_dir():
                continue

            topic = topic_dir.name

            for md_file in topic_dir.glob("*.md"):
                chunks, metadata = self._process_markdown_file(md_file, topic)
                all_chunks.extend(chunks)
                all_metadata.extend(metadata)

        if not all_chunks:
            self.logger.error("No chunks extracted. Index build aborted.")
            return

        embeddings = self.embedder.embed_batch(all_chunks)
        self.vector_store.add(embeddings, all_metadata)
        self.vector_store.save()
        
        # 2. Fit BM25
        self.logger.info("Fitting BM25 index...")
        self.bm25.fit(all_chunks, all_metadata)
        self.bm25.save(self.bm25_path)

        self.logger.info(
            f"Index built successfully: {self.vector_store.get_count()} vectors + BM25"
        )

    # ------------------------------------------------------------------
    # MARKDOWN PROCESSING (LEAF-ONLY, SEMANTIC ANCHORED)
    # ------------------------------------------------------------------

    def _process_markdown_file(
        self, file_path: Path, topic: str
    ) -> tuple[List[str], List[Dict[str, Any]]]:

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        subtopic = file_path.stem
        chunks = []
        metadata = []

        sections = re.split(r"\n## ", content)

        for section in sections:
            if not section.strip():
                continue

            lines = section.split("\n")
            title = lines[0].replace("#", "").strip()
            body = "\n".join(lines[1:]).strip()

            if not body:
                continue

            # ---- SEMANTIC ANCHOR (CRITICAL) ----
            chunk_text = (
                f"Concept: {title}. "
                f"This section explains {title}. "
                f"{body}"
            )

            chunk_type = self._determine_chunk_type(title)

            chunks.append(chunk_text)
            metadata.append({
                "content": chunk_text,
                "source": file_path.name,
                "topic": topic,
                "subtopic": subtopic,
                "chunk_type": chunk_type
            })

        return chunks, metadata

    # ------------------------------------------------------------------
    # CHUNK TYPE CLASSIFIER
    # ------------------------------------------------------------------

    def _determine_chunk_type(self, title: str) -> str:
        t = title.lower()

        if "formula" in t:
            return "formulas"
        if "solution" in t or "template" in t:
            return "solution_template"
        if "theorem" in t:
            return "theorems"
        return "general"
