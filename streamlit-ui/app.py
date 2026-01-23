"""Main Streamlit application for Products Chat Agents."""
import streamlit as st
from api_client import PineconeAPIClient, SupabaseAPIClient
from components.api_status import render_api_status_indicator
from components.status import render_current_status
from components.parameters import render_parameter_controls
from components.prompts import render_system_prompt_section
from components.configurations import render_configuration_section
from components.chat import render_chat_interface


def init_session_state() -> None:
    """Initialize session state with default values."""
    defaults = {
        "pinecone_messages": [],
        "supabase_messages": [],
        "pinecone_session_id": None,
        "supabase_session_id": None,
        "pinecone_current_prompt": None,
        "supabase_current_prompt": None,
        "pinecone_last_error": None,
        "supabase_last_error": None,
        "pinecone_last_failed_request": None,
        "supabase_last_failed_request": None,
        "pinecone_api_status": None,
        "supabase_api_status": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    """Main application entry point."""
    st.set_page_config(page_title="Products Chat Agents", layout="wide")
    init_session_state()

    # Compact Header
    header_col1, header_col2 = st.columns([2, 1])
    with header_col1:
        st.title("Products Chat Agents")
    with header_col2:
        # API Status indicators (compact)
        pinecone_client = PineconeAPIClient()
        supabase_client = SupabaseAPIClient()
        status_cols = st.columns(2)
        with status_cols[0]:
            render_api_status_indicator("pinecone", pinecone_client)
        with status_cols[1]:
            render_api_status_indicator("supabase", supabase_client)

    # Initialize agent selection in session state
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = "pinecone"

    # Two-column layout: Left (Settings) | Right (Chat)
    left_col, right_col = st.columns([1, 1.5])
    
    # Store params for use in chat interface
    current_params = None
    
    with left_col:
        # Agent Tab Selection (compact)
        selected_agent = st.radio(
            "Agent",
            options=["pinecone", "supabase"],
            format_func=lambda x: "Pinecone" if x == "pinecone" else "Supabase",
            key="agent_selection",
            horizontal=True
        )
        st.session_state.selected_agent = selected_agent
        
        # Process pending configuration loads BEFORE rendering status
        # (This ensures active_config_id is set before status component checks it)
        from database import get_configuration
        pending_load_key = f"{selected_agent}_pending_load_config_id"
        if pending_load_key in st.session_state and st.session_state[pending_load_key] is not None:
            config_id = st.session_state[pending_load_key]
            cfg = get_configuration(config_id)
            if cfg:
                # Set values before widgets are created
                st.session_state[f"{selected_agent}_temperature"] = cfg["temperature"]
                st.session_state[f"{selected_agent}_chat_model"] = cfg["chat_model"]
                st.session_state[f"{selected_agent}_k"] = cfg["k"]
                st.session_state[f"{selected_agent}_filters"] = cfg["filters"] or ""
                if selected_agent == "supabase":
                    st.session_state["supabase_embedding_model"] = (
                        cfg.get("embedding_model") or ""
                    )
                if cfg.get("custom_system_prompt"):
                    st.session_state[f"{selected_agent}_prompt_mode"] = "Custom Prompt"
                    st.session_state[f"{selected_agent}_custom_prompt"] = cfg["custom_system_prompt"]
                    st.session_state[f"{selected_agent}_current_prompt"] = cfg["custom_system_prompt"]
                else:
                    st.session_state[f"{selected_agent}_current_prompt"] = None
                st.session_state[f"{selected_agent}_active_config_id"] = config_id
                # Show success message
                st.success(f"✅ Configuration '{cfg.get('name', 'Unknown')}' loaded.")
            # Clear the pending load flag
            st.session_state[pending_load_key] = None
        
        # Current Status Indicator
        render_current_status(selected_agent)
        st.markdown("---")
        
        if selected_agent == "pinecone":
            # Parameters section
            with st.expander("📊 Parameters", expanded=True):
                current_params = render_parameter_controls("pinecone", show_header=False)
            
            # Configurations section
            with st.expander("💾 Configurations", expanded=False):
                render_configuration_section("pinecone", current_params, None)
            
            # System Prompt section (in expander to save space)
            with st.expander("💬 System Prompt", expanded=False):
                pine_prompt = render_system_prompt_section("pinecone", show_header=False)
        else:
            # Parameters section
            with st.expander("📊 Parameters", expanded=True):
                current_params = render_parameter_controls("supabase", show_header=False)
            
            # Configurations section
            with st.expander("💾 Configurations", expanded=False):
                render_configuration_section("supabase", current_params, None)
            
            # System Prompt section (in expander to save space)
            with st.expander("💬 System Prompt", expanded=False):
                supa_prompt = render_system_prompt_section("supabase", show_header=False)
    
    with right_col:
        # Chat interface
        if current_params:
            if selected_agent == "pinecone":
                render_chat_interface("pinecone", pinecone_client, current_params)
            else:
                render_chat_interface("supabase", supabase_client, current_params)
        else:
            st.warning("⚠️ Parameters not loaded. Please check the Parameters section.")


if __name__ == "__main__":
    main()
