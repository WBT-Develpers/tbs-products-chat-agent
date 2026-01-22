"""
FastAPI server for Products Chatbot API.

Provides REST endpoints for chat functionality with session-based conversation history.
"""
import os
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from chat_agent import ProductsChatAgent
from session_manager import create_session_manager
from models import (
    ChatRequest, ChatResponse, ResetRequest, ResetResponse, HealthResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Products Chatbot API",
    description="RAG-based chatbot API for product queries",
    version="1.0.0"
)

# Configure CORS - allow all origins for flexibility (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Next.js domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent and session manager (singleton pattern)
_agent: Optional[ProductsChatAgent] = None
_session_manager = None


def get_agent() -> ProductsChatAgent:
    """Get or create the chat agent instance."""
    global _agent
    if _agent is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        
        if not all([supabase_url, supabase_key, openai_api_key]):
            raise ValueError(
                "Missing required environment variables: "
                "SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY"
            )
        
        _agent = ProductsChatAgent(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            openai_api_key=openai_api_key,
            embedding_model=embedding_model,
            chat_model=chat_model
        )
    return _agent


def get_session_manager():
    """Get or create the session manager instance."""
    global _session_manager
    if _session_manager is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not all([supabase_url, supabase_key]):
            raise ValueError(
                "Missing required environment variables: SUPABASE_URL, SUPABASE_KEY"
            )
        
        _session_manager = create_session_manager(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
    return _session_manager


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
            "filters": "object - Search filters",
            "system_prompt": "string - Custom system prompt"
        },
        "example": {
            "message": "What products do you have?"
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
        session_manager = get_session_manager()
        
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Retrieve conversation history
        chat_history = session_manager.get_conversation_history(session_id)
        
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
        session_manager.save_conversation_history(
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
        session_manager = get_session_manager()
        success = session_manager.clear_session(request.session_id)
        
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
        "name": "Products Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
