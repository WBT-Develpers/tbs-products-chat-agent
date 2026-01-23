"""
Pinecone Vector Store for RAG retrieval.
"""
from typing import Optional
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.embeddings import Embeddings


def create_pinecone_vector_store(
    api_key: str,
    index_name: str,
    embedding_function: Embeddings
) -> PineconeVectorStore:
    """
    Factory function to create Pinecone vector store.
    
    Args:
        api_key: Pinecone API key
        index_name: Name of the Pinecone index
        embedding_function: LangChain embeddings function
        
    Returns:
        PineconeVectorStore instance
        
    Raises:
        ValueError: If the index doesn't exist
    """
    # Initialize Pinecone client to check if index exists
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"⚠️  Warning: Index '{index_name}' does not exist.")
        print(f"   Available indexes: {existing_indexes}")
        print(f"   Please create the index in Pinecone console or use Pinecone client.")
        raise ValueError(f"Index '{index_name}' not found. Please create it first.")
    
    # Create vector store using LangChain Pinecone integration
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_function,
        pinecone_api_key=api_key
    )
    
    return vector_store
