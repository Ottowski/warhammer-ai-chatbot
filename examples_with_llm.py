"""
Example: Integrating OpenAI LLM with the RAG Pipeline

This is an optional enhancement. To use this:

1. Get an API key from https://platform.openai.com/api-keys
2. Install: pip install openai langchain langchain-openai
3. Set environment variable: 
   - Windows PowerShell: $env:OPENAI_API_KEY = "your-key-here"
   - Windows CMD: set OPENAI_API_KEY=your-key-here
   - Linux/Mac: export OPENAI_API_KEY="your-key-here"
4. Run: python examples/with_llm.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_pipeline import RAGPipeline


def generate_answer_with_llm(query: str, context_documents: list) -> str:
    """
    Generate an answer using OpenAI's GPT-3.5-turbo
    
    Args:
        query: User's question
        context_documents: Retrieved relevant documents from vector store
        
    Returns:
        Generated answer from LLM
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
    except ImportError:
        print("Please install: pip install openai langchain langchain-openai")
        return None
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return None
    
    # Prepare context
    context = "\n\n".join(context_documents[:3])
    
    # Create prompt template
    prompt_template = """You are an expert on Warhammer: The Old World rules. 
Based on the following rule excerpts, provide a clear and concise answer to the question.
Keep your answer to 2-3 sentences and cite the relevant rules.

Rule excerpts:
{context}

Question: {query}

Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "query"]
    )
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        max_tokens=512
    )
    
    # Create chain and run
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(context=context, query=query)
    
    return response.strip()


def main():
    """Example: RAG with LLM-generated answers"""
    print("=" * 60)
    print("WARHAMMER: THE OLD WORLD - AI ASSISTANT (with LLM)")
    print("=" * 60)
    print("Using OpenAI's GPT-3.5-turbo for answer generation\n")
    
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
        
        # Generate answer with LLM
        print("\nThinking...")
        answer = generate_answer_with_llm(query, documents)
        
        if answer:
            print(f"\nA: {answer}")
            
            # Show sources
            print("\nSources:")
            for source in metadatas:
                print(f"  - {source.get('source', 'Unknown')}")
        else:
            print("Unable to generate answer (check API key and connection)")
        
        print()


if __name__ == "__main__":
    main()
