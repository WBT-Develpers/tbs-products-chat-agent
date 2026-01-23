"""Utility functions for the Streamlit app."""
import json
from typing import Dict, Optional, Tuple


def parse_filters(raw: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Parse JSON filters and return (parsed_dict, error_message)."""
    if not raw.strip():
        return None, None
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            return None, "Filters must be a JSON object (dictionary)."
        return parsed, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {str(e)}"


def validate_and_fix_system_prompt(prompt: str) -> Tuple[str, Optional[str]]:
    """
    Validate system prompt has {context} placeholder and fix if needed.
    Returns (fixed_prompt, warning_message).
    """
    if not prompt:
        return prompt, None
    
    # Check if prompt contains {context}
    if "{context}" not in prompt:
        # Auto-fix: append context instruction
        fixed_prompt = f"""{prompt}

Use the following pieces of retrieved context to answer the question:
{{context}}

If you don't know the answer based on the context, say so. Don't make up information."""
        warning = "⚠️ Added {context} placeholder to your prompt. The system prompt must include {context} to work with RAG."
        return fixed_prompt, warning
    
    return prompt, None
