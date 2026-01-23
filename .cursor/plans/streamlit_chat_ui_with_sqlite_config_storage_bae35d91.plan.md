---
name: Streamlit Chat UI with SQLite Config Storage
overview: Build a Streamlit UI application with tabbed interface for Pinecone and Supabase chatbot agents, including parameter controls, SQLite database for saving configurations and system prompts, and full chat functionality.
todos:
  - id: setup-project-structure
    content: Create streamlit-ui/ folder and initialize project structure with all required files
    status: completed
  - id: implement-database
    content: Implement database.py with SQLite schema, initialization, and CRUD operations for system_prompts and configurations tables
    status: completed
    dependencies:
      - setup-project-structure
  - id: implement-api-client
    content: Create api_client.py with PineconeAPIClient and SupabaseAPIClient classes, including chat, reset, and health_check methods
    status: completed
    dependencies:
      - setup-project-structure
  - id: implement-config
    content: Create config.py with API URLs, default values, and constants for both agents
    status: completed
    dependencies:
      - setup-project-structure
  - id: implement-main-app
    content: Build app.py with Streamlit UI including tabs, parameter controls, system prompt management, configuration management, and chat interface
    status: completed
    dependencies:
      - implement-database
      - implement-api-client
      - implement-config
  - id: create-requirements
    content: Create requirements.txt with streamlit and requests dependencies
    status: completed
    dependencies:
      - setup-project-structure
  - id: create-readme
    content: Create README.md with setup instructions, usage guide, and feature documentation
    status: completed
    dependencies:
      - implement-main-app
---

# Streamlit Chat UI Implementation Plan

## Project Structure

Create a new `streamlit-ui/` folder at the root with the following structure:

```
streamlit-ui/
├── app.py                    # Main Streamlit application
├── database.py               # SQLite database operations
├── api_client.py             # API client for both agents
├── config.py                 # Configuration constants
├── requirements.txt           # Python dependencies
├── README.md                  # Setup and usage instructions
└── configs.db                # SQLite database (auto-created)
```

## Database Schema

### Table 1: `system_prompts`

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `title` TEXT NOT NULL UNIQUE
- `prompt` TEXT NOT NULL
- `agent_type` TEXT NOT NULL CHECK(agent_type IN ('pinecone', 'supabase', 'both'))
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Table 2: `configurations`

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `name` TEXT NOT NULL
- `agent_type` TEXT NOT NULL CHECK(agent_type IN ('pinecone', 'supabase'))
- `temperature` REAL DEFAULT 0.7
- `chat_model` TEXT DEFAULT 'gpt-4o-mini'
- `k` INTEGER DEFAULT 4
- `filters` TEXT (JSON string)
- `embedding_model` TEXT (nullable, Supabase only)
- `system_prompt_id` INTEGER (nullable, FK to system_prompts)
- `custom_system_prompt` TEXT (nullable)
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Implementation Components

### 1. Database Module (`database.py`)

**Functions:**

- `init_database()` - Create tables if they don't exist
- `save_system_prompt(title, prompt, agent_type)` - Save new system prompt
- `get_system_prompts(agent_type=None)` - Retrieve prompts (filtered by agent type)
- `update_system_prompt(id, title, prompt, agent_type)` - Update existing prompt
- `delete_system_prompt(id)` - Delete prompt
- `save_configuration(name, agent_type, params_dict, system_prompt_id=None, custom_prompt=None)` - Save configuration
- `get_configurations(agent_type)` - Get all configs for agent type
- `get_configuration(id)` - Get single configuration
- `delete_configuration(id)` - Delete configuration

**SQLite connection handling:**

- Use `sqlite3` with context managers
- Database file: `configs.db` in the streamlit-ui directory
- Auto-initialize on first import

### 2. API Client Module (`api_client.py`)

**Classes:**

- `PineconeAPIClient` - Handles Pinecone API calls
- `SupabaseAPIClient` - Handles Supabase API calls

**Methods for each:**

- `chat(message, session_id, **params)` - Send chat request, returns response dict
- `reset_session(session_id)` - Reset conversation history
- `health_check()` - Check API status

**API Endpoints:**

- Pinecone: `https://fabulous-healing-production.up.railway.app`
- Supabase: `https://tbs-products-chat-agent-production.up.railway.app`

**Error handling:**

- Try/except for network errors
- Display user-friendly error messages
- Handle JSON parsing errors

### 3. Configuration Module (`config.py`)

**Constants:**

- `PINECONE_API_URL` - Pinecone API base URL
- `SUPABASE_API_URL` - Supabase API base URL
- `DEFAULT_TEMPERATURE` - 0.7
- `DEFAULT_CHAT_MODEL` - 'gpt-4o-mini'
- `DEFAULT_K` - 4
- `CHAT_MODELS` - ['gpt-4o-mini', 'gpt-4']
- `TEMPERATURE_MIN` - 0.0
- `TEMPERATURE_MAX` - 2.0
- `K_MIN` - 1
- `K_MAX` - 20

### 4. Main Application (`app.py`)

**Streamlit Layout:**

```
┌─────────────────────────────────────────┐
│  Header: "Chatbot Agent Interface"     │
├─────────────────────────────────────────┤
│  Tabs: [Pinecone] [Supabase]           │
├──────────────┬──────────────────────────┤
│  Sidebar     │  Main Area                │
│              │                           │
│  Parameters  │  Chat Interface           │
│  Section:    │  - Message History       │
│  - Temp      │  - User Input            │
│  - Model     │  - Send Button          │
│  - K         │  - Reset Button          │
│  - Filters   │  - Sources Display       │
│  - Embedding │                           │
│    (Supabase)│                           │
│              │                           │
│  System      │                           │
│  Prompts:    │                           │
│  - Select    │                           │
│  - Custom    │                           │
│  - Save New  │                           │
│              │                           │
│  Configs:    │                           │
│  - Load      │                           │
│  - Save      │                           │
│  - Delete    │                           │
└──────────────┴──────────────────────────┘
```

**Session State Variables:**

- `pinecone_messages` - List of chat messages
- `supabase_messages` - List of chat messages
- `pinecone_session_id` - Current session ID
- `supabase_session_id` - Current session ID
- `current_tab` - Active tab ('pinecone' or 'supabase')

**Key Functions:**

1. **`render_parameter_controls(agent_type)`**

   - Temperature slider (0.0-2.0, step 0.1)
   - Chat model selectbox
   - K slider (1-20)
   - Filters text area (JSON input with validation)
   - Embedding model text input (Supabase only)
   - Returns dict of parameter values

2. **`render_system_prompt_section(agent_type)`**

   - Radio: "Use Saved Prompt" or "Custom Prompt"
   - Dropdown of saved prompts (filtered by agent_type or 'both')
   - Text area for custom prompt
   - "Save New Prompt" button with modal/form
   - Returns selected prompt text

3. **`render_configuration_section(agent_type)`**

   - Dropdown of saved configurations
   - "Load Config" button
   - "Save Current Config" button (with name input)
   - "Delete Config" button
   - Load applies all parameters to UI

4. **`render_chat_interface(agent_type, messages, session_id)`**

   - Display message history (user/assistant)
   - Show sources for each assistant message
   - Text input for new message
   - Send button
   - Reset button (calls API reset endpoint)

5. **`handle_chat_message(agent_type, message, params, session_id)`**

   - Call appropriate API client
   - Update session state with response
   - Handle errors gracefully
   - Display loading spinner during request

**Tab Implementation:**

- Use `st.tabs()` for Pinecone/Supabase switching
- Each tab maintains separate session state
- Parameters persist when switching tabs

## Features Implementation

### System Prompts Management

1. **Save New Prompt:**

   - Modal/form with:
     - Title input (required, unique)
     - Prompt text area
     - Agent type radio ('pinecone', 'supabase', 'both')
   - Validation: title must be unique
   - Success/error feedback

2. **Select Saved Prompt:**

   - Dropdown filtered by current agent type
   - Shows prompts where agent_type matches or is 'both'
   - Displays prompt preview on selection

3. **Edit/Delete Prompts:**

   - Expandable section showing all prompts
   - Edit button opens form with current values
   - Delete button with confirmation

### Configuration Management

1. **Save Configuration:**

   - Collect all current parameter values
   - Get selected system prompt (saved or custom)
   - Name input (required)
   - Save to database
   - Success notification

2. **Load Configuration:**

   - Select from dropdown
   - Apply all parameters to UI controls
   - Load system prompt (saved ID or custom text)
   - Update session state

3. **Delete Configuration:**

   - Select from dropdown
   - Confirmation dialog
   - Remove from database

### Filters Handling

- **Pinecone:** JSON text area with example:
  ```json
  {
    "$and": [
      {"document_type": {"$eq": "installation_manual"}},
      {"source": {"$eq": "Greenstar_1000"}}
    ]
  }
  ```

- **Supabase:** JSON text area with example:
  ```json
  {
    "is_active": true,
    "category": "electronics"
  }
  ```

- JSON validation before sending
- Error message if invalid JSON

## Dependencies (`requirements.txt`)

```
streamlit>=1.28.0
requests>=2.31.0
```

## Error Handling

- API connection errors: Display user-friendly message
- Invalid JSON filters: Show validation error
- Database errors: Log and show error message
- Missing required fields: Validation before save
- Duplicate names: Check uniqueness before save

## UI/UX Enhancements

- Loading spinners during API calls
- Success/error notifications using `st.success()` and `st.error()`
- Collapsible sections for better organization
- Tooltips/help text for parameters
- Default values clearly displayed
- Session ID display (read-only, for debugging)

## Testing Considerations

- Test with both API endpoints
- Verify SQLite operations (CRUD)
- Test parameter persistence across tab switches
- Validate JSON filter inputs
- Test error scenarios (API down, invalid JSON, etc.)

## Future Enhancements (Optional)

- Export/import configurations as JSON
- Configuration comparison view
- Usage statistics/history
- Multiple session management
- Configuration templates/presets