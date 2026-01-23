# Pinecone Chatbot API - User Guide

Welcome! This guide will help you integrate the Pinecone Chatbot API into your website or Next.js project.

## Quick Start

The API is hosted on Railway at:
```
https://fabulous-healing-production.up.railway.app
```

### Basic Chat Request

Here's the simplest way to send a message:

```javascript
const API_URL = 'https://fabulous-healing-production.up.railway.app';

const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What installation instructions are available?'
  })
});

const data = await response.json();
console.log(data.answer); // The AI's response
console.log(data.sources); // Document sources used
console.log(data.session_id); // Use this for conversation continuity
```

## API Endpoints

### 1. Chat Endpoint

**GET** `/api/chat` - Get usage instructions  
**POST** `/api/chat` - Send a message to the chatbot and get a response

#### GET /api/chat

Returns helpful information about how to use the chat endpoint.

```javascript
const response = await fetch('https://fabulous-healing-production.up.railway.app/api/chat');
const info = await response.json();
// Returns endpoint documentation and usage examples
```

#### POST /api/chat

Send a message to the chatbot and get a response.

#### Request Body

All fields except `message` are optional:

```typescript
{
  message: string;              // Required: Your question/message
  session_id?: string;           // Optional: For conversation continuity
  temperature?: number;         // Optional: 0.0-2.0 (default: 0.7)
  chat_model?: string;          // Optional: "gpt-4o-mini" or "gpt-4" (default: "gpt-4o-mini")
  embedding_model?: string;     // Optional: Embedding model name
  k?: number;                  // Optional: Number of documents to retrieve (1-20, default: 4)
  filters?: object;            // Optional: Pinecone metadata filters
  system_prompt?: string;       // Optional: Custom instructions for the AI
}
```

#### Response

```typescript
{
  answer: string;              // The AI's response
  sources: Array<{             // Documents used in the response
    title: string;
    category: string;
    id: string;
  }>;
  session_id: string;          // Session ID (use this for conversation continuity)
}
```

#### Example Request

```javascript
const API_URL = 'https://fabulous-healing-production.up.railway.app';

const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'How do I install the Greenstar 1000?',
    temperature: 0.8,
    k: 5
  })
});

const data = await response.json();
console.log(data.answer); // AI response
console.log(data.sources); // Array of document sources
console.log(data.session_id); // Session ID for follow-up messages
```

### 2. Reset Endpoint

**POST** `/api/reset`

Clear the conversation history for a session.

#### Request Body

```typescript
{
  session_id: string;  // Required: The session to reset
}
```

#### Response

```typescript
{
  success: boolean;
  message: string;
  session_id: string;
}
```

#### Example

```javascript
const API_URL = 'https://fabulous-healing-production.up.railway.app';

const response = await fetch(`${API_URL}/api/reset`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'your-session-id'
  })
});

const data = await response.json();
console.log(data.success); // true if successful
```

### 3. Health Check

**GET** `/health`

Check if the API is running.

```javascript
const API_URL = 'https://fabulous-healing-production.up.railway.app';

const response = await fetch(`${API_URL}/health`);
const data = await response.json();
// { status: "healthy", version: "1.0.0" }
```

### 4. Root Endpoint

**GET** `/`

Get API information and available endpoints.

```javascript
const API_URL = 'https://fabulous-healing-production.up.railway.app';

const response = await fetch(`${API_URL}/`);
const data = await response.json();
// { name: "Pinecone Chatbot API", version: "1.0.0", docs: "/docs", health: "/health" }
```

### 5. Interactive API Documentation

**GET** `/docs`

Swagger UI for interactive API testing. Open in your browser:
```
https://fabulous-healing-production.up.railway.app/docs
```

## Parameters Explained

### `message` (Required)
The user's question or message. This is the only required field.

```javascript
message: "How do I maintain the ecofit pure 830 system?"
```

### `session_id` (Optional)
A unique identifier for maintaining conversation context. 

- **First message**: Don't include it - the API will generate one and return it
- **Follow-up messages**: Use the `session_id` from previous responses to maintain context

```javascript
// First message - no session_id
const firstResponse = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: 'Hello' })
});
const firstData = await firstResponse.json();
const sessionId = firstData.session_id; // Save this!

// Follow-up message - use the session_id
const secondResponse = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ 
    message: 'Tell me more',
    session_id: sessionId  // Maintains conversation context
  })
});
```

### `temperature` (Optional, 0.0-2.0)
Controls how creative/random the AI responses are.

- **Lower (0.0-0.5)**: More focused, deterministic responses
- **Default (0.7)**: Balanced creativity and accuracy
- **Higher (1.0-2.0)**: More creative, varied responses

```javascript
temperature: 0.5  // More focused
temperature: 0.9  // More creative
```

### `chat_model` (Optional)
Which OpenAI model to use for chat.

- **"gpt-4o-mini"** (default): Fast and cost-effective
- **"gpt-4"**: More capable but slower and more expensive

```javascript
chat_model: "gpt-4o-mini"  // Recommended for most cases
chat_model: "gpt-4"        // For more complex queries
```

### `k` (Optional, 1-20)
Number of document chunks to retrieve and use as context.

- **Lower (1-3)**: Faster, less context
- **Default (4)**: Good balance
- **Higher (5-20)**: More context, slower

```javascript
k: 3   // Quick responses
k: 5   // More comprehensive answers
k: 10  // Maximum context
```

### `filters` (Optional)
Pinecone metadata filters to narrow down document search.

```javascript
// Filter by document type
filters: { document_type: "installation_manual" }

// Filter by source file
filters: { source: "Greenstar_1000_installation_manual_1" }

// Multiple filters (Pinecone syntax)
filters: { 
  "$and": [
    { "document_type": { "$eq": "installation_manual" } },
    { "source": { "$eq": "ecofit-pure-830" } }
  ]
}
```

**Note:** Pinecone uses a specific filter syntax. See [Pinecone metadata filtering docs](https://docs.pinecone.io/docs/metadata-filtering) for more examples.

### `system_prompt` (Optional)
Custom instructions for how the AI should behave.

```javascript
system_prompt: "You are a technical support assistant. Always provide step-by-step instructions."
```

## Next.js Integration Examples

### Simple Chat Component

```jsx
'use client';

import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || 'https://fabulous-healing-production.up.railway.app';

export default function SimpleChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // Add user message to UI immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId, // null on first message
        }),
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();

      // Save session ID if it's new
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      // Add AI response to UI
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  const resetChat = async () => {
    if (sessionId) {
      await fetch(`${API_URL}/api/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
    }
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <small>Sources: {msg.sources.map(s => s.title).join(', ')}</small>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message assistant">Thinking...</div>}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about installation instructions..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
        <button onClick={resetChat}>Reset</button>
      </div>
    </div>
  );
}
```

### Custom Hook for Chat

```javascript
// hooks/useChat.js
import { useState, useCallback } from 'react';

const API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || 'https://fabulous-healing-production.up.railway.app';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (message, options = {}) => {
    setLoading(true);
    setError(null);

    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: message }]);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          ...options, // temperature, k, filters, etc.
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      // Update session ID if new
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }]);

      return data;
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      }]);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const reset = useCallback(async () => {
    if (sessionId) {
      await fetch(`${API_URL}/api/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
    }
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, [sessionId]);

  return {
    messages,
    sendMessage,
    reset,
    loading,
    error,
    sessionId,
  };
}
```

Usage in a component:

```jsx
import { useChat } from '@/hooks/useChat';

export default function ChatPage() {
  const { messages, sendMessage, reset, loading } = useChat();

  const handleSend = () => {
    const input = document.getElementById('chat-input').value;
    sendMessage(input, {
      temperature: 0.8,
      k: 5,
    });
  };

  return (
    <div>
      {/* Your chat UI */}
    </div>
  );
}
```

## Session Management Best Practices

1. **Store session_id in state or localStorage**
   ```javascript
   // Save to localStorage
   localStorage.setItem('chatSessionId', sessionId);
   
   // Retrieve
   const sessionId = localStorage.getItem('chatSessionId');
   ```

2. **Generate session_id on the client side** (optional)
   ```javascript
   import { v4 as uuidv4 } from 'uuid';
   const sessionId = uuidv4();
   ```

3. **Reset sessions periodically** to avoid very long conversation histories

4. **Note:** Sessions are stored in-memory on the server and will be cleared on restart. For production, consider implementing persistent storage.

## Error Handling

Always wrap API calls in try-catch blocks:

```javascript
try {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello' }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'API request failed');
  }

  const data = await response.json();
  // Use data...
} catch (error) {
  console.error('Chat error:', error);
  // Show error to user
}
```

## Common Use Cases

### 1. Installation Instructions Query

```javascript
const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'How do I install the Greenstar 1000?',
    k: 5
  })
});
```

### 2. Creative Responses

```javascript
const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Explain this in simple terms',
    temperature: 1.0, // More creative
    chat_model: 'gpt-4' // More capable model
  })
});
```

### 3. Focused, Accurate Responses

```javascript
const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What are the exact specifications?',
    temperature: 0.3, // More focused
    k: 3 // Less context, faster
  })
});
```

## Environment Variables

In your Next.js project, add to `.env.local`:

```env
NEXT_PUBLIC_CHAT_API_URL=https://fabulous-healing-production.up.railway.app
```

Or use the default URL directly in your code (already set in examples above).

## Testing the API

You can test the API using curl:

```bash
# Health check
curl https://fabulous-healing-production.up.railway.app/health

# Chat endpoint
curl -X POST https://fabulous-healing-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What installation instructions are available?"}'

# With session ID
curl -X POST https://fabulous-healing-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me more", "session_id": "your-session-id"}'
```

## Need Help?

- Check the interactive API docs at `https://fabulous-healing-production.up.railway.app/docs`
- Review the main README.md for architecture details
- Test endpoints using the Swagger UI at `/docs`
- All endpoints are live and tested on Railway

Happy coding!
