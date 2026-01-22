# Products Chatbot - RAG Agent

A text-to-text chat agent using Retrieval Augmented Generation (RAG) with Supabase vector embeddings and OpenAI. Available as both a CLI tool and a REST API for integration with web applications.

## Features

- **RAG-based retrieval** from Supabase `products` table using vector embeddings
- **LangChain framework** for orchestration
- **OpenAI GPT-4o-mini** for chat (cost-effective and fast)
- **Session-based conversation memory** stored in Supabase
- **CLI interface** for easy interaction
- **REST API** for Next.js and other web integrations
- **Configurable parameters** (temperature, model, retrieval count, filters, etc.)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials (see `.env.example`):
```env
SUPABASE_URL=https://npeajhtemjbcpnhsqknf.supabase.co
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4o-mini
```

**Note:** See `RLS_SETUP.md` if you encounter issues accessing products (Row Level Security).

3. Run the chat agent:
```bash
python chat_agent.py
```

## Architecture

- **Vector Store**: Supabase PostgreSQL with pgvector extension
- **Embeddings**: OpenAI `text-embedding-3-large` (3072 dimensions, matches existing product embeddings)
- **LLM**: OpenAI `gpt-4o-mini` for chat
- **Framework**: LangChain for RAG chain and conversation management

## Usage

### CLI Usage

Run the chat agent locally:

```bash
python chat_agent.py
```

The agent will:
1. Convert your query to an embedding
2. Search for similar products in Supabase
3. Use retrieved product information as context
4. Generate a response using GPT-4o-mini

Type `exit` or `quit` to end the conversation.

### API Usage

#### Starting the API Server

```bash
# Development
uvicorn api:app --reload

# Production (Railway)
# Uses Procfile: uvicorn api:app --host 0.0.0.0 --port $PORT
```

#### API Endpoints

**POST `/api/chat`** - Main chat endpoint

Request body:
```json
{
  "message": "What products do you have?",
  "session_id": "optional-session-id",
  "temperature": 0.7,
  "chat_model": "gpt-4o-mini",
  "k": 4,
  "filters": {"is_active": true, "category": "electronics"},
  "system_prompt": "Custom system prompt (optional)"
}
```

Response:
```json
{
  "answer": "We have several products available...",
  "sources": [
    {
      "title": "Product Name",
      "category": "electronics",
      "id": "123"
    }
  ],
  "session_id": "generated-or-provided-session-id"
}
```

**POST `/api/reset`** - Clear conversation history

Request body:
```json
{
  "session_id": "session-id-to-reset"
}
```

**GET `/health`** - Health check endpoint

#### Next.js Integration Example

```javascript
// lib/chatApi.js
const API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || 'https://your-api.railway.app';

export async function sendMessage(message, sessionId = null, options = {}) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      temperature: options.temperature || 0.7,
      chat_model: options.chatModel || 'gpt-4o-mini',
      k: options.k || 4,
      filters: options.filters,
      system_prompt: options.systemPrompt,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function resetConversation(sessionId) {
  const response = await fetch(`${API_URL}/api/reset`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ session_id: sessionId }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

```javascript
// components/ChatWidget.jsx
'use client';

import { useState } from 'react';
import { sendMessage, resetConversation } from '@/lib/chatApi';

export default function ChatWidget() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await sendMessage(userMessage, sessionId, {
        temperature: 0.7,
        k: 5,
      });

      // Update session ID if it's a new session
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Add AI response to UI
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.answer,
        sources: response.sources 
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (sessionId) {
      await resetConversation(sessionId);
    }
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className="chat-widget">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <strong>Sources:</strong>
                {msg.sources.map((source, i) => (
                  <span key={i}>{source.title}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about products..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </button>
        <button onClick={handleReset}>Reset</button>
      </div>
    </div>
  );
}
```

## Deployment

### Railway Deployment

1. Push your code to a Git repository
2. Connect Railway to your repository
3. Set environment variables in Railway:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY`
   - `EMBEDDING_MODEL` (optional, default: `text-embedding-3-large`)
   - `CHAT_MODEL` (optional, default: `gpt-4o-mini`)
4. Railway will automatically detect the `Procfile` and deploy

### Database Setup

Before deploying, run the migration to create the conversations table:

```sql
-- Run migrations/create_conversations_table.sql in your Supabase SQL editor
```

See `migrations/create_conversations_table.sql` for the full schema.

## API Documentation

Interactive API documentation is available at `/docs` when the server is running (Swagger UI).

For a detailed guide on using the API, see `API_GUIDE.md`.
# tbs-products-chat-agent
# tbs-products-chat-agent
# tbs-products-chat-agent
