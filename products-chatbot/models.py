"""
Pydantic models for API request/response schemas.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Source document information."""
    title: str
    category: str
    id: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message/query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="LLM temperature (0-2)")
    chat_model: Optional[str] = Field(None, description="OpenAI chat model name (e.g., 'gpt-4o-mini', 'gpt-4')")
    embedding_model: Optional[str] = Field(None, description="OpenAI embedding model name")
    k: Optional[int] = Field(None, ge=1, le=20, description="Number of documents to retrieve (1-20)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters (e.g., {'is_active': True, 'category': 'electronics'})")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt for the assistant")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="AI's response to the user's message")
    sources: List[Source] = Field(default_factory=list, description="Source documents used in the response")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ResetRequest(BaseModel):
    """Request model for reset endpoint."""
    session_id: str = Field(..., description="Session ID to reset")


class ResetResponse(BaseModel):
    """Response model for reset endpoint."""
    success: bool = Field(..., description="Whether the reset was successful")
    message: str = Field(..., description="Status message")
    session_id: str = Field(..., description="Session ID that was reset")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(default="1.0.0", description="API version")
