# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Supabase project with `products` table containing `embeddings` column
- OpenAI API key

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
SUPABASE_URL=https://npeajhtemjbcpnhsqknf.supabase.co
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
```

**Where to find your keys:**
- **Supabase Key**: Go to your Supabase project → Settings → API → `anon` key (or `service_role` key for development - see RLS_SETUP.md)
- **OpenAI API Key**: Get from https://platform.openai.com/api-keys

**Important:** The `products` table has RLS enabled. See `RLS_SETUP.md` for instructions on how to handle this.

### 3. (Optional) Create Vector Search Function

For better performance, you can create a SQL function in Supabase for efficient vector search:

1. Go to your Supabase project → SQL Editor
2. Run the SQL from `migrations/create_vector_search_function.sql`
3. Adjust the vector dimension (1536) if your embeddings use a different model

**Note:** The agent will work without this function, but it will be slower for large datasets.

### 4. Verify Embedding Model

Make sure the `EMBEDDING_MODEL` in your `.env` matches the model used to create the embeddings in your `products` table. Common models:
- `text-embedding-3-small` (1536 dimensions) - Recommended
- `text-embedding-3-large` (3072 dimensions)
- `text-embedding-ada-002` (1536 dimensions)

### 5. Run the Chat Agent

```bash
python chat_agent.py
```

## Usage

Once running, you can:
- Ask questions about products
- Type `reset` to clear conversation history
- Type `exit` or `quit` to end the session

## Troubleshooting

### "Missing required environment variables"
- Make sure your `.env` file exists and contains all required variables
- Check that there are no typos in variable names

### "Error connecting to Supabase"
- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that your Supabase project is active

### "No products found" or poor results
- Ensure your `products` table has data with embeddings
- Verify the embedding model matches what was used to create embeddings
- Check that `is_active = true` products exist

### Slow performance
- Create the vector search function (see step 3 above)
- Reduce the number of retrieved documents (change `k` in `chat_agent.py`)
