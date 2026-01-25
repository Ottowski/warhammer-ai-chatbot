from typing import List, Tuple
import numpy as np
from src.embeddings import EmbeddingManager
from src.document_loader import DocumentLoader

class RAGPipeline:
    """Main RAG pipeline for question answering"""
    
    def __init__(self, rules_directory: str = "./rules", vector_store_path: str = "./data/vector_store"):
        """
        Initialize RAG pipeline
        
        Args:
            rules_directory: Path to rules documents
            vector_store_path: Path for storing embeddings
        """
        # Initialize components
        self.embedding_manager = EmbeddingManager()
        self.document_loader = DocumentLoader(rules_directory=rules_directory)
        
        # In-memory storage for documents and embeddings
        self.documents = []
        self.embeddings = None
        self.metadatas = []
    
    def initialize_knowledge_base(self, force_rebuild: bool = False):
        """
        Load documents and build in-memory embedding store
        
        Args:
            force_rebuild: If True, rebuild the store from scratch
        """
        print("Initializing knowledge base...")
        
        # Load documents
        documents, metadatas, ids = self.document_loader.load_all_documents()
        
        if not documents:
            print("Warning: No documents loaded!")
            return
        
        # Store documents and metadata
        self.documents = documents
        self.metadatas = metadatas
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings_list = self.embedding_manager.embed_texts(documents)
        self.embeddings = np.array(embeddings_list)
        
        print(f"Loaded {len(documents)} documents with embeddings")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> Tuple[List[str], List[dict]]:
        """
        Retrieve relevant context for a query using cosine similarity
        
        Args:
            query: User's question
            top_k: Number of top results to retrieve
            
        Returns:
            Tuple of (relevant_documents, metadatas)
        """
        if self.embeddings is None or len(self.documents) == 0:
            return [], []
        
        # Get query embedding
        query_embedding = np.array(self.embedding_manager.embed_text(query))
        
        # Compute cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Retrieve documents and metadata
        retrieved_docs = [self.documents[i] for i in top_indices]
        retrieved_meta = [self.metadatas[i] for i in top_indices]
        
        return retrieved_docs, retrieved_meta
    
    def generate_answer(self, query: str, context_documents: List[str]) -> str:
        """
        Generate an answer based on retrieved context
        
        This is a simple template-based approach. For more sophisticated answers,
        integrate with an LLM like OpenAI or a local model via ollama.
        
        Args:
            query: Original user question
            context_documents: Retrieved relevant documents
            
        Returns:
            Generated answer
        """
        if not context_documents:
            return "No relevant information found in the knowledge base."
        
        # Simple approach: combine context and generate prompt
        context = "\n\n".join(context_documents[:3])
        
        # Create a prompt for an LLM (if you integrate one)
        prompt = f"""Based on the following Warhammer: The Old World rules, answer the question:

Question: {query}

Relevant Rules:
{context}

Answer:"""
        
        return prompt
    
    def answer_question(self, query: str, use_llm: bool = False) -> dict:
        """
        Complete RAG pipeline: retrieve and answer
        
        Args:
            query: User's question
            use_llm: If True, use LLM to generate answer (requires LLM setup)
            
        Returns:
            Dictionary with answer and references
        """
        # Step 1: Retrieve relevant context
        relevant_docs, metadatas = self.retrieve_context(query, top_k=3)
        
        # Step 2: Generate answer
        if use_llm:
            # This would integrate with OpenAI, ollama, or other LLM
            # For now, return the prompt that would be sent to LLM
            answer = self.generate_answer(query, relevant_docs)
        else:
            # Simple approach: return extracted context
            answer = self._simple_answer(relevant_docs)
        
        # Step 3: Return with references
        return {
            "query": query,
            "answer": answer,
            "sources": metadatas,
            "context_chunks": relevant_docs
        }
    
    def _simple_answer(self, documents: List[str]) -> str:
        """Generate a simple answer by summarizing retrieved documents"""
        if not documents:
            return "No relevant information found."
        
        # Combine and truncate for simple answer
        combined = " ".join(documents)
        if len(combined) > 500:
            combined = combined[:500] + "..."
        
        return combined
