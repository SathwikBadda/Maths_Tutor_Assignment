"""
Script to build RAG index from knowledge base.
Run this after adding new markdown files to the knowledge base.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import get_config_loader
from rag.retriever import Retriever
from utils.logger import setup_logger


def main():
    """Build the RAG index."""
    print("=" * 60)
    print("Math Mentor - Build RAG Index")
    print("=" * 60)
    
    # Load configuration
    print("\n1. Loading configuration...")
    config_loader = get_config_loader()
    config = config_loader.load_config()
    
    # Setup logging
    logger = setup_logger("build_index", config.get('logging', {}))
    logger.info("Starting index build process")
    
    # Initialize retriever
    print("\n2. Initializing retriever...")
    rag_config = config.get('rag', {})
    retriever = Retriever(rag_config)
    
    # Get knowledge base path
    kb_path = rag_config.get('knowledge_base_path', './rag/knowledge_base')
    print(f"\n3. Knowledge base path: {kb_path}")
    
    # Check if knowledge base exists
    kb_dir = Path(kb_path)
    if not kb_dir.exists():
        print(f"\n❌ ERROR: Knowledge base not found at {kb_path}")
        print("Please create the knowledge base directory and add markdown files.")
        return
    
    # Count markdown files
    md_files = list(kb_dir.rglob('*.md'))
    if not md_files:
        print(f"\n❌ ERROR: No markdown files found in {kb_path}")
        print("Please add .md files to the knowledge base.")
        return
    
    print(f"\n4. Found {len(md_files)} markdown files:")
    for md_file in md_files:
        rel_path = md_file.relative_to(kb_dir)
        print(f"   - {rel_path}")
    
    # Build index
    print("\n5. Building index...")
    print("This may take a few minutes...")
    
    try:
        retriever.build_index_from_knowledge_base(kb_path)
        
        print("\n" + "=" * 60)
        print("✅ Index built successfully!")
        print("=" * 60)
        print(f"\nTotal vectors in index: {retriever.vector_store.get_count()}")
        print(f"Vector dimension: {retriever.embedder.get_dimension()}")
        print(f"\nIndex saved to: {rag_config.get('vector_db_path')}")
        
        # Test retrieval
                # Test retrieval
        print("\n6. Testing retrieval...")

        test_queries = [
            "quadratic equation formula",
            "L hopital's rule",
            "Bayes Theorem"
        ]

        def print_results(query, results):
            print("\n" + "=" * 60)
            print(f"Test query: '{query}'")
            print(f"Retrieved {len(results)} documents:")

            for i, doc in enumerate(results, 1):
                print(f"\n  {i}. Source: {doc['source']}")
                print(f"     Topic: {doc['topic']}")
                print(f"     Type: {doc['chunk_type']}")
                print(f"     Score: {doc['similarity_score']:.3f}")
                print(f"     Preview: {doc['content'][:100]}...")

        for query in test_queries:
            results = retriever.retrieve(query, top_k=3)
            print_results(query, results)

        logger.info("Index build completed successfully")

        
    except Exception as e:
        print(f"\n❌ ERROR during index build: {e}")
        logger.error(f"Index build failed: {e}", exc_info=True)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()