"""
Vector Store Management
Handles creation and querying of Chroma vector database for rules documents
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Tuple

class VectorStoreManager:
    """Manages Chroma vector store for rule documents"""
    
    def __init__(self, persist_directory: str = "./data/vector_store"):
        """
        Initialize vector store
        
        Args:
            persist_directory: Path where vector store will be persisted
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Chroma client with persistence
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(settings)
        self.collection = None
    
    def create_collection(self, name: str = "warhammer_rules", embedding_function=None):
        """
        Create or get a collection for storing embeddings
        
        Args:
            name: Name of the collection
            embedding_function: Optional custom embedding function
        """
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=name, embedding_function=embedding_function)
            print(f"Loaded existing collection: {name}")
        except:
            # Create new collection if doesn't exist
            self.collection = self.client.create_collection(
                name=name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {name}")
    
    def add_documents(self, documents: List[str], metadatas: List[dict], ids: List[str]):
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts (e.g., source file, section)
            ids: List of unique document IDs
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection first.")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to collection")
    
    def query(self, query_text: str, n_results: int = 3) -> Tuple[List[str], List[dict]]:
        """
        Query the vector store for relevant documents
        
        Args:
            query_text: User's question or search query
            n_results: Number of results to return
            
        Returns:
            Tuple of (documents, metadatas)
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection first.")
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Extract and flatten results
        documents = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        
        return documents, metadatas
    
    def persist(self):
        """Persist the vector store to disk"""
        self.client.persist()
        print("Vector store persisted to disk")
