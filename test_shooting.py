import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import RAGPipeline

def test_question(question: str):
    """Test a single question"""
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)
    
    # Initialize RAG pipeline
    print("\nInitializing...")
    rag = RAGPipeline(
        rules_directory="./rules",
        vector_store_path="./data/vector_store"
    )
    
    # Initialize/load vector store
    rag.initialize_knowledge_base()
    
    # Get answer
    print("Searching...")
    result = rag.answer_question(question, use_llm=False)
    
    # Display results
    print(f"\nANSWER:")
    print(result['answer'])
    
    if result['sources']:
        print(f"\nSOURCES:")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source.get('source', 'Unknown')}")
    
    print('='*60 + '\n')

if __name__ == "__main__":
    # Test with a shooting phase question
    test_question("Who can shoot?")
