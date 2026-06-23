import hashlib
import pickle
import re
from pathlib import Path
from typing import List, Tuple
import numpy as np
from src.embeddings import EmbeddingManager
from src.document_loader import DocumentLoader

class RAGPipeline:
    """
    The main brain of the app. Ties everything together:
    loads rules → turns them into vectors → finds relevant chunks
    for a question → builds an answer.
    RAG = Retrieval-Augmented Generation.
    """
    
    def __init__(self, rules_directory: str = "./rules", vector_store_path: str = "./data/vector_store"):
        # Wire up the helper classes
        self.embedding_manager = EmbeddingManager()
        self.document_loader = DocumentLoader(rules_directory=rules_directory)
        self.rules_directory = rules_directory
        self.vector_store_path = Path(vector_store_path)
        
        # These get populated when initialize_knowledge_base() is called
        self.documents = []
        self.embeddings = None
        self.metadatas = []

    def _rules_hash(self) -> str:
        """
        Fingerprint all the rules files using their names + last-modified times.
        If any file changes, the hash changes and the cache gets rebuilt.
        """
        hasher = hashlib.md5()
        rules_path = Path(self.rules_directory)
        for f in sorted(rules_path.rglob("*.md")):
            hasher.update(f.name.encode())
            hasher.update(str(f.stat().st_mtime_ns).encode())
        return hasher.hexdigest()
    
    def initialize_knowledge_base(self, force_rebuild: bool = False):
        """
        Load all rules into memory as vectors.
        On the first run this takes a while; after that it loads from a cache
        on disk so startup is fast. The cache is automatically invalidated
        if any rules file changes.
        """
        cache_hash_file = self.vector_store_path / "cache_hash.txt"
        embeddings_file = self.vector_store_path / "embeddings.npy"
        documents_file = self.vector_store_path / "documents.pkl"
        metadatas_file = self.vector_store_path / "metadatas.pkl"

        current_hash = self._rules_hash()

        # Check if a valid cache already exists
        cache_valid = (
            not force_rebuild
            and cache_hash_file.exists()
            and embeddings_file.exists()
            and documents_file.exists()
            and metadatas_file.exists()
            and cache_hash_file.read_text().strip() == current_hash
        )

        if cache_valid:
            # Fast path: load pre-computed vectors from disk
            print("Loading knowledge base from cache...")
            self.embeddings = np.load(str(embeddings_file))
            with open(documents_file, "rb") as f:
                self.documents = pickle.load(f)
            with open(metadatas_file, "rb") as f:
                self.metadatas = pickle.load(f)
            print(f"Loaded {len(self.documents)} documents from cache")
            return

        # Slow path: read files, generate vectors, save to cache
        print("Building knowledge base (first run or rules changed)...")
        documents, metadatas, ids = self.document_loader.load_all_documents()
        if not documents:
            print("Warning: No documents loaded!")
            return

        self.documents = documents
        self.metadatas = metadatas

        print("Generating embeddings...")
        embeddings_list = self.embedding_manager.embed_texts(documents)
        self.embeddings = np.array(embeddings_list)

        # Save everything so next startup is instant
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        np.save(str(embeddings_file), self.embeddings)
        with open(documents_file, "wb") as f:
            pickle.dump(self.documents, f)
        with open(metadatas_file, "wb") as f:
            pickle.dump(self.metadatas, f)
        cache_hash_file.write_text(current_hash)
        print(f"Loaded {len(documents)} documents with embeddings (cache saved)")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> Tuple[List[str], List[dict]]:
        """
        Find the most relevant rule chunks for a question using two signals:
        - Semantic similarity: do the meanings match? (70% weight)
        - Keyword overlap: do the same words appear? (30% weight)
        Returns the top_k best matching chunks.
        """
        if self.embeddings is None or len(self.documents) == 0:
            return [], []
        
        # Embed the question so we can compare it against stored rule vectors
        query_embedding = np.array(self.embedding_manager.embed_text(query))
        
        # Score every chunk by how similar it is to the question (cosine similarity)
        from sklearn.metrics.pairwise import cosine_similarity
        semantic_scores = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Also score by raw keyword overlap as a secondary signal
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        keyword_scores = np.zeros(len(self.documents))
        for i, doc in enumerate(self.documents):
            doc_lower = doc.lower()
            # Boost if document contains query words
            matching_words = sum(1 for word in query_words if word in doc_lower)
            # Extra boost if a section heading directly matches a query word
            if any(heading in doc_lower for heading in ['###', '##']):
                for word in query_words:
                    if f"## {word}" in doc_lower or f"### {word}" in doc_lower:
                        matching_words += 3
            keyword_scores[i] = matching_words
        
        # Normalise keyword scores to 0–1 so they're on the same scale as cosine scores
        if keyword_scores.max() > 0:
            keyword_scores = keyword_scores / keyword_scores.max()
        
        # Blend the two scores
        combined_scores = 0.7 * semantic_scores + 0.3 * keyword_scores
        
        # Pick the highest-scoring chunks
        top_indices = np.argsort(combined_scores)[-top_k:][::-1]
        # Retrieve documents and metadata
        retrieved_docs = [self.documents[i] for i in top_indices]
        retrieved_meta = [self.metadatas[i] for i in top_indices]
        
        return retrieved_docs, retrieved_meta
    
    def generate_answer(self, query: str, context_documents: List[str]) -> str:
        """
        Builds the prompt that would be sent to an LLM.
        Right now this just formats the text — actual LLM integration is TODO.
        """
        if not context_documents:
            return "No relevant information found in the knowledge base."
        
        # Combine the top 3 chunks into one block of context
        context = "\n\n".join(self._normalize_markdown_for_display(d) for d in context_documents[:3])
        
        # Ready-to-send prompt for an LLM
        prompt = f"""Based on the following Warhammer: The Old World rules, answer the question:

Question: {query}

Relevant Rules:
{context}

Answer:"""
        
        return prompt
    
    def answer_question(self, query: str, use_llm: bool = False) -> dict:
        """
        The main entry point. Given a question, returns an answer + sources.
        Set use_llm=True once an LLM is wired up; for now it falls back
        to returning the raw matched rule text.
        """
        # Step 1: Find the most relevant rule chunks
        relevant_docs, metadatas = self.retrieve_context(query, top_k=5)
        
        # Step 2: Generate an answer from those chunks
        if use_llm:
            # Returns a formatted prompt (LLM not yet integrated)
            answer = self.generate_answer(query, relevant_docs)
        else:
            # Just display the matched rule text directly
            answer = self._simple_answer(relevant_docs)
        
        # Step 3: Package everything up for the caller
        return {
            "query": query,
            "answer": answer,
            "sources": metadatas,
            "context_chunks": relevant_docs
        }
    
    def _simple_answer(self, documents: List[str]) -> str:
        """Combine the top 3 matched chunks into a clean readable block of text."""
        if not documents:
            return "No relevant information found."
        
        # Return the top chunks separated clearly
        answer_parts = []
        for i, doc in enumerate(documents[:3], 1):
            # Clean up the text
            doc = self._normalize_markdown_for_display(doc)
            # Remove any excessive newlines
            if i > 1:
                answer_parts.append("\n\n---\n\n")  # Visual separator between chunks
            answer_parts.append(doc)
        
        return "".join(answer_parts)

    def _normalize_markdown_for_display(self, text: str) -> str:
        """
        Keep markdown readable even if any upstream step flattens whitespace.

        This fixes two common cases seen in imported rule docs:
        1) table rows collapsed into one line: "| ... | | --- | ..."
        2) key-value lines collapsed together: "Unit Category: ...Troop Type: ..."
        """
        if not text:
            return ""

        s = text.replace("\r\n", "\n").replace("\r", "\n").strip()

        # Re-split collapsed markdown table rows.
        # If rows were flattened, they often appear as "| ... | | ...".
        s = re.sub(r"\|\s+\|", "|\n|", s)

        # Ensure each heading starts on its own line.
        s = re.sub(r"(?<!\n)(#{2,3}\s)", r"\n\1", s)

        # If a heading and a table header were flattened onto one line,
        # split at the first table pipe.
        s = re.sub(r"^(#{2,3}\s[^\n|]+?)\s+(\|\s*[^\n]+)$", r"\1\n\2", s, flags=re.MULTILINE)

        # Ensure common unit stat fields each start on their own line.
        labels = [
            "Unit Category:",
            "Troop Type:",
            "Base Size:",
            "Unit Size:",
            "Equipment:",
            "Special Rules:",
            "Optional Rules:",
        ]
        label_pattern = "|".join(re.escape(label) for label in labels)
        s = re.sub(rf"(?<!\n)({label_pattern})", r"\n\1", s)

        # Keep output tidy.
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()