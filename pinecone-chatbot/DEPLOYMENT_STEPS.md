# Deployment Steps - Pinecone Chatbot API

## Current Status
✅ Code is ready for deployment
✅ Railway configuration files present (`railway.json`, `Procfile`)
✅ API code complete
❌ Git repository needs to be set up
❌ Railway project needs to be created
❌ Environment variables need to be configured

## Step-by-Step Deployment Guide

### Step 1: Initialize Git Repository (if needed)

If you want `pinecone-chatbot` to be its own repository:

```bash
cd pinecone-chatbot
git init
git add .
git commit -m "Initial commit: Pinecone chatbot API"
```

Or if you're using the parent repository, make sure all files are committed:

```bash
cd /Users/cj/Documents/GitHub/tbs-products-chat-agent
git add pinecone-chatbot/
git commit -m "Add pinecone chatbot API"
```

### Step 2: Push to GitHub

**Option A: Create a new repository on GitHub**
1. Go to https://github.com/new
2. Create a new repository (e.g., `pinecone-chatbot`)
3. Don't initialize with README
4. Copy the repository URL

**Option B: Use existing repository**
- Use the repository URL you have access to

**Then push:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Create Railway Project

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Select your repository (`pinecone-chatbot` or the repo containing it)
6. Railway will automatically detect the `Procfile` and `railway.json`

### Step 4: Set Environment Variables in Railway

In your Railway project dashboard:

1. Go to your project → **Variables** tab
2. Add the following environment variables:

```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=products
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
PORT=8000
```

**Important:** 
- Use your actual Pinecone API key
- Use your actual OpenAI API key
- Make sure `PINECONE_INDEX_NAME` matches your Pinecone index name (default: "products")
- Railway will automatically set `PORT`, but you can set it explicitly

### Step 5: Deploy and Test

1. Railway will automatically deploy when you:
   - Push code to the connected branch
   - Add environment variables (triggers redeploy)

2. Wait for deployment to complete (check the **Deployments** tab)

3. Get your API URL:
   - Go to **Settings** → **Networking**
   - Your app URL will be: `https://your-app-name.railway.app`
   - Or generate a custom domain if preferred

### Step 6: Test the API

**Health Check:**
```bash
curl https://your-app-name.railway.app/health
```

**Test Chat Endpoint:**
```bash
curl -X POST https://your-app-name.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What installation instructions are available?"}'
```

**Or use the interactive docs:**
- Visit: `https://your-app-name.railway.app/docs`

### Step 7: Share with Your Friend

1. **Share the API URL:**
   ```
   https://your-app-name.railway.app
   ```

2. **Share the API Guide:**
   - Send them the `API_GUIDE.md` file
   - Or share the link to the interactive docs: `https://your-app-name.railway.app/docs`

3. **Provide example integration code:**
   - The `API_GUIDE.md` contains complete Next.js integration examples
   - Point them to the "Next.js Integration Examples" section

## Troubleshooting

### Deployment fails
- Check Railway logs in the **Deployments** tab
- Verify all environment variables are set correctly
- Ensure `requirements.txt` is correct
- Check that Pinecone index exists and is accessible

### API returns errors
- Check Railway logs
- Verify Pinecone connection (test with health endpoint)
- Check OpenAI API key is valid
- Ensure Pinecone index name matches your environment variable

### Can't connect to repository
- Ensure Railway has access to your GitHub account
- Check repository permissions
- Try reconnecting the repository in Railway settings

### Embeddings not found
- Make sure you've run the PDF ingestion script (`ingest_pdfs.py`) to populate the Pinecone index
- Verify the index name in Railway matches your Pinecone index
- Check that embeddings were successfully stored (check Pinecone console)

## Checklist

- [ ] Git repository initialized and pushed
- [ ] Railway project created
- [ ] Railway connected to GitHub repository
- [ ] Environment variables set in Railway
- [ ] Pinecone index exists and has data
- [ ] Deployment successful (check logs)
- [ ] Health endpoint works (`/health`)
- [ ] Chat endpoint tested (`/api/chat`)
- [ ] API URL documented
- [ ] API_GUIDE.md shared with friend

## Quick Commands Reference

```bash
# Local development
cd pinecone-chatbot
source venv/bin/activate
uvicorn api:app --reload

# Test locally
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'

# Git workflow
git add .
git commit -m "Your message"
git push origin main
```

## Important Notes

1. **Session Storage**: The current implementation uses in-memory session storage. Sessions will be cleared on server restart. For production with persistent sessions, consider implementing Redis or a database.

2. **Pinecone Index**: Make sure your Pinecone index is populated with embeddings before deploying. Run `python ingest_pdfs.py` locally to populate the index.

3. **CORS**: The API is configured to allow all origins (`*`). For production, you may want to restrict this to your specific frontend domain.

4. **Rate Limiting**: Consider adding rate limiting for production use to prevent abuse.
