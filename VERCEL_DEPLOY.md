# Deploying Frontend to Vercel

This guide walks you through deploying the Next.js frontend to Vercel while keeping the backend local (with ngrok tunnel).

## Prerequisites

- Git repository created and pushed to GitHub/GitLab/Bitbucket
- [Vercel account](https://vercel.com/signup) (free)
- Backend running locally
- ngrok installed (for exposing local backend)

## Step 1: Expose Local Backend with ngrok

Since your backend is running locally, you need to expose it to the internet:

```bash
# Install ngrok (if not already installed)
# macOS:
brew install ngrok

# Or download from: https://ngrok.com/download

# Start your backend first
cd backend
uvicorn app.main:app --reload

# In another terminal, expose port 8000
ngrok http 8000
```

Copy the **HTTPS URL** from ngrok output (e.g., `https://abc123.ngrok.io`)

## Step 2: Deploy to Vercel

### Option A: Vercel CLI (Recommended)

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to frontend folder
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: ai-agent-frontend (or your choice)
# - Directory: ./ (default)
# - Build settings: (accept defaults)
```

### Option B: Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Framework preset: **Next.js** (auto-detected)
4. Root directory: **frontend**
5. Click **Deploy**

## Step 3: Configure Environment Variables

After deployment, add the environment variable:

### Via Vercel Dashboard:
1. Go to your project settings
2. Click **Environment Variables**
3. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your ngrok URL (e.g., `https://abc123.ngrok.io`)
   - **Environment**: Production

### Via Vercel CLI:
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Paste your ngrok URL when prompted
```

## Step 4: Redeploy with New Environment Variable

```bash
# Trigger redeploy
vercel --prod
```

Or in the dashboard: **Deployments** → **...** → **Redeploy**

## Step 5: Test Your Deployment

1. Visit your Vercel URL (e.g., `https://ai-agent-frontend.vercel.app`)
2. Go to Settings page
3. Connect Gmail/HubSpot
4. Sync data
5. Test chat interface

## Important Notes

### ngrok Limitations (Free Tier)
- ⚠️ URL changes every time ngrok restarts
- ⚠️ You'll need to update `NEXT_PUBLIC_API_URL` in Vercel each time
- 💡 **Solution**: Get a static ngrok domain ($8/mo) or deploy backend

### CORS Configuration
The backend is already configured to allow requests from any origin:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, update to:
```python
allow_origins=["https://ai-agent-frontend.vercel.app"]
```

## Troubleshooting

### "Network Error" in Frontend
- Check ngrok is running: `curl https://your-ngrok-url.ngrok.io`
- Verify `NEXT_PUBLIC_API_URL` in Vercel matches ngrok URL
- Check backend is running locally

### OAuth Not Working
- Ensure Pipedream redirect URIs include your Vercel domain
- Go to Pipedream dashboard → Your Project → Settings → Add redirect URI

### Environment Variable Not Applied
- Redeploy after adding env vars: `vercel --prod`
- Environment variables only apply to new builds

## Next Steps: Deploy Backend

When ready to deploy the backend permanently:

### Option 1: Railway (Easiest)
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Option 2: Render
1. Create account at [render.com](https://render.com)
2. New Web Service → Connect Git repo
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

### Option 3: Digital Ocean App Platform
1. Create App → From GitHub
2. Select `backend` directory
3. Detect Python buildpack
4. Add environment variables
5. Deploy

Then update Vercel's `NEXT_PUBLIC_API_URL` to your deployed backend URL!

## Useful Commands

```bash
# View deployment logs
vercel logs

# List deployments
vercel ls

# Remove a deployment
vercel rm [deployment-url]

# Update environment variable
vercel env rm NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_API_URL production

# Check which env vars are set
vercel env ls
```

## Summary

✅ Frontend: **Vercel** (deployed)
✅ Backend: **Local** (exposed via ngrok)
✅ FalkorDB: **Cloud** (already configured)

Your app is now accessible from anywhere! 🚀
