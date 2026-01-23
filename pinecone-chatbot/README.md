# Pinecone Chatbot

RAG-based chatbot using Pinecone vector database for retrieval and OpenAI for generation.

## Overview

This chatbot uses Retrieval Augmented Generation (RAG) to answer questions by:
1. Retrieving relevant documents from Pinecone vector database
2. Using the retrieved context to generate accurate responses with OpenAI

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `pinecone-chatbot` directory with the following:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional: Model Configuration
EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4o-mini
```

### 3. Pinecone Index Setup

Make sure you have a Pinecone index created with:
- Appropriate dimension for your embedding model (e.g., 3072 for `text-embedding-3-large`)
- Metadata fields that match your document structure (e.g., `title`, `category`, `id`)

## Usage

### 1. Test Connection

First, test your Pinecone connection and configuration:

```bash
python test_connection.py
```

This will verify:
- Pinecone API key and index access
- OpenAI API key and embedding generation
- Index exists and is accessible

### 2. CLI Testing

Run the CLI interface to test the chatbot:

```bash
python chat_agent.py
```

The CLI supports:
- Interactive chat with conversation history
- Type `reset` to clear conversation history
- Type `exit` or `quit` to exit

### Example Session

```
You: What products do you have?
Assistant: [Response based on retrieved context]

Sources:
  1. Product Title (Category)
  2. Another Product (Category)
```

### 3. Pinecone Metadata Filters

Pinecone supports metadata filtering. Example filters:

```python
# Filter by category
filters = {"category": {"$eq": "electronics"}}

# Filter by multiple conditions
filters = {
    "$and": [
        {"category": {"$eq": "electronics"}},
        {"is_active": {"$eq": True}}
    ]
}
```

See [Pinecone metadata filtering docs](https://docs.pinecone.io/docs/metadata-filtering) for more examples.

## Architecture

- **`chat_agent.py`**: Main chat agent with RAG implementation and CLI
- **`pinecone_vector_store.py`**: Pinecone vector store integration
- **`models.py`**: Pydantic models for API schemas

## PDF Ingestion

To populate the Pinecone index with product manuals from PDFs:

1. **Place PDF files** in the `pdf/` directory

2. **Run the ingestion script**:
   ```bash
   python ingest_pdfs.py
   ```

The script is **optimized for large PDF files** (75MB+) with:
- ✅ **Parallel PDF processing** - Processes multiple PDFs simultaneously
- ✅ **Batch embedding generation** - Generates embeddings in batches for efficiency
- ✅ **Incremental uploads** - Uploads in batches to avoid memory issues
- ✅ **Progress tracking** - Real-time progress bars for PDF processing and uploads
- ✅ **Time estimates** - Shows estimated completion time
- ✅ **Error recovery** - Continues processing even if one file fails

### Configuration

You can customize the ingestion via environment variables:
```env
PDF_DIRECTORY=pdf              # Directory containing PDFs
PINECONE_INDEX_NAME=products   # Pinecone index name
CHUNK_SIZE=1000                # Text chunk size
CHUNK_OVERLAP=200              # Overlap between chunks
BATCH_SIZE=50                  # Documents per batch (default: 50)
MAX_WORKERS=2                  # Parallel PDF processors (default: 2)
```

**Performance Tips:**
- For very large PDFs (100MB+), consider increasing `BATCH_SIZE` to 100-200
- Increase `MAX_WORKERS` (up to 4) if you have multiple large PDFs and good CPU/memory
- Larger `CHUNK_SIZE` (1500-2000) reduces total chunks but may lose some context granularity

### Adding More Files

Simply add new PDF files to the `pdf/` directory and run the ingestion script again. The script will process all PDFs in the directory.

**Note:** The script processes all PDFs each time. For production, consider adding a file tracking system to skip already-processed files.

## Next Steps

After testing with the CLI, you can create a FastAPI server similar to the `products-chatbot` implementation.
