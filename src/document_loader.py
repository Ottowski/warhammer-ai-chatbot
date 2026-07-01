import os
from pathlib import Path
from typing import List, Optional, Tuple

class DocumentLoader:
    """Reads rule files from disk and breaks them into smaller searchable chunks."""
    
    def __init__(self, rules_directory: str = "./rules"):
        # Where to look for rule files
        self.rules_directory = rules_directory
    
    def load_all_documents(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> Tuple[List[str], List[dict], List[str]]:
        """
        Scans the rules folder, reads every .md and .txt file,
        and splits them into chunks. Returns the chunks, where each
        came from, and a unique ID for each.
        """
        documents = []
        metadatas = []
        ids = []
        doc_id_counter = 0

        # Sanity-check the chunking settings
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            chunk_overlap = 0
        elif chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1
        
        # Bail out early if the rules folder doesn't exist
        if not os.path.exists(self.rules_directory):
            print(f"Warning: Rules directory not found at {self.rules_directory}")
            return documents, metadatas, ids
        
        # Find all .md and .txt files, sorted so order is consistent
        rules_root = Path(self.rules_directory)
        rule_files = sorted(list(rules_root.rglob("*.md")) + list(rules_root.rglob("*.txt")))
        
        if not rule_files:
            print(f"Warning: No rule files found in {self.rules_directory}")
            return documents, metadatas, ids
        
        for file_path in rule_files:
            relative_path = file_path.relative_to(rules_root)
            print(f"Loading: {relative_path}")

            content = self._read_text_file(file_path)
            if content is None:
                continue  # Skip files that couldn't be read
            
            # Split the file into overlapping chunks
            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
            
            for chunk in chunks:
                if chunk.strip():  # Skip any chunks that are just whitespace
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(relative_path),
                        "file_path": str(file_path)
                    })
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1
        
        print(f"Loaded {len(documents)} document chunks from {len(rule_files)} files")
        return documents, metadatas, ids

    def _read_text_file(self, file_path: Path) -> Optional[str]:
        """Safely read a file. Returns None if the file can't be opened or decoded."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Warning: Skipping unreadable file {file_path}: {exc}")
            return None
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Splits a long text into smaller chunks at markdown heading boundaries.
        Chunks overlap slightly so context isn't lost at the edges.
        """
        # If the whole text fits in one chunk, just return it as-is
        if len(text) <= chunk_size:
            return [text]

        overlap = max(0, overlap)
        
        import re

        # Normalize line endings so markdown table rows don't get collapsed onto one line
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Split on ## or ### headings — these are natural section breaks in rule docs
        sections = re.split(r'(\n#{2,3}\s+[^\n]+\n)', text)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            # Only strip leading/trailing whitespace for non-table sections
            # Stripping table sections collapses rows onto one line
            if '|' in section:
               section = section.strip('\r\n')  # remove surrounding blank lines only, not internal newlines
            else:
               section = section.strip()
            if not section:
                continue
                
            # If adding this section would overflow the chunk, save what we have
            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # When starting a new chunk, carry over some text from the end
                # of the previous one so context isn't cut off abruptly
                if section.startswith('#'):
                    current_chunk = section
                else:
                    overlap_text = current_chunk[-overlap:].strip() if overlap else ""
                    if overlap_text:
                        current_chunk = overlap_text + '\n\n' + section
                    else:
                        current_chunk = section
            else:
                # Keep building the current chunk
                if current_chunk:
                    current_chunk += '\n\n' + section  # \n\n preserves markdown table row breaks
                else:
                    current_chunk = section
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def load_single_document(self, file_name: str) -> Tuple[List[str], List[dict], List[str]]:
        """Load just one specific file by name, without chunking."""
        file_path = Path(self.rules_directory) / file_name
        
        if not file_path.exists():
            print(f"Error: File not found at {file_path}")
            return [], [], []

        content = self._read_text_file(file_path)
        if content is None:
            return [], [], []
        
        documents = [content]
        metadatas = [{"source": file_name, "file_path": str(file_path)}]
        ids = ["doc_0"]
        
        return documents, metadatas, ids