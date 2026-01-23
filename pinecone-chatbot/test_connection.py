"""
Simple test script to verify Pinecone connection and index access.
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()


def test_pinecone_connection():
    """Test basic Pinecone connection and index access."""
    print("Testing Pinecone connection...\n")
    
    # Get configuration
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not api_key:
        print("❌ Error: PINECONE_API_KEY not found in environment variables")
        return False
    
    if not index_name:
        print("❌ Error: PINECONE_INDEX_NAME not found in environment variables")
        return False
    
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        
        # List all indexes
        print("📋 Available indexes:")
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        for idx_name in index_names:
            print(f"   - {idx_name}")
        
        print()
        
        # Check if target index exists
        if index_name not in index_names:
            print(f"❌ Error: Index '{index_name}' not found")
            print(f"   Available indexes: {index_names}")
            return False
        
        # Get index info
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        
        print(f"✅ Successfully connected to index: {index_name}")
        print(f"   Total vectors: {stats.get('total_vector_count', 'Unknown')}")
        print(f"   Dimension: {stats.get('dimension', 'Unknown')}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {e}")
        return False


def test_embeddings():
    """Test OpenAI embeddings generation."""
    print("Testing OpenAI embeddings...\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=api_key
        )
        
        # Test embedding generation
        test_text = "This is a test query"
        embedding = embeddings.embed_query(test_text)
        
        print(f"✅ Successfully generated embedding")
        print(f"   Model: {embedding_model}")
        print(f"   Dimension: {len(embedding)}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Pinecone Chatbot - Connection Test")
    print("=" * 60)
    print()
    
    pinecone_ok = test_pinecone_connection()
    embeddings_ok = test_embeddings()
    
    print("=" * 60)
    if pinecone_ok and embeddings_ok:
        print("✅ All tests passed! You're ready to use the chatbot.")
    else:
        print("❌ Some tests failed. Please check your configuration.")
    print("=" * 60)


if __name__ == "__main__":
    main()
