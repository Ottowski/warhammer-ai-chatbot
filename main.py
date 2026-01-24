"""
Warhammer: The Old World - AI Rules Assistant
Main entry point for the RAG-based chatbot

Run with: python main.py
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import RAGPipeline


def print_header():
    """Print application header"""
    print("\n" + "=" * 60)
    print("WARHAMMER: THE OLD WORLD - AI RULES ASSISTANT")
    print("=" * 60)
    print("Ask questions about the rules in natural language")
    print("Type 'exit' or 'quit' to quit\n")


def format_answer(result: dict):
    """Format and print the answer with sources"""
    print("\n" + "-" * 60)
    print(f"Q: {result['query']}\n")
    
    print("ANSWER:")
    print(result['answer'])
    
    if result['sources']:
        print("\n" + "-" * 60)
        print("SOURCES:")
        for i, source in enumerate(result['sources'], 1):
            source_file = source.get('source', 'Unknown')
            print(f"  {i}. {source_file}")
    
    print("-" * 60 + "\n")


def main():
    """Main application loop"""
    print_header()
    
    # Initialize RAG pipeline
    print("Loading knowledge base...")
    try:
        rag = RAGPipeline(
            rules_directory="./rules",
            vector_store_path="./data/vector_store"
        )
        
        # Initialize/load vector store and documents
        # Note: On first run, this will download embeddings and build the store
        rag.initialize_knowledge_base()
        
    except Exception as e:
        print(f"Error initializing knowledge base: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Python 3.11+ is installed")
        print("2. Run: pip install -r requirements.txt")
        print("3. Add .md or .txt files to the ./rules directory")
        return
    
    print("✓ Ready to answer questions!\n")
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_question = input("Your question: ").strip()
            
            # Check for exit commands
            if user_question.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_question:
                print("Please enter a question.\n")
                continue
            
            # Process question through RAG pipeline
            print("\nSearching knowledge base...")
            result = rag.answer_question(user_question, use_llm=False)
            
            # Display answer and sources
            format_answer(result)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error processing question: {e}\n")


if __name__ == "__main__":
    main()
