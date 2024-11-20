from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None

    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the vector store
        documents: List of dicts with 'content' and 'metadata' keys
        """
        self.documents.extend(documents)
        texts = [doc['content'] for doc in documents]
        new_embeddings = self.model.encode(texts)
        
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity
        """
        query_embedding = self.model.encode([query])[0]
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [self.documents[i] for i in top_indices]