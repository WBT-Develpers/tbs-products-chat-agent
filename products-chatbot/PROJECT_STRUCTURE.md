# Project Structure

```
products-chatbot/
├── chat_agent.py              # Main chat agent with CLI interface
├── supabase_vector_store.py   # Custom Supabase vector store for RAG
├── test_setup.py              # Setup verification script
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── SETUP.md                    # Detailed setup instructions
├── RLS_SETUP.md               # Row Level Security configuration guide
├── .gitignore                 # Git ignore rules
├── migrations/
│   └── create_vector_search_function.sql  # Optional SQL function for performance
└── venv/                      # Virtual environment (not in git)
```

## Core Files

- **chat_agent.py**: Main entry point for the RAG chat agent
- **supabase_vector_store.py**: Custom vector store implementation for Supabase pgvector
- **test_setup.py**: Utility to verify Supabase and OpenAI connections

## Documentation

- **README.md**: Quick start guide and overview
- **SETUP.md**: Detailed installation and configuration steps
- **RLS_SETUP.md**: Guide for handling Row Level Security policies

## Configuration

- **requirements.txt**: Python package dependencies
- **.env**: Environment variables (create from .env.example, not in git)

## Optional

- **migrations/**: SQL migration for vector search function (optional, improves performance)
