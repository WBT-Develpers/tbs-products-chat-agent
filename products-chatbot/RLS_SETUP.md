# Row Level Security (RLS) Setup

## Issue

The `products` table has Row Level Security (RLS) enabled, which means the `anon` key cannot read products by default. This is a security feature, but it will block the chat agent from retrieving products.

## Solutions

### Option 1: Use Service Role Key (Recommended for Development/Testing)

For development and testing, you can use the `service_role` key which bypasses RLS:

1. Go to your Supabase project → Settings → API
2. Copy the `service_role` key (keep this secret!)
3. Update your `.env` file:
   ```env
   SUPABASE_KEY=your_service_role_key_here
   ```

**⚠️ Warning:** Never commit the service_role key to git or expose it in client-side code. It has full database access.

### Option 2: Create RLS Policy for Anon Access (Recommended for Production)

If you want to allow anonymous read access to products, create an RLS policy:

1. Go to your Supabase project → SQL Editor
2. Run this SQL:

```sql
-- Allow anonymous users to read active products
CREATE POLICY "Allow anon read access to active products"
ON products
FOR SELECT
TO anon
USING (is_active = true);
```

This allows anonymous users to read products where `is_active = true`.

### Option 3: Authenticate with User Session

If you want to require authentication, you'll need to:

1. Authenticate users in your application
2. Pass the user's session token to Supabase
3. Update the chat agent to use authenticated sessions

This is more complex but provides better security.

## Current Status

The test script will show a warning about RLS, but the setup is considered valid. The chat agent will work once you:
- Use a service_role key, OR
- Set up RLS policies, OR  
- Implement user authentication

## Testing

After applying one of the solutions above, run the test again:

```bash
source venv/bin/activate
python test_setup.py
```

You should see products being returned.
