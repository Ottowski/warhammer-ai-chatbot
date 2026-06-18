from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    """Converts text into numeric vectors so we can compare meaning, not just words."""
    
    # 'all-MiniLM-L6-v2' is fast and good enough for most cases
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        # Load the AI model that turns text into vectors
        self.model_name = model_name
        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name)
        print(f"Initialized embeddings with model: {model_name}")
    
    def embed_text(self, text: str):
        # Turn a single string into a vector (used for the user's question)
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_texts(self, texts: list):
        # Turn a list of strings into vectors (used when indexing all the rules)
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
