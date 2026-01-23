"""
Pinecone Chatbot - RAG Agent using LangChain and OpenAI.

This agent uses RAG (Retrieval Augmented Generation) to answer questions
by retrieving relevant information from Pinecone vector database.
"""
import os
from typing import List, Optional, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
try:
    # Try LangChain v1.0+ imports (langchain-classic)
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
    from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
except ImportError:
    # Fallback to LangChain 0.3.x imports
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from pinecone_vector_store import create_pinecone_vector_store


# Load environment variables
load_dotenv()


class PineconeChatAgent:
    """RAG-based chat agent for queries using Pinecone."""
    
    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_index_name: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small",
        chat_model: str = "gpt-4o-mini",
        default_temperature: float = 0.7,
        default_k: int = 4,
        default_filters: Optional[Dict] = None
    ):
        """
        Initialize the chat agent.
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Name of the Pinecone index
            openai_api_key: OpenAI API key
            embedding_model: OpenAI embedding model name
            chat_model: OpenAI chat model name
            default_temperature: Default temperature for LLM (can be overridden per request)
            default_k: Default number of documents to retrieve
            default_filters: Default filters for retrieval (Pinecone metadata filters)
        """
        # Store configuration
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index_name = pinecone_index_name
        self.openai_api_key = openai_api_key
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.default_temperature = default_temperature
        self.default_k = default_k
        self.default_filters = default_filters or {}
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=openai_api_key
        )
        
        # Initialize vector store
        print("Connecting to Pinecone vector store...")
        self.vector_store = create_pinecone_vector_store(
            api_key=pinecone_api_key,
            index_name=pinecone_index_name,
            embedding_function=self.embeddings
        )
        
        print("Chat agent initialized successfully!")
    
    def chat(
        self,
        query: str,
        chat_history: Optional[List[BaseMessage]] = None,
        temperature: Optional[float] = None,
        chat_model: Optional[str] = None,
        k: Optional[int] = None,
        filters: Optional[Dict] = None,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Process a user query and return a response.
        
        Args:
            query: User's question/query
            chat_history: List of previous messages (for conversation context)
            temperature: LLM temperature (overrides default)
            chat_model: LLM model name (overrides default)
            k: Number of documents to retrieve (overrides default)
            filters: Search filters for retrieval (Pinecone metadata filters, overrides default)
            system_prompt: Custom system prompt (overrides default)
            
        Returns:
            Dictionary with 'answer', 'sources', and 'updated_history'
        """
        # Use provided parameters or defaults
        temperature = temperature if temperature is not None else self.default_temperature
        chat_model = chat_model or self.chat_model
        k = k if k is not None else self.default_k
        filters = filters if filters is not None else self.default_filters
        chat_history = chat_history or []
        
        # Initialize LLM with specified parameters
        llm = ChatOpenAI(
            model=chat_model,
            temperature=temperature,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize retriever with specified parameters
        # Pinecone filters use metadata filtering syntax
        search_kwargs = {"k": k}
        if filters:
            search_kwargs["filter"] = filters
        
        retriever = self.vector_store.as_retriever(
            search_kwargs=search_kwargs
        )
        
        # Create context prompt for retrieval
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # Create history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm,
            retriever,
            contextualize_q_prompt
        )
        
        # Create QA prompt with optional custom system prompt
        qa_system_prompt = system_prompt or """You are a helpful assistant for a chatbot. \
Your role is to help users find and understand information based on the retrieved context.

Use the following pieces of retrieved context to answer the question. \
If you don't know the answer based on the context, say so. Don't make up information.

{context}

Provide a helpful, accurate answer based on the context. If the context doesn't contain \
enough information, politely let the user know and suggest they rephrase their question."""
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # Create question answering chain
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        # Create retrieval chain
        qa_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain
        )
        
        # Invoke the chain
        result = qa_chain.invoke({
            "input": query,
            "chat_history": chat_history
        })
        
        # Extract sources from context documents
        context_docs = result.get("context", [])
        sources = []
        for doc in context_docs:
            # Extract metadata from Pinecone document
            metadata = doc.metadata or {}
            source_name = metadata.get("source", "Unknown Document")
            
            # Create a unique identifier for the source
            doc_id = metadata.get("id", f"{source_name}_chunk_{metadata.get('chunk_index', 'unknown')}")
            if not isinstance(doc_id, str):
                doc_id = str(doc_id)
            
            sources.append({
                "title": source_name,
                "category": metadata.get("document_type", "manual"),
                "id": doc_id
            })
        
        # Build updated chat history (caller should save this)
        from langchain_core.messages import HumanMessage, AIMessage
        updated_history = chat_history.copy()
        updated_history.append(HumanMessage(content=query))
        updated_history.append(AIMessage(content=result.get("answer", "")))
        
        return {
            "answer": result.get("answer", "I'm sorry, I couldn't generate a response."),
            "sources": sources,
            "updated_history": updated_history
        }


def main():
    """Main CLI interface for the chat agent."""
    # Load configuration
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    
    # Validate configuration
    if not all([pinecone_api_key, pinecone_index_name, openai_api_key]):
        print("Error: Missing required environment variables.")
        print("Please check your .env file and ensure:")
        print("  - PINECONE_API_KEY")
        print("  - PINECONE_INDEX_NAME")
        print("  - OPENAI_API_KEY")
        return
    
    # Initialize agent
    try:
        agent = PineconeChatAgent(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=pinecone_index_name,
            openai_api_key=openai_api_key,
            embedding_model=embedding_model,
            chat_model=chat_model
        )
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return
    
    # Chat loop with manual history tracking
    print("\n" + "="*60)
    print("Pinecone Chatbot - RAG Agent")
    print("="*60)
    print("Type your questions. Type 'exit' or 'quit' to end.")
    print("Type 'reset' to clear conversation history.\n")
    
    # Track conversation history manually for CLI
    from langchain_core.messages import BaseMessage
    chat_history: List[BaseMessage] = []
    
    while True:
        try:
            # Get user input
            user_query = input("You: ").strip()
            
            if not user_query:
                continue
            
            # Handle special commands
            if user_query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if user_query.lower() == "reset":
                chat_history = []
                print("Conversation history cleared.\n")
                continue
            
            # Process query
            print("\nThinking...")
            response = agent.chat(user_query, chat_history=chat_history)
            
            # Update chat history for next iteration
            chat_history = response["updated_history"]
            
            # Display response
            print(f"\nAssistant: {response['answer']}")
            
            # Display sources if available
            if response.get("sources"):
                print("\nSources:")
                for i, source in enumerate(response["sources"], 1):
                    print(f"  {i}. {source['title']} ({source['category']})")
            
            print()  # Empty line for readability
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
