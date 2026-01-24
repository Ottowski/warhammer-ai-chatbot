"""
Document Loader
Loads rule documents from markdown/txt files and chunks them appropriately
"""
import os
from pathlib import Path
from typing import List, Tuple

class DocumentLoader:
    """Loads and processes rule documents"""
    
    def __init__(self, rules_directory: str = "./rules"):
        """
        Initialize document loader
        
        Args:
            rules_directory: Path to directory containing rule files
        """
        self.rules_directory = rules_directory
    
    def load_all_documents(self, chunk_size: int = 500) -> Tuple[List[str], List[dict], List[str]]:
        """
        Load all rule documents from the rules directory
        
        Args:
            chunk_size: Approximate size of text chunks for chunking large documents
            
        Returns:
            Tuple of (documents, metadatas, ids)
        """
        documents = []
        metadatas = []
        ids = []
        doc_id_counter = 0
        
        # Scan rules directory for markdown and txt files
        if not os.path.exists(self.rules_directory):
            print(f"Warning: Rules directory not found at {self.rules_directory}")
            return documents, metadatas, ids
        
        rule_files = list(Path(self.rules_directory).glob("*.md")) + \
                     list(Path(self.rules_directory).glob("*.txt"))
        
        if not rule_files:
            print(f"Warning: No rule files found in {self.rules_directory}")
            return documents, metadatas, ids
        
        for file_path in rule_files:
            print(f"Loading: {file_path.name}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunk large documents
            chunks = self._chunk_text(content, chunk_size)
            
            for chunk in chunks:
                if chunk.strip():  # Skip empty chunks
                    documents.append(chunk)
                    metadatas.append({
                        "source": file_path.name,
                        "file_path": str(file_path)
                    })
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1
        
        print(f"Loaded {len(documents)} document chunks from {len(rule_files)} files")
        return documents, metadatas, ids
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk (approximate)
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(text), step):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def load_single_document(self, file_name: str) -> Tuple[List[str], List[dict], List[str]]:
        """
        Load a single document by filename
        
        Args:
            file_name: Name of the file to load
            
        Returns:
            Tuple of (documents, metadatas, ids)
        """
        file_path = Path(self.rules_directory) / file_name
        
        if not file_path.exists():
            print(f"Error: File not found at {file_path}")
            return [], [], []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        documents = [content]
        metadatas = [{"source": file_name, "file_path": str(file_path)}]
        ids = ["doc_0"]
        
        return documents, metadatas, ids
