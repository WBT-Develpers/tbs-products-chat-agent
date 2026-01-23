# Streamlit Chat UI for Products Chat Agents

This app provides a unified Streamlit interface to chat with both the Pinecone-based and Supabase-based product chat agents. It lets you:

- Switch between agents via tabs
- Tune parameters (temperature, model, k, filters)
- Define and reuse system prompts per agent
- Save and load parameter configurations using a local SQLite database

## Project Structure

```
streamlit-ui/
├── app.py          # Main Streamlit application
├── api_client.py   # API clients for Pinecone and Supabase agents
├── config.py       # Configuration constants (API URLs, defaults)
├── database.py     # SQLite database schema and CRUD helpers
├── requirements.txt
└── configs.db      # SQLite database (auto-created)
```

## Prerequisites

- Python 3.9+ recommended
- The existing APIs deployed and reachable:
  - Pinecone agent: https://fabulous-healing-production.up.railway.app
  - Supabase agent: https://tbs-products-chat-agent-production.up.railway.app

If your deployments use different URLs, you can override them with environment variables:

```bash
export PINECONE_API_URL="https://your-pinecone-api"
export SUPABASE_API_URL="https://your-supabase-api"
```

## Installation

From the repository root:

```bash
cd streamlit-ui
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the App

From the `streamlit-ui` directory (with the virtual environment activated):

```bash
streamlit run app.py
```

The app will open in your browser (typically at http://localhost:8501).

## Using the UI

### Tabs

- **Pinecone Agent**: Talks to the Pinecone-based RAG API.
- **Supabase Agent**: Talks to the Supabase-based products API.

Each tab has its own:

- Chat history
- Session ID
- Parameter controls

### Parameters

In the sidebar for each agent:

- **Temperature**: 0.0–2.0 (controls creativity).
- **Chat Model**: `gpt-4o-mini` or `gpt-4`.
- **k**: Number of documents/products to retrieve (1–20).
- **Filters (JSON)**:
  - Pinecone: Pinecone metadata filter syntax.
  - Supabase: Simple key/value filters.
- **Embedding Model (Supabase only)**: Optional override for the embedding model name.

### System Prompts

Per agent:

- Choose between **Saved Prompt** and **Custom Prompt**.
- **Saved Prompt**:
  - Select from a dropdown of prompts stored in the local SQLite database.
  - Create new prompts with title + body.
  - Delete existing prompts.
- **Custom Prompt**:
  - Type a one-off system prompt for the current session.

### Configurations

Per agent:

- Save the current parameter set (temperature, model, k, filters, embedding model, and current system prompt) as a named configuration.
- Load a saved configuration to restore all parameters and optional custom prompt.
- Delete configurations you no longer need.

### Chat

For each agent:

- Type your message in the text area and click **Send**.
- The app calls the corresponding `/api/chat` endpoint and displays:
  - Assistant response.
  - Source documents/products (in an expandable section).
- The **Session ID** is tracked and shown below the chat, and is passed to the API for follow-up messages.
- Click **Reset Conversation** to:
  - Clear local chat history.
  - Clear the stored session ID.
  - Call the API `/api/reset` endpoint if a session exists.

## Data Storage

- All prompts and configurations are stored locally in `configs.db` (SQLite).
- This file is created automatically the first time you run the app.

## Notes

- This UI assumes the back-end APIs follow the request/response shapes described in the `API_GUIDE.md` files in `pinecone-chatbot/` and `supabase-chatbot/`.
- Error messages from failed HTTP requests are shown in the UI to help with debugging connectivity or deployment issues.

