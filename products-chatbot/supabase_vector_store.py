"""
Supabase Vector Store for RAG retrieval from products table.
"""
import os
from typing import List, Optional
from supabase import create_client, Client
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
import numpy as np


class SupabaseVectorStore(VectorStore):
    """Custom vector store for Supabase pgvector."""
    
    def __init__(
        self,
        supabase_client: Client,
        embedding_function: Embeddings,
        table_name: str = "products",
        embedding_column: str = "embeddings",
        text_column: str = "content",
        metadata_columns: Optional[List[str]] = None
    ):
        self.supabase = supabase_client
        self.embedding_function = embedding_function
        self.table_name = table_name
        self.embedding_column = embedding_column
        self.text_column = text_column
        self.metadata_columns = metadata_columns or [
            "id", "title", "subtitle", "category", "description", 
            "product_specs", "features", "is_active"
        ]
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """
        Search for similar products using vector similarity.
        Uses Supabase RPC function for efficient vector search if available,
        otherwise falls back to Python-based similarity calculation.
        """
        # Generate query embedding
        query_embedding = self.embedding_function.embed_query(query)
        
        # Try to use Supabase RPC function for vector search (more efficient)
        try:
            # Call RPC function for vector similarity search
            filter_conditions = filter or {}
            is_active = filter_conditions.get("is_active", True)
            
            response = self.supabase.rpc(
                "match_products",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,
                    "match_count": k,
                    "is_active_filter": is_active
                }
            ).execute()
            
            if response.data:
                results = []
                for product in response.data:
                    similarity = product.get("similarity", 0.0)
                    metadata = {col: product.get(col) for col in self.metadata_columns}
                    doc = Document(
                        page_content=product.get(self.text_column) or product.get("description", ""),
                        metadata=metadata
                    )
                    results.append((doc, similarity))
                return results
        except Exception:
            # Fallback to Python-based similarity if RPC function doesn't exist
            pass
        
        # Fallback: Python-based similarity search
        # Start with select() first, then apply filters
        query_builder = self.supabase.table(self.table_name).select(
            ",".join([self.text_column, self.embedding_column] + self.metadata_columns)
        )
        
        # Apply filter if provided
        if filter:
            for key, value in filter.items():
                query_builder = query_builder.eq(key, value)
        
        # Execute query
        response = query_builder.execute()
        
        products = response.data
        
        # Calculate cosine similarity
        results = []
        for product in products:
            if not product.get(self.embedding_column):
                continue
            
            # Parse embedding - it might be stored as a string
            product_embedding_raw = product[self.embedding_column]
            
            # Convert to numpy array if it's a string
            if isinstance(product_embedding_raw, str):
                try:
                    # Try to parse as JSON array
                    import json
                    product_embedding = json.loads(product_embedding_raw)
                except (json.JSONDecodeError, ValueError):
                    # If that fails, try to parse as a Python literal
                    import ast
                    try:
                        product_embedding = ast.literal_eval(product_embedding_raw)
                    except (ValueError, SyntaxError):
                        # Skip this product if we can't parse the embedding
                        continue
            else:
                product_embedding = product_embedding_raw
            
            # Ensure it's a numpy array
            product_embedding = np.array(product_embedding, dtype=np.float32)
            
            # Skip if dimensions don't match
            if len(product_embedding) != len(query_embedding):
                # Log a warning for the first mismatch
                if not hasattr(self, '_dimension_warning_shown'):
                    print(f"⚠️  Warning: Embedding dimension mismatch. Product embeddings: {len(product_embedding)}, Query embeddings: {len(query_embedding)}")
                    print(f"   This product will be skipped. Consider using the same embedding model.")
                    self._dimension_warning_shown = True
                continue
            
            similarity = self._cosine_similarity(
                np.array(query_embedding, dtype=np.float32),
                product_embedding
            )
            
            metadata = {col: product.get(col) for col in self.metadata_columns}
            doc = Document(
                page_content=product.get(self.text_column) or product.get("description", ""),
                metadata=metadata
            )
            
            results.append((doc, similarity))
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Search for similar products, returning only documents."""
        results = self.similarity_search_with_score(query, k, filter)
        return [doc for doc, _ in results]
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """Not implemented - embeddings should be created in Supabase."""
        raise NotImplementedError(
            "Use Supabase directly to add embeddings. "
            "This vector store is read-only for RAG retrieval."
        )
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        **kwargs
    ):
        """Not implemented - embeddings should be created in Supabase."""
        raise NotImplementedError(
            "Use Supabase directly to add embeddings. "
            "This vector store is read-only for RAG retrieval."
        )
    
    def as_retriever(self, **kwargs):
        """Return a retriever interface for LangChain."""
        from langchain_core.vectorstores import VectorStoreRetriever
        return VectorStoreRetriever(vectorstore=self, **kwargs)


def create_supabase_vector_store(
    supabase_url: str,
    supabase_key: str,
    embedding_function: Embeddings
) -> SupabaseVectorStore:
    """Factory function to create Supabase vector store."""
    supabase_client = create_client(supabase_url, supabase_key)
    return SupabaseVectorStore(
        supabase_client=supabase_client,
        embedding_function=embedding_function
    )
