"""
Session Manager for storing and retrieving conversation history in Supabase.

Handles conversation history persistence using Supabase as the storage backend.
Converts LangChain message format to/from JSON for database storage.
"""
import json
from typing import List, Optional
from datetime import datetime
from supabase import create_client, Client
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.messages import message_to_dict, messages_from_dict


class SessionManager:
    """Manages conversation sessions stored in Supabase."""
    
    def __init__(self, supabase_client: Client, table_name: str = "conversations"):
        """
        Initialize session manager.
        
        Args:
            supabase_client: Supabase client instance
            table_name: Name of the conversations table in Supabase
        """
        self.supabase = supabase_client
        self.table_name = table_name
    
    def get_conversation_history(self, session_id: str) -> List[BaseMessage]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of LangChain message objects, empty list if session doesn't exist
        """
        try:
            response = self.supabase.table(self.table_name).select("messages").eq(
                "session_id", session_id
            ).execute()
            
            if response.data and len(response.data) > 0:
                messages_json = response.data[0].get("messages", [])
                if messages_json:
                    # Convert JSON back to LangChain messages
                    return messages_from_dict(messages_json)
            return []
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def save_conversation_history(
        self, 
        session_id: str, 
        messages: List[BaseMessage]
    ) -> bool:
        """
        Save conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            messages: List of LangChain message objects
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert messages to JSON-serializable format
            messages_dict = [message_to_dict(msg) for msg in messages]
            
            # Check if session exists
            existing = self.supabase.table(self.table_name).select("session_id").eq(
                "session_id", session_id
            ).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing session
                self.supabase.table(self.table_name).update({
                    "messages": messages_dict,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("session_id", session_id).execute()
            else:
                # Create new session
                self.supabase.table(self.table_name).insert({
                    "session_id": session_id,
                    "messages": messages_dict,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).execute()
            
            return True
        except Exception as e:
            print(f"Error saving conversation history: {e}")
            return False
    
    def add_message_to_session(
        self, 
        session_id: str, 
        user_message: str, 
        ai_message: str
    ) -> bool:
        """
        Add a new message pair (user + AI) to an existing session.
        
        Args:
            session_id: Unique session identifier
            user_message: User's message text
            ai_message: AI's response text
            
        Returns:
            True if successful, False otherwise
        """
        # Get existing history
        existing_messages = self.get_conversation_history(session_id)
        
        # Add new messages
        existing_messages.append(HumanMessage(content=user_message))
        existing_messages.append(AIMessage(content=ai_message))
        
        # Save updated history
        return self.save_conversation_history(session_id, existing_messages)
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.supabase.table(self.table_name).update({
                "messages": [],
                "updated_at": datetime.utcnow().isoformat()
            }).eq("session_id", session_id).execute()
            return True
        except Exception as e:
            print(f"Error clearing session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session entirely from the database.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.supabase.table(self.table_name).delete().eq(
                "session_id", session_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False


def create_session_manager(
    supabase_url: str,
    supabase_key: str,
    table_name: str = "conversations"
) -> SessionManager:
    """
    Factory function to create a SessionManager instance.
    
    Args:
        supabase_url: Supabase project URL
        supabase_key: Supabase anon/service key
        table_name: Name of the conversations table
        
    Returns:
        SessionManager instance
    """
    supabase_client = create_client(supabase_url, supabase_key)
    return SessionManager(supabase_client, table_name)
