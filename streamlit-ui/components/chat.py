"""Chat interface component."""
from typing import Any, Dict, List
import streamlit as st
from api_client import APIRequestError, NetworkError
from utils import parse_filters, validate_and_fix_system_prompt


def render_chat_interface(
    agent_type: str,
    client: Any,
    params: Dict[str, Any],
) -> None:
    """Render chat interface."""
    st.markdown("### Chat")

    messages_key = f"{agent_type}_messages"
    session_key = f"{agent_type}_session_id"

    messages: List[Dict[str, Any]] = st.session_state[messages_key]

    # Message history container with auto-scroll
    chat_container = st.container()
    with chat_container:
        if not messages:
            st.info("Start a conversation by sending a message below.")
        else:
            for msg in messages:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                sources = msg.get("sources") or []
                
                # Use st.chat_message for proper styling
                with st.chat_message(role):
                    st.write(content)
                    
                    # Display sources inline with badges
                    if sources:
                        st.markdown("---")
                        st.caption(f"📚 Sources ({len(sources)}):")
                        source_cols = st.columns(min(len(sources), 3))
                        for idx, src in enumerate(sources):
                            col_idx = idx % 3
                            with source_cols[col_idx]:
                                category = src.get('category', '')
                                title = src.get('title', 'Unknown')
                                if category:
                                    st.markdown(f"**{title}**")
                                    st.caption(f"`{category}`")
                                else:
                                    st.markdown(f"**{title}**")

    # Use st.chat_input for better chat experience
    user_message = st.chat_input(
        "Type your message here...",
        key=f"{agent_type}_input",
    )

    if user_message:
        if not user_message.strip():
            st.error("Please enter a message.")
        else:
            filters_parsed, filter_error = parse_filters(params["filters_raw"])
            if params["filters_raw"] and filter_error:
                st.error(f"Cannot send message: {filter_error}")
                return

            st.session_state[messages_key].append(
                {"role": "user", "content": user_message}
            )

            # Store request for retry
            request_data = {
                "message": user_message,
                "params": params,
                "filters_parsed": filters_parsed,
            }
            st.session_state[f"{agent_type}_last_failed_request"] = request_data

            with st.spinner("Calling API..."):
                try:
                    session_id = st.session_state[session_key]
                    # Get current system prompt from session state and validate/fix
                    current_prompt = st.session_state.get(f"{agent_type}_current_prompt")
                    if current_prompt:
                        fixed_prompt, warning = validate_and_fix_system_prompt(current_prompt)
                        if warning:
                            st.warning(warning)
                        current_prompt = fixed_prompt
                    
                    if agent_type == "pinecone":
                        payload = client.build_payload(
                            message=user_message,
                            session_id=session_id,
                            temperature=params["temperature"],
                            chat_model=params["chat_model"],
                            k=params["k"],
                            filters=filters_parsed,
                            system_prompt=current_prompt,
                        )
                    else:
                        payload = client.build_payload(
                            message=user_message,
                            session_id=session_id,
                            temperature=params["temperature"],
                            chat_model=params["chat_model"],
                            embedding_model=params.get("embedding_model") or None,
                            k=params["k"],
                            filters=filters_parsed,
                            system_prompt=current_prompt,
                        )

                    data = client.chat(payload)
                    answer = data.get("answer", "")
                    sources = data.get("sources") or []
                    new_session_id = data.get("session_id")
                    if new_session_id:
                        st.session_state[session_key] = new_session_id

                    # Clear error state on success
                    st.session_state[f"{agent_type}_last_error"] = None
                    st.session_state[f"{agent_type}_last_failed_request"] = None

                    st.session_state[messages_key].append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                    st.rerun()
                except NetworkError as e:
                    error_msg = f"🌐 Network Error: {e.message}"
                    if e.details:
                        error_msg += f"\n\nDetails: {e.details}"
                    st.error(error_msg)
                    st.session_state[f"{agent_type}_last_error"] = error_msg
                    st.info("💡 **Tip:** Check your internet connection and API URL. You can retry the request below.")
                except APIRequestError as e:
                    error_msg = f"⚠️ API Error: {e.message}"
                    if e.details:
                        error_msg += f"\n\nDetails: {e.details}"
                    if e.status_code == 400:
                        error_msg += "\n\n💡 **Tip:** Check your request parameters (filters, message format, etc.)."
                    elif e.status_code == 401:
                        error_msg += "\n\n💡 **Tip:** Check your API authentication credentials."
                    elif e.status_code >= 500:
                        error_msg += "\n\n💡 **Tip:** The server may be experiencing issues. Please try again later."
                    st.error(error_msg)
                    st.session_state[f"{agent_type}_last_error"] = error_msg
                except Exception as exc:  # noqa: BLE001
                    error_msg = f"❌ Unexpected error: {str(exc)}"
                    st.error(error_msg)
                    st.session_state[f"{agent_type}_last_error"] = error_msg

    # Retry button for failed requests
    if st.session_state.get(f"{agent_type}_last_failed_request"):
        if st.button("🔄 Retry Last Request", key=f"{agent_type}_retry_btn"):
            st.rerun()

    # Reset button and session info
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Reset Conversation", key=f"{agent_type}_reset_btn", use_container_width=True):
            session_id = st.session_state.get(session_key)
            st.session_state[messages_key] = []
            st.session_state[session_key] = None
            if session_id:
                try:
                    client.reset_session(session_id)
                except Exception:  # noqa: BLE001
                    # Non-fatal if reset fails
                    pass
            st.success("Conversation reset.")
            st.rerun()
    
    with col2:
        with st.expander("ℹ️ Session Info", expanded=False):
            session_id = st.session_state.get(session_key)
            if session_id:
                st.code(session_id, language=None)
                if st.button("📋 Copy Session ID", key=f"{agent_type}_copy_session"):
                    st.success("Session ID copied to clipboard!")
            else:
                st.caption("Session ID will be created on first message.")
