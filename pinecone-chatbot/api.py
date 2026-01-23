"""
FastAPI server for Pinecone Chatbot API.

Provides REST endpoints for chat functionality with session-based conversation history.
"""
import os
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from chat_agent import PineconeChatAgent
from models import (
    ChatRequest, ChatResponse, ResetRequest, ResetResponse, HealthResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pinecone Chatbot API",
    description="RAG-based chatbot API using Pinecone vector database",
    version="1.0.0"
)

# Configure CORS - allow all origins for flexibility (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent (singleton pattern)
_agent: Optional[PineconeChatAgent] = None

# In-memory session storage (for production, consider using Redis or a database)
_sessions: dict[str, list] = {}


def get_agent() -> PineconeChatAgent:
    """Get or create the chat agent instance."""
    global _agent
    if _agent is None:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "products")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        
        if not all([pinecone_api_key, openai_api_key]):
            raise ValueError(
                "Missing required environment variables: "
                "PINECONE_API_KEY, PINECONE_INDEX_NAME, OPENAI_API_KEY"
            )
        
        _agent = PineconeChatAgent(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=pinecone_index_name,
            openai_api_key=openai_api_key,
            embedding_model=embedding_model,
            chat_model=chat_model
        )
    return _agent


def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    from langchain_core.messages import messages_from_dict
    if session_id in _sessions:
        return messages_from_dict(_sessions[session_id])
    return []


def save_conversation_history(session_id: str, messages):
    """Save conversation history for a session."""
    from langchain_core.messages import message_to_dict
    _sessions[session_id] = [message_to_dict(msg) for msg in messages]


def clear_session(session_id: str) -> bool:
    """Clear conversation history for a session."""
    if session_id in _sessions:
        _sessions[session_id] = []
        return True
    return True  # Return True even if session doesn't exist


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway monitoring."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/api/chat")
async def chat_get():
    """GET endpoint - provides information about how to use the chat API."""
    return {
        "message": "This endpoint requires a POST request with a JSON body.",
        "method": "POST",
        "endpoint": "/api/chat",
        "required_fields": {
            "message": "string (required) - Your question/query"
        },
        "optional_fields": {
            "session_id": "string - For conversation continuity",
            "temperature": "float (0-2) - LLM temperature",
            "chat_model": "string - OpenAI model name",
            "k": "integer (1-20) - Number of documents to retrieve",
            "filters": "object - Pinecone metadata filters",
            "system_prompt": "string - Custom system prompt"
        },
        "example": {
            "message": "What installation instructions are available?"
        },
        "docs": "/docs",
        "note": "Use the interactive docs at /docs to test this endpoint, or use curl/Postman with POST method"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for processing user queries.
    
    Accepts a message and optional parameters for customization.
    Maintains conversation history via session_id.
    """
    try:
        agent = get_agent()
        
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Retrieve conversation history
        chat_history = get_conversation_history(session_id)
        
        # Prepare parameters for agent
        agent_params = {}
        if request.temperature is not None:
            agent_params["temperature"] = request.temperature
        if request.chat_model:
            agent_params["chat_model"] = request.chat_model
        if request.k is not None:
            agent_params["k"] = request.k
        if request.filters:
            agent_params["filters"] = request.filters
        if request.system_prompt:
            agent_params["system_prompt"] = request.system_prompt
        
        # Process chat request
        result = agent.chat(
            query=request.message,
            chat_history=chat_history,
            **agent_params
        )
        
        # Save updated conversation history
        save_conversation_history(
            session_id=session_id,
            messages=result["updated_history"]
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=session_id
        )
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/reset", response_model=ResetResponse)
async def reset_conversation(request: ResetRequest):
    """
    Reset conversation history for a session.
    
    Clears all messages for the given session_id.
    """
    try:
        success = clear_session(request.session_id)
        
        if success:
            return ResetResponse(
                success=True,
                message="Conversation history cleared successfully",
                session_id=request.session_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear conversation history"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Pinecone Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
