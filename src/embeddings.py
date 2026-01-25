from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    """Manages embeddings using sentence-transformers"""
    
    # Model options: 'all-MiniLM-L6-v2' (fast, good), 'all-mpnet-base-v2' (slower, better)
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize embedding manager
        
        Args:
            model_name: Name of sentence-transformers model to use
        """
        self.model_name = model_name
        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name)
        print(f"Initialized embeddings with model: {model_name}")
    
    def embed_text(self, text: str):
        """Embed a single text string"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_texts(self, texts: list):
        """Embed multiple text strings"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
