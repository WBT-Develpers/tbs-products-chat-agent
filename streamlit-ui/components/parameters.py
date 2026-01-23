"""Parameter controls component."""
from typing import Any, Dict, Optional
import streamlit as st
import config
from utils import parse_filters


def render_parameter_controls(agent_type: str, show_header: bool = True) -> Dict[str, Any]:
    """Render parameter controls for the agent."""
    if show_header:
        st.subheader("⚙️ Parameters")
    
    # Quick Presets (compact)
    st.caption("Presets")
    preset_cols = st.columns(len(config.PRESETS))
    for idx, (preset_name, preset_config) in enumerate(config.PRESETS.items()):
        with preset_cols[idx]:
            if st.button(
                preset_name,
                key=f"{agent_type}_preset_{preset_name}",
                use_container_width=True,
                help=preset_config["description"],
            ):
                st.session_state[f"{agent_type}_temperature"] = preset_config["temperature"]
                st.session_state[f"{agent_type}_chat_model"] = preset_config["chat_model"]
                st.session_state[f"{agent_type}_k"] = preset_config["k"]
                st.success(f"✅ Applied '{preset_name}' preset")
                st.rerun()

    # Get current values or defaults
    current_temp = st.session_state.get(f"{agent_type}_temperature", config.DEFAULT_TEMPERATURE)
    current_model = st.session_state.get(f"{agent_type}_chat_model", config.DEFAULT_CHAT_MODEL)
    current_k = st.session_state.get(f"{agent_type}_k", config.DEFAULT_K)
    
    # Temperature (compact)
    temp_is_default = abs(current_temp - config.DEFAULT_TEMPERATURE) < 0.01
    temp_col1, temp_col2 = st.columns([3, 1])
    with temp_col1:
        temperature = st.slider(
            "🌡️ Temperature",
            min_value=float(config.TEMPERATURE_MIN),
            max_value=float(config.TEMPERATURE_MAX),
            value=float(current_temp),
            step=0.1,
            help="Controls creativity vs. determinism. Default: 0.7",
            key=f"{agent_type}_temperature",
        )
    with temp_col2:
        if not temp_is_default and st.button("↩️", key=f"{agent_type}_reset_temp", help="Reset to default"):
            st.session_state[f"{agent_type}_temperature"] = config.DEFAULT_TEMPERATURE
            st.rerun()

    # Chat Model (compact)
    model_is_default = current_model == config.DEFAULT_CHAT_MODEL
    model_col1, model_col2 = st.columns([3, 1])
    with model_col1:
        chat_model = st.selectbox(
            "🤖 Chat Model",
            config.CHAT_MODELS,
            index=config.CHAT_MODELS.index(current_model),
            help="gpt-4o-mini: Fast and cost-effective. gpt-4: More capable but slower.",
            key=f"{agent_type}_chat_model",
        )
    with model_col2:
        if not model_is_default and st.button("↩️", key=f"{agent_type}_reset_model", help="Reset to default"):
            st.session_state[f"{agent_type}_chat_model"] = config.DEFAULT_CHAT_MODEL
            st.rerun()

    # K (compact)
    k_is_default = current_k == config.DEFAULT_K
    k_col1, k_col2 = st.columns([3, 1])
    with k_col1:
        k = st.slider(
            "📚 Documents (k)",
            min_value=config.K_MIN,
            max_value=config.K_MAX,
            value=current_k,
            help=f"Number of documents to retrieve. Default: {config.DEFAULT_K}",
            key=f"{agent_type}_k",
        )
    with k_col2:
        if not k_is_default and st.button("↩️", key=f"{agent_type}_reset_k", help="Reset to default"):
            st.session_state[f"{agent_type}_k"] = config.DEFAULT_K
            st.rerun()

    st.markdown("**🔍 Filters (JSON)**")
    
    # Filter templates (compact)
    if agent_type == "supabase":
        templates = {
            "Active": '{"is_active": true}',
            "Category": '{"category": "electronics"}',
            "Both": '{"is_active": true, "category": "electronics"}',
        }
    else:
        templates = {
            "Manuals": '{"$and": [{"document_type": {"$eq": "installation_manual"}}]}',
            "Source": '{"source": {"$eq": "Greenstar_1000"}}',
            "Complex": '{"$and": [{"document_type": {"$eq": "installation_manual"}}, {"source": {"$eq": "ecofit-pure-830"}}]}',
        }
    
    st.caption("Templates")
    template_cols = st.columns(len(templates))
    for idx, (template_name, template_json) in enumerate(templates.items()):
        with template_cols[idx]:
            if st.button(template_name, key=f"{agent_type}_template_{template_name}", use_container_width=True):
                st.session_state[f"{agent_type}_filters"] = template_json
                st.rerun()
    
    filters_raw = st.text_area(
        "Metadata filters",
        value=st.session_state.get(f"{agent_type}_filters", ""),
        placeholder=(
            '{"is_active": true, "category": "electronics"}'
            if agent_type == "supabase"
            else '{"$and": [{"document_type": {"$eq": "installation_manual"}}]}'
        ),
        key=f"{agent_type}_filters",
        help="Enter valid JSON",
        height=60,
    )
    
    # Real-time JSON validation (compact)
    if filters_raw.strip():
        parsed, error = parse_filters(filters_raw)
        if error:
            st.error(f"❌ {error}")
        else:
            st.success("✅ Valid JSON")

    embedding_model: Optional[str] = None
    if agent_type == "supabase":
        embedding_model = st.text_input(
            "🔤 Embedding Model (optional)",
            value=st.session_state.get("supabase_embedding_model", ""),
            placeholder="text-embedding-3-small",
            help="Optional override for the embedding model. Leave empty to use API default. Common: text-embedding-3-small (1536 dims), text-embedding-3-large (3072 dims).",
            key="supabase_embedding_model",
        )

    return {
        "temperature": temperature,
        "chat_model": chat_model,
        "k": k,
        "filters_raw": filters_raw,
        "embedding_model": embedding_model,
    }
