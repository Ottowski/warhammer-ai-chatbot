import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_pipeline import RAGPipeline


def generate_answer_with_ollama(query: str, context_documents: list, model: str = "llama2") -> str:
    """
    Generate answer using Ollama (local LLM)
    
    Args:
        query: User's question
        context_documents: Retrieved documents
        model: Ollama model to use (llama2, mistral, etc.)
        
    Returns:
        Generated answer
    """
    try:
        import ollama
    except ImportError:
        print("Please install: pip install ollama")
        return None
    
    # Prepare context
    context = "\n\n".join(context_documents[:3])
    
    # Create prompt
    prompt = f"""You are an expert on Warhammer: The Old World rules.
Based on the following rule excerpts, provide a clear and concise answer.
Keep it to 2-3 sentences.

Rules:
{context}

Question: {query}

Answer:"""
    
    try:
        # Call Ollama
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False,
            options={
                "temperature": 0.3,
                "num_predict": 256,
            }
        )
        return response["response"].strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
        return None


def main():
    """Example: RAG with local Ollama LLM"""
    print("=" * 60)
    print("WARHAMMER: THE OLD WORLD - AI ASSISTANT (Local LLM)")
    print("=" * 60)
    print("Using Ollama for local LLM inference\n")
    
    # Initialize RAG pipeline
    rag = RAGPipeline()
    rag.initialize_knowledge_base()
    
    print("Ready! Ask a question (type 'exit' to quit):\n")
    
    while True:
        query = input("Q: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not query:
            continue
        
        # Retrieve context
        documents, metadatas = rag.retrieve_context(query, top_k=3)
        
        # Generate answer with local LLM
        print("\nThinking (using local LLM)...")
        answer = generate_answer_with_ollama(query, documents, model="llama2")
        
        if answer:
            print(f"\nA: {answer}")
            
            # Show sources
            print("\nSources:")
            for source in metadatas:
                print(f"  - {source.get('source', 'Unknown')}")
        else:
            print("Unable to generate answer")
        
        print()


if __name__ == "__main__":
    main()
