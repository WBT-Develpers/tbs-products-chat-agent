#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run this before deploying to Railway.
"""
import sys

def test_imports():
    """Test all critical imports."""
    errors = []
    
    print("Testing imports...")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}\n")
    
    # Test core LangChain imports
    try:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.documents import Document
        from langchain_core.messages import BaseMessage
        print("✓ Core LangChain imports OK")
    except ImportError as e:
        errors.append(f"Core LangChain imports failed: {e}")
        print(f"✗ Core LangChain imports failed: {e}")
    
    # Test chain imports
    try:
        try:
            from langchain_classic.chains.combine_documents import create_stuff_documents_chain
            from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
            print("✓ LangChain 1.0+ imports (langchain-classic) OK")
        except ImportError:
            from langchain.chains.combine_documents import create_stuff_documents_chain
            from langchain.chains import create_history_aware_retriever, create_retrieval_chain
            print("✓ LangChain 0.3.x imports (fallback) OK")
    except ImportError as e:
        errors.append(f"Chain imports failed: {e}")
        print(f"✗ Chain imports failed: {e}")
    
    # Test chat_agent module
    try:
        import chat_agent
        from chat_agent import ProductsChatAgent
        print("✓ chat_agent module imports OK")
    except ImportError as e:
        errors.append(f"chat_agent imports failed: {e}")
        print(f"✗ chat_agent imports failed: {e}")
    
    # Test other dependencies
    try:
        from supabase import create_client
        print("✓ Supabase imports OK")
    except ImportError as e:
        errors.append(f"Supabase imports failed: {e}")
        print(f"✗ Supabase imports failed: {e}")
    
    try:
        from fastapi import FastAPI
        print("✓ FastAPI imports OK")
    except ImportError as e:
        errors.append(f"FastAPI imports failed: {e}")
        print(f"✗ FastAPI imports failed: {e}")
    
    print("\n" + "="*50)
    if errors:
        print("❌ Some imports failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All imports successful! Ready for deployment.")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
