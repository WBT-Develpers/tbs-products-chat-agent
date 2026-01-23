"""Current status display component."""
import streamlit as st
import config
from database import get_configuration


def render_current_status(agent_type: str) -> None:
    """Render current configuration and prompt status."""
    st.markdown("**📋 Current Status**")
    
    # Active Configuration
    active_config_id = st.session_state.get(f"{agent_type}_active_config_id")
    if active_config_id:
        config_data = get_configuration(active_config_id)
        if config_data:
            st.success(f"✅ Config: **{config_data['name']}**")
        else:
            st.info("ℹ️ No active configuration")
    else:
        st.info("ℹ️ No active configuration")
    
    # Current Prompt
    current_prompt = st.session_state.get(f"{agent_type}_current_prompt")
    if current_prompt:
        prompt_preview = current_prompt[:100] + "..." if len(current_prompt) > 100 else current_prompt
        with st.expander("💬 Active Prompt", expanded=False):
            st.text(prompt_preview)
            st.caption(f"Length: {len(current_prompt)} chars")
    else:
        st.info("ℹ️ Using default prompt")
    
    # Current Parameters Summary
    temp = st.session_state.get(f"{agent_type}_temperature", config.DEFAULT_TEMPERATURE)
    model = st.session_state.get(f"{agent_type}_chat_model", config.DEFAULT_CHAT_MODEL)
    k_val = st.session_state.get(f"{agent_type}_k", config.DEFAULT_K)
    
    with st.expander("⚙️ Current Parameters", expanded=False):
        st.caption(f"🌡️ Temp: {temp} | 🤖 Model: {model} | 📚 K: {k_val}")
