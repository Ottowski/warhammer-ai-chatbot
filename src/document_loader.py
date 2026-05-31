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
        
        # Scan rules directory recursively for markdown and txt files
        if not os.path.exists(self.rules_directory):
            print(f"Warning: Rules directory not found at {self.rules_directory}")
            return documents, metadatas, ids
        
        rules_root = Path(self.rules_directory)
        rule_files = sorted(list(rules_root.rglob("*.md")) + list(rules_root.rglob("*.txt")))
        
        if not rule_files:
            print(f"Warning: No rule files found in {self.rules_directory}")
            return documents, metadatas, ids
        
        for file_path in rule_files:
            relative_path = file_path.relative_to(rules_root)
            print(f"Loading: {relative_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunk large documents
            chunks = self._chunk_text(content, chunk_size)
            
            for chunk in chunks:
                if chunk.strip():  # Skip empty chunks
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(relative_path),
                        "file_path": str(file_path)
                    })
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1
        
        print(f"Loaded {len(documents)} document chunks from {len(rule_files)} files")
        return documents, metadatas, ids
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks at section boundaries
        
        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk (approximate)
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        # Split by markdown headings first (better for question matching)
        import re
        # Split on markdown headings (## or ###)
        sections = re.split(r'(\n#{2,3}\s+[^\n]+\n)', text)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # If this would exceed chunk size, save current and start new
            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with heading if current section is a heading
                if section.startswith('#'):
                    current_chunk = section
                else:
                    # Create small overlap from previous chunk
                    lines = current_chunk.split('\n')
                    overlap_text = '\n'.join(lines[-3:]) if len(lines) > 3 else current_chunk
                    current_chunk = overlap_text + '\n\n' + section
            else:
                if current_chunk:
                    current_chunk += '\n' + section
                else:
                    current_chunk = section
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
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
