"""API status indicator component."""
from typing import Any
import streamlit as st


def render_api_status_indicator(agent_type: str, client: Any) -> None:
    """Render API status indicator."""
    status_key = f"{agent_type}_api_status"
    
    # Check status on first load or if not checked recently
    if status_key not in st.session_state or st.session_state[status_key] is None:
        is_healthy, error = client.health_check()
        st.session_state[status_key] = {"healthy": is_healthy, "error": error}
    
    status = st.session_state[status_key]
    if status["healthy"]:
        st.success(f"✅ {agent_type.capitalize()} API: Online")
    else:
        st.error(f"❌ {agent_type.capitalize()} API: Offline")
        if status["error"]:
            st.caption(f"Error: {status['error']}")
