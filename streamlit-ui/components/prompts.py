"""System prompt management component."""
from typing import Optional
import streamlit as st
from database import (
    delete_system_prompt,
    get_system_prompts,
    save_system_prompt,
    update_system_prompt,
)
from utils import validate_and_fix_system_prompt


def render_system_prompt_section(agent_type: str, show_header: bool = True) -> Optional[str]:
    """Render system prompt section."""
    if show_header:
        st.subheader("💬 System Prompt")
    
    # Show active prompt indicator
    current_prompt = st.session_state.get(f"{agent_type}_current_prompt")
    if current_prompt:
        with st.expander("✅ Active Prompt", expanded=False):
            st.text_area(
                "Currently using:",
                value=current_prompt[:200] + "..." if len(current_prompt) > 200 else current_prompt,
                height=60,
                disabled=True,
                key=f"{agent_type}_active_prompt_display",
            )
    
    mode = st.radio(
        "Prompt source",
        options=["Saved Prompt", "Custom Prompt"],
        key=f"{agent_type}_prompt_mode",
        horizontal=True,
    )

    selected_prompt_text: Optional[str] = None
    selected_prompt_id: Optional[int] = None

    if mode == "Saved Prompt":
        prompts = get_system_prompts(agent_type=agent_type)
        titles = ["(None)"] + [p["title"] for p in prompts]
        selected_title = st.selectbox(
            "Choose a saved prompt",
            titles,
            key=f"{agent_type}_prompt_select",
        )
        if selected_title != "(None)":
            selected = next(p for p in prompts if p["title"] == selected_title)
            selected_prompt_text = selected["prompt"]
            selected_prompt_id = selected["id"]
            st.text_area(
                "Prompt Preview",
                value=selected_prompt_text,
                height=120,
                disabled=True,
                key=f"{agent_type}_prompt_preview",
            )
            # Load button for prompt
            if st.button("📥 Load Prompt", key=f"{agent_type}_load_prompt_btn", use_container_width=True):
                st.session_state[f"{agent_type}_prompt_mode"] = "Saved Prompt"
                st.session_state[f"{agent_type}_prompt_select"] = selected_title
                st.session_state[f"{agent_type}_current_prompt"] = selected_prompt_text
                st.session_state[f"{agent_type}_current_prompt_id"] = selected_prompt_id
                st.success(f"✅ Loaded prompt: {selected_title}")
                st.rerun()

        # Prompt management with tabs
        tab1, tab2 = st.tabs(["➕ Create New", "📝 Manage Existing"])
        
        with tab1:
            st.caption("Create a new prompt for this agent.")
            new_title = st.text_input(
                "Prompt title",
                key=f"{agent_type}_new_prompt_title",
                placeholder="e.g., Technical Support Assistant",
            )
            st.info("💡 **Tip:** Include `{context}` placeholder where retrieved documents will be inserted.")
            new_body = st.text_area(
                "Prompt text",
                key=f"{agent_type}_new_prompt_body",
                height=150,
                placeholder="Enter your system prompt here...\n\nInclude {context} where you want retrieved documents inserted.",
                help="The prompt must include {context} placeholder for RAG to work properly.",
            )
            if new_body:
                char_count = len(new_body)
                st.caption(f"Character count: {char_count}")
            if st.button("💾 Save Prompt", key=f"{agent_type}_save_prompt_btn", use_container_width=True):
                if not new_title or not new_body:
                    st.error("Title and prompt text are required.")
                else:
                    try:
                        save_system_prompt(
                            title=new_title,
                            prompt=new_body,
                            agent_type=agent_type,
                        )
                        st.success("✅ Prompt saved.")
                        st.rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Failed to save prompt: {exc}")

        with tab2:
            if not prompts:
                st.info("No saved prompts yet. Create one in the 'Create New' tab.")
            else:
                st.caption("Edit or delete existing prompts")
                for p in prompts:
                    with st.expander(f"📝 {p['title']}", expanded=False):
                        edit_key = f"{agent_type}_edit_prompt_{p['id']}"
                        if edit_key not in st.session_state:
                            st.session_state[edit_key] = False
                        
                        if not st.session_state[edit_key]:
                            st.text_area(
                                "Current prompt",
                                value=p["prompt"],
                                height=100,
                                disabled=True,
                                key=f"{agent_type}_view_prompt_{p['id']}",
                            )
                            col1, col2 = st.columns(2)
                            if col1.button("✏️ Edit", key=f"{agent_type}_edit_btn_{p['id']}", use_container_width=True):
                                st.session_state[edit_key] = True
                                st.rerun()
                            if col2.button("🗑️ Delete", key=f"{agent_type}_del_btn_{p['id']}", use_container_width=True):
                                delete_system_prompt(p["id"])
                                st.success(f"✅ Deleted prompt '{p['title']}'.")
                                st.rerun()
                        else:
                            # Edit mode
                            edit_title = st.text_input(
                                "Title",
                                value=p["title"],
                                key=f"{agent_type}_edit_title_{p['id']}",
                            )
                            edit_body = st.text_area(
                                "Prompt",
                                value=p["prompt"],
                                height=150,
                                key=f"{agent_type}_edit_body_{p['id']}",
                            )
                            if edit_body:
                                char_count = len(edit_body)
                                st.caption(f"Character count: {char_count}")
                            col1, col2 = st.columns(2)
                            if col1.button("💾 Save Changes", key=f"{agent_type}_save_edit_{p['id']}", use_container_width=True):
                                try:
                                    update_system_prompt(
                                        prompt_id=p["id"],
                                        title=edit_title,
                                        prompt=edit_body,
                                        agent_type=p["agent_type"],
                                    )
                                    st.session_state[edit_key] = False
                                    st.success("✅ Prompt updated.")
                                    st.rerun()
                                except Exception as exc:  # noqa: BLE001
                                    st.error(f"Failed to update: {exc}")
                            if col2.button("❌ Cancel", key=f"{agent_type}_cancel_edit_{p['id']}", use_container_width=True):
                                st.session_state[edit_key] = False
                                st.rerun()

    else:
        st.info("💡 **Tip:** Your prompt should include `{context}` placeholder where retrieved documents will be inserted.")
        custom_prompt_key = f"{agent_type}_custom_prompt"
        selected_prompt_text = st.text_area(
            "Custom system prompt (optional)",
            value=st.session_state.get(custom_prompt_key, ""),
            height=150,
            key=custom_prompt_key,
            placeholder="Enter a custom system prompt for this session...\n\nInclude {context} where you want retrieved documents inserted.",
            help="The prompt must include {context} placeholder. If missing, it will be automatically added.",
        )
        if selected_prompt_text:
            char_count = len(selected_prompt_text)
            st.caption(f"Character count: {char_count}")
            if "{context}" not in selected_prompt_text:
                st.warning("⚠️ Your prompt doesn't include {context}. It will be automatically added when used.")
            if char_count > 2000:
                st.warning("⚠️ Prompt is quite long. Consider using a saved prompt for better management.")

    # Validate and fix prompt if needed
    prompt_value = selected_prompt_text or None
    if prompt_value:
        fixed_prompt, warning = validate_and_fix_system_prompt(prompt_value)
        if warning:
            st.warning(warning)
            prompt_value = fixed_prompt
    
    # Store current prompt in session state for configuration section to access
    st.session_state[f"{agent_type}_current_prompt"] = prompt_value
    st.session_state[f"{agent_type}_current_prompt_id"] = selected_prompt_id
    
    return prompt_value
