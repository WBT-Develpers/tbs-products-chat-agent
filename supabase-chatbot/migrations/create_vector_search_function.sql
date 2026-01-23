-- Create RPC function for efficient vector similarity search
-- This function uses pgvector's native cosine similarity operator

CREATE OR REPLACE FUNCTION match_products(
  query_embedding vector(1536),  -- Adjust dimension based on your embedding model
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 4,
  is_active_filter boolean DEFAULT true
)
RETURNS TABLE (
  id bigint,
  title varchar,
  subtitle varchar,
  category varchar,
  description text,
  content text,
  product_specs jsonb,
  features jsonb,
  is_active boolean,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.id,
    p.title,
    p.subtitle,
    p.category,
    p.description,
    p.content,
    p.product_specs,
    p.features,
    p.is_active,
    1 - (p.embeddings <=> query_embedding) as similarity
  FROM products p
  WHERE 
    p.is_active = is_active_filter
    AND p.embeddings IS NOT NULL
    AND 1 - (p.embeddings <=> query_embedding) > match_threshold
  ORDER BY p.embeddings <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION match_products TO anon, authenticated;

-- Note: Adjust the vector dimension (1536) based on your embedding model:
-- - text-embedding-3-small: 1536
-- - text-embedding-3-large: 3072
-- - text-embedding-ada-002: 1536
