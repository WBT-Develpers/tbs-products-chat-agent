-- Create conversations table for storing chat session history
-- This table stores conversation history for each session_id

CREATE TABLE IF NOT EXISTS conversations (
    session_id TEXT PRIMARY KEY,
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on session_id for fast lookups (already primary key, but explicit for clarity)
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

-- Create index on updated_at for cleanup queries (optional, for TTL/cleanup policies)
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on row updates
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust based on your RLS policies)
-- For now, grant to authenticated users - you may want to add RLS policies
GRANT SELECT, INSERT, UPDATE, DELETE ON conversations TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON conversations TO anon;

-- Optional: Add RLS (Row Level Security) policies if needed
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- 
-- Example RLS policy (uncomment and adjust as needed):
-- CREATE POLICY "Users can manage their own sessions" ON conversations
--     FOR ALL
--     USING (auth.uid()::text = session_id OR session_id LIKE auth.uid()::text || '-%');

-- Optional: Add cleanup function for old sessions (older than 30 days)
-- This can be called periodically via a cron job or scheduled task
CREATE OR REPLACE FUNCTION cleanup_old_conversations(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversations
    WHERE updated_at < NOW() - (days_old || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Note: The messages JSONB column stores LangChain message objects in this format:
-- [
--   {"type": "human", "content": "user message"},
--   {"type": "ai", "content": "ai response"},
--   ...
-- ]
