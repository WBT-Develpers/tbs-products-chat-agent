import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional


DB_PATH = Path(__file__).resolve().parent / "configs.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_database() -> None:
    """Initialize SQLite database and required tables."""
    with get_connection() as conn:
        cur = conn.cursor()

        # system_prompts table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                prompt TEXT NOT NULL,
                agent_type TEXT NOT NULL CHECK(agent_type IN ('pinecone', 'supabase', 'both')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # configurations table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                agent_type TEXT NOT NULL CHECK(agent_type IN ('pinecone', 'supabase')),
                temperature REAL DEFAULT 0.7,
                chat_model TEXT DEFAULT 'gpt-4o-mini',
                k INTEGER DEFAULT 4,
                filters TEXT,
                embedding_model TEXT,
                system_prompt_id INTEGER,
                custom_system_prompt TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(system_prompt_id) REFERENCES system_prompts(id)
            )
            """
        )


def save_system_prompt(title: str, prompt: str, agent_type: str) -> int:
    """Insert a new system prompt and return its ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO system_prompts (title, prompt, agent_type)
            VALUES (?, ?, ?)
            """,
            (title, prompt, agent_type),
        )
        return int(cur.lastrowid)


def get_system_prompts(agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch system prompts, optionally filtered by agent_type."""
    with get_connection() as conn:
        cur = conn.cursor()
        if agent_type:
            cur.execute(
                """
                SELECT * FROM system_prompts
                WHERE agent_type = ? OR agent_type = 'both'
                ORDER BY created_at DESC
                """,
                (agent_type,),
            )
        else:
            cur.execute(
                "SELECT * FROM system_prompts ORDER BY created_at DESC"
            )
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def update_system_prompt(
    prompt_id: int,
    title: str,
    prompt: str,
    agent_type: str,
) -> None:
    """Update an existing system prompt."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE system_prompts
            SET title = ?, prompt = ?, agent_type = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, prompt, agent_type, prompt_id),
        )


def delete_system_prompt(prompt_id: int) -> None:
    """Delete a system prompt by ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM system_prompts WHERE id = ?", (prompt_id,))


def save_configuration(
    name: str,
    agent_type: str,
    params: Dict[str, Any],
    system_prompt_id: Optional[int] = None,
    custom_prompt: Optional[str] = None,
) -> int:
    """Insert a configuration and return its ID."""
    temperature = params.get("temperature")
    chat_model = params.get("chat_model")
    k = params.get("k")
    filters = params.get("filters")
    embedding_model = params.get("embedding_model")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO configurations (
                name,
                agent_type,
                temperature,
                chat_model,
                k,
                filters,
                embedding_model,
                system_prompt_id,
                custom_system_prompt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                agent_type,
                temperature,
                chat_model,
                k,
                filters,
                embedding_model,
                system_prompt_id,
                custom_prompt,
            ),
        )
        return int(cur.lastrowid)


def get_configurations(agent_type: str) -> List[Dict[str, Any]]:
    """Get all configurations for a given agent type."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM configurations
            WHERE agent_type = ?
            ORDER BY created_at DESC
            """,
            (agent_type,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def get_configuration(config_id: int) -> Optional[Dict[str, Any]]:
    """Get a single configuration by ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM configurations WHERE id = ?",
            (config_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def delete_configuration(config_id: int) -> None:
    """Delete a configuration by ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM configurations WHERE id = ?", (config_id,))


# Ensure database is initialized when this module is imported
init_database()

