"""Configuration management component."""
import json
from typing import Any, Dict, Optional
import streamlit as st
from database import (
    delete_configuration,
    get_configuration,
    get_configurations,
    save_configuration,
)
from utils import parse_filters


def render_configuration_section(
    agent_type: str,
    params: Dict[str, Any],
    system_prompt: Optional[str],
) -> None:
    """Render configuration management section."""
    st.subheader("💾 Configurations")

    configs = get_configurations(agent_type=agent_type)
    
    # Create mapping for clean display (name -> id)
    config_map = {c['name']: c['id'] for c in configs}
    active_config_id = st.session_state.get(f"{agent_type}_active_config_id")
    
    # Display options with active indicator
    options = ["(None)"] + [c['name'] for c in configs]
    if active_config_id:
        # Find active config name
        active_config = next((c for c in configs if c['id'] == active_config_id), None)
        if active_config:
            # Highlight active config in options
            default_idx = options.index(active_config['name']) if active_config['name'] in options else 0
        else:
            default_idx = 0
    else:
        default_idx = 0
    
    selected_name = st.selectbox(
        "Saved configurations",
        options,
        index=default_idx,
        key=f"{agent_type}_config_select",
    )

    # Show active indicator
    if active_config_id and selected_name != "(None)":
        selected_id = config_map.get(selected_name)
        if selected_id == active_config_id:
            st.success("✅ This configuration is currently active")

    # Configuration preview
    if selected_name != "(None)":
        selected_id = config_map.get(selected_name)
        if selected_id:
            cfg = get_configuration(selected_id)
            if cfg:
                with st.expander("📋 Preview Configuration", expanded=False):
                    st.json({
                        "Temperature": cfg["temperature"],
                        "Chat Model": cfg["chat_model"],
                        "K (Documents)": cfg["k"],
                        "Filters": json.loads(cfg["filters"]) if cfg.get("filters") else None,
                        "Embedding Model": cfg.get("embedding_model"),
                        "System Prompt": cfg.get("custom_system_prompt", "None"),
                    })

    # Save current
    st.markdown("---")
    config_name = st.text_input(
        "💾 Save current settings as:",
        key=f"{agent_type}_config_name",
        placeholder="e.g., High Accuracy Mode",
    )
    if st.button("💾 Save Configuration", key=f"{agent_type}_save_config_btn", use_container_width=True):
        if not config_name:
            st.error("Configuration name is required.")
        else:
            filters_parsed, filter_error = parse_filters(params["filters_raw"])
            if params["filters_raw"] and filter_error:
                st.error(f"Cannot save: {filter_error}")
                return
            filters_str = (
                json.dumps(filters_parsed) if filters_parsed is not None else None
            )
            payload = {
                "temperature": params["temperature"],
                "chat_model": params["chat_model"],
                "k": params["k"],
                "filters": filters_str,
                "embedding_model": params.get("embedding_model"),
            }
            # Get current system prompt from session state (set by render_system_prompt_section)
            current_prompt = st.session_state.get(f"{agent_type}_current_prompt")
            try:
                save_configuration(
                    name=config_name,
                    agent_type=agent_type,
                    params=payload,
                    system_prompt_id=None,
                    custom_prompt=current_prompt,
                )
                st.success("✅ Configuration saved.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Failed to save configuration: {exc}")

    # Load / delete
    if selected_name != "(None)":
        selected_id = config_map.get(selected_name)
        if selected_id:
            col_load, col_delete = st.columns(2)
            if col_load.button("📥 Load", key=f"{agent_type}_load_config_btn", use_container_width=True):
                # Store config_id to load on next render cycle (before widgets are created)
                st.session_state[f"{agent_type}_pending_load_config_id"] = selected_id
                st.rerun()

            if col_delete.button("🗑️ Delete", key=f"{agent_type}_delete_config_btn", use_container_width=True):
                # Confirmation
                confirm_key = f"{agent_type}_delete_confirm_{selected_id}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                if not st.session_state[confirm_key]:
                    st.warning(f"⚠️ Are you sure you want to delete '{selected_name}'?")
                    if st.button("✅ Confirm Delete", key=f"{agent_type}_confirm_delete_{selected_id}"):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    delete_configuration(selected_id)
                    if active_config_id == selected_id:
                        st.session_state[f"{agent_type}_active_config_id"] = None
                    st.success(f"✅ Configuration '{selected_name}' deleted.")
                    st.session_state[confirm_key] = False
                    st.rerun()
