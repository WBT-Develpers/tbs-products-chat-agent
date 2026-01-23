import os

PINECONE_API_URL = os.getenv(
    "PINECONE_API_URL",
    "https://fabulous-healing-production.up.railway.app",
)

SUPABASE_API_URL = os.getenv(
    "SUPABASE_API_URL",
    "https://tbs-products-chat-agent-production.up.railway.app",
)

DEFAULT_TEMPERATURE = 0.7
DEFAULT_CHAT_MODEL = "gpt-4o-mini"
DEFAULT_K = 4

CHAT_MODELS = ["gpt-4o-mini", "gpt-4"]

TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 2.0

K_MIN = 1
K_MAX = 20

# Parameter Presets
PRESETS = {
    "High Accuracy": {
        "temperature": 0.3,
        "chat_model": "gpt-4o-mini",
        "k": 5,
        "description": "Focused, deterministic responses with more context",
    },
    "Creative": {
        "temperature": 1.2,
        "chat_model": "gpt-4",
        "k": 6,
        "description": "More creative and varied responses",
    },
    "Balanced": {
        "temperature": 0.7,
        "chat_model": "gpt-4o-mini",
        "k": 4,
        "description": "Default balanced settings",
    },
    "Fast": {
        "temperature": 0.5,
        "chat_model": "gpt-4o-mini",
        "k": 2,
        "description": "Quick responses with minimal context",
    },
}
