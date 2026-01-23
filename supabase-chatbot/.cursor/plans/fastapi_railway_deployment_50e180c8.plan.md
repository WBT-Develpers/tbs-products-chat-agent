---
name: FastAPI Railway Deployment
overview: Convert the Python CLI chatbot into a FastAPI REST API with session-based conversation history stored in Supabase, deployable on Railway for Next.js integration.
todos:
  - id: "1"
    content: Create session_manager.py for Supabase conversation history storage/retrieval
    status: completed
  - id: "2"
    content: Refactor chat_agent.py to accept runtime parameters and chat_history instead of in-memory memory
    status: completed
  - id: "3"
    content: Create models.py with Pydantic request/response schemas
    status: completed
  - id: "4"
    content: Create api.py FastAPI server with /api/chat and /api/reset endpoints
    status: completed
    dependencies:
      - "1"
      - "2"
      - "3"
  - id: "5"
    content: Create database migration SQL for conversations table in Supabase
    status: completed
  - id: "6"
    content: Update requirements.txt with FastAPI, uvicorn, and pydantic
    status: completed
  - id: "7"
    content: Create Procfile and railway.json for Railway deployment
    status: completed
    dependencies:
      - "4"
  - id: "8"
    content: Update README.md with API documentation and Next.js integration examples
    status: completed
    dependencies:
      - "4"
  - id: "9"
    content: Create simple user manual (API_GUIDE.md) for friend explaining endpoint usage, parameters, and Next.js integration examples
    status: completed
    dependencies:
      - "4"
---

# FastAPI REST API for Products Chatbot

## Architecture Overview

Convert the CLI chatbot into a stateless FastAPI service that supports 10-50 concurrent users with session-based conversation history stored in Supabase.

## Implementation Steps

### 1. Create FastAPI Server (`api.py`)

Create a new FastAPI application that:

- Wraps `ProductsChatAgent` class
- Provides REST endpoints: `POST /api/chat`, `POST /api/reset`
- Accepts configurable parameters (temperature, model, k, filters, etc.)
- Manages sessions via `session_id` parameter
- Returns JSON responses with answer and sources

Key endpoints:

- `POST /api/chat` - Main chat endpoint
- `POST /api/reset` - Clear conversation history
- `GET /health` - Health check for Railway

### 2. Create Session Management Module (`session_manager.py`)

New module to handle conversation history in Supabase:

- Store/retrieve conversation history by `session_id`
- Convert LangChain message format to/from JSON for database storage
- Handle session expiration (optional TTL)

### 3. Modify `ProductsChatAgent` Class (`chat_agent.py`)

Refactor to support:

- Runtime parameter configuration (temperature, model, k, filters)
- Accept chat history as parameter instead of using in-memory memory
- Remove `ConversationBufferMemory` dependency
- Make `chat()` method accept `chat_history` parameter

### 4. Create Database Migration (`migrations/create_conversations_table.sql`)

SQL migration to create `conversations` table in Supabase:

- Columns: `session_id` (text, primary key), `messages` (jsonb), `created_at`, `updated_at`
- Index on `session_id` for fast lookups
- Optional: TTL/cleanup policy for old sessions

### 5. Update Dependencies (`requirements.txt`)

Add FastAPI and related packages:

- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `pydantic>=2.0.0` (for request/response models)

### 6. Create Railway Deployment Files

**`Procfile`** - Railway startup command:

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

**`railway.json`** (optional) - Railway configuration:

- Python version specification
- Build/start commands

### 7. Create API Request/Response Models (`models.py`)

Pydantic models for:

- `ChatRequest` - message, session_id, temperature, chat_model, embedding_model, k, filters, system_prompt
- `ChatResponse` - answer, sources, session_id
- `ResetRequest` - session_id

### 8. Environment Variables Setup

Document required Railway environment variables:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `OPENAI_API_KEY`
- `EMBEDDING_MODEL` (optional, default: text-embedding-3-large)
- `CHAT_MODEL` (optional, default: gpt-4o-mini)
- `PORT` (Railway sets this automatically)

### 9. Update Documentation

- Update `README.md` with API usage examples
- Add Next.js integration example
- Document all configurable parameters

### 10. Create User Manual (`API_GUIDE.md`)

Create a simple, easy-to-read guide for your friend that includes:

- Quick start: How to call the API endpoint
- All available parameters with explanations and examples
- Next.js integration code examples
- Session management best practices
- Error handling examples
- Common use cases and patterns

## File Changes Summary

**New Files:**

- `api.py` - FastAPI server
- `session_manager.py` - Supabase session management
- `models.py` - Pydantic request/response models
- `migrations/create_conversations_table.sql` - Database schema
- `Procfile` - Railway deployment
- `railway.json` - Railway config (optional)
- `API_GUIDE.md` - Simple user manual for friend

**Modified Files:**

- `chat_agent.py` - Refactor for stateless operation
- `requirements.txt` - Add FastAPI dependencies
- `README.md` - Add API documentation

## Data Flow

```
Next.js App → POST /api/chat → FastAPI → SessionManager (load history) 
→ ProductsChatAgent (process) → SessionManager (save history) → Response
```

## Testing Considerations

- Test with multiple concurrent session_ids
- Verify conversation history persistence
- Test parameter overrides (temperature, model, etc.)
- Health check endpoint for Railway monitoring