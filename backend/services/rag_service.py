import os
import numpy as np
from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity

class RAGService:
    """
    Enhanced RAG with semantic search using embeddings
    Time Complexity: O(n) for search where n = number of chunks
    Space Complexity: O(n * d) where d = embedding dimension
    """
    def __init__(self, data_path: str = "university_data.txt"):
        self.data_path = data_path
        self.chunks: List[str] = []
        self.embeddings: np.ndarray = None
        self.load_data()
    
    def load_data(self):
        """Load and chunk the knowledge base"""
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split by sections (identified by double newline or header patterns)
            sections = content.split('\n\n')
            self.chunks = [chunk.strip() for chunk in sections if chunk.strip()]
        else:
            self.chunks = ["Ma'lumotlar bazasi topilmadi."]
    
    def generate_embeddings(self, texts: List[str], client) -> np.ndarray:
        """
        Generate embeddings for texts using OpenAI
        Returns: numpy array of shape (n_texts, embedding_dim)
        """
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
        except Exception as e:
            print(f"Embedding error: {e}")
            # Fallback to keyword search
            return None
    
    def initialize_embeddings(self, client):
        """One-time initialization of chunk embeddings"""
        if self.embeddings is None and self.chunks:
            print("Generating embeddings for knowledge base...")
            self.embeddings = self.generate_embeddings(self.chunks, client)
            print(f"Generated embeddings for {len(self.chunks)} chunks")
    
    def semantic_search(self, query: str, client, top_k: int = 3) -> str:
        """
        Perform semantic search to find most relevant chunks
        Time Complexity: O(n) where n = number of chunks
        """
        # Initialize embeddings if not done yet
        if self.embeddings is None:
            self.initialize_embeddings(client)
        
        # If embeddings failed, fall back to full context
        if self.embeddings is None:
            return self.get_full_context()
        
        # Generate query embedding
        query_embedding = self.generate_embeddings([query], client)
        
        if query_embedding is None:
            return self.get_full_context()
        
        # Compute cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return concatenated top chunks
        relevant_chunks = [self.chunks[i] for i in top_indices]
        return "\n\n".join(relevant_chunks)
    
    def get_full_context(self) -> str:
        """Fallback: return all knowledge base"""
        return "\n\n".join(self.chunks)
    
    def get_relevant_context(self, query: str, client=None) -> str:
        """
        Main method to get relevant context
        Uses semantic search if client available, else returns all
        """
        if client:
            return self.semantic_search(query, client, top_k=3)
        else:
            # Fallback to full context
            return self.get_full_context()

rag_service = RAGService()
