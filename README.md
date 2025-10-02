# AI Agent MVP - Gmail + HubSpot Knowledge Graph

An AI agent application that syncs Gmail and HubSpot data into a Graphiti knowledge graph (stored in FalkorDB) and provides an intelligent chat interface to query your business data.

## Tech Stack

**Backend:**
- FastAPI (Python)
- Graphiti + FalkorDB (Knowledge Graph)
- Pipedream Connect (OAuth & API proxy)
- OpenAI GPT-4 (AI Agent)

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- TanStack Query

## Prerequisites

Before you begin, ensure you have:

- Python 3.11+
- Node.js 18+
- Docker Desktop
- [Pipedream Connect](https://pipedream.com/connect) account (free)
- OpenAI API key

## Setup Instructions

### 1. Start FalkorDB

First, ensure FalkorDB is running:

```bash
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  -v falkordb-data:/data \
  falkordb/falkordb:latest
```

Verify it's running:
```bash
docker ps
```

### 2. Get Pipedream Credentials

1. Go to [Pipedream Connect](https://pipedream.com/connect)
2. Create a new project
3. Copy the following credentials:
   - Project ID
   - Client ID
   - Client Secret

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `backend/.env` with your credentials:

```env
# Pipedream
PIPEDREAM_PROJECT_ID=your_project_id
PIPEDREAM_CLIENT_ID=your_client_id
PIPEDREAM_CLIENT_SECRET=your_client_secret

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_DATABASE=my_app_graph

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
```

Start the backend:
```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Using the Application

### 1. Connect Your Apps

1. Navigate to `http://localhost:3000/settings`
2. Click "Connect" for Gmail
   - Authorize via Pipedream OAuth popup
   - Wait for connection confirmation
3. Click "Connect" for HubSpot
   - Authorize via Pipedream OAuth popup
   - Wait for connection confirmation

### 2. Sync Your Data

After connecting, click "Sync Now" for each integration:
- **Gmail**: Syncs last 3 months of emails
- **HubSpot**: Syncs all contacts, deals, and companies

The sync process:
1. Fetches data via Pipedream proxy
2. Processes into Graphiti episodes
3. Stores in FalkorDB knowledge graph

### 3. Chat with Your Data

1. Navigate to `http://localhost:3000`
2. Ask questions like:
   - "What emails did I receive this week?"
   - "Show me all deals in progress"
   - "Who are my top contacts?"
   - "Summarize conversations with [Company Name]"

The AI agent will:
- Search the knowledge graph for relevant context
- Use GPT-4 to generate intelligent responses
- Cite sources from your data

## Docker Compose (Alternative Setup)

To run the entire stack with Docker:

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit both .env files with your credentials

# Start all services
docker-compose up
```

Access:
- Frontend: `http://localhost:3001`
- Backend API: `http://localhost:8000`
- FalkorDB UI: `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/v1/auth/connect-token` - Generate Pipedream Connect token

### Integrations
- `POST /api/v1/integrations/gmail/save` - Save Gmail account ID
- `POST /api/v1/integrations/hubspot/save` - Save HubSpot account ID

### Sync
- `POST /api/v1/sync/gmail` - Sync Gmail emails
- `POST /api/v1/sync/hubspot` - Sync HubSpot data
- `GET /api/v1/sync/status` - Get sync status

### AI Agent
- `POST /api/v1/agent/chat` - Chat with AI agent

## Project Structure

```
my-ai-app/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Settings
│   │   ├── clients/
│   │   │   └── pipedream.py          # Pipedream client
│   │   ├── services/
│   │   │   ├── graphiti_service.py   # Knowledge graph
│   │   │   ├── agent_service.py      # AI agent
│   │   │   ├── gmail_sync.py         # Gmail sync
│   │   │   └── hubspot_sync.py       # HubSpot sync
│   │   └── storage/
│   │       └── connected_accounts.json
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx              # Chat page
    │   │   └── settings/
    │   │       └── page.tsx          # Integrations
    │   └── lib/
    │       └── api-client.ts
    └── package.json
```

## How It Works

### Data Flow

1. **OAuth Connection**
   - User clicks "Connect Gmail/HubSpot"
   - Frontend requests Pipedream Connect token from backend
   - Pipedream OAuth popup opens
   - Account ID saved to backend

2. **Data Sync**
   - User clicks "Sync Now"
   - Backend fetches data via Pipedream proxy API
   - Data converted to Graphiti episodes
   - Episodes stored in FalkorDB

3. **AI Chat**
   - User asks question
   - Graphiti searches knowledge graph
   - Relevant facts sent to GPT-4 as context
   - AI generates answer with sources

### Knowledge Graph

Graphiti automatically:
- Extracts entities (people, companies, deals)
- Identifies relationships
- Tracks temporal changes
- Enables semantic search

## Troubleshooting

### FalkorDB Connection Error
```bash
# Check if FalkorDB is running
docker ps

# Restart if needed
docker restart falkordb
```

### Pipedream OAuth Not Working
- Verify your Pipedream credentials in `.env`
- Check that redirect URIs are configured in Pipedream dashboard
- Ensure frontend can reach backend API

### Sync Failing
- Check backend logs: `uvicorn app.main:app --reload`
- Verify OAuth tokens are valid
- Check Pipedream account has necessary permissions

### No Results in Chat
- Ensure data has been synced (check settings page)
- Try more specific questions
- Check FalkorDB has data: Visit `http://localhost:3000` (FalkorDB UI)

## Development

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

### Frontend
```bash
cd frontend
npm run dev
```

### View Logs
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# FalkorDB logs
docker logs falkordb
```

## Deployment

### Frontend to Vercel

See detailed instructions in [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)

**Quick Deploy:**
```bash
cd frontend
vercel

# Set environment variable in Vercel dashboard:
# NEXT_PUBLIC_API_URL = https://your-ngrok-url.ngrok.io
```

**Expose local backend with ngrok:**
```bash
ngrok http 8000
# Copy HTTPS URL and add to Vercel env vars
```

### Backend Deployment Options

When ready to deploy backend permanently:
- **Railway**: `railway init && railway up`
- **Render**: Connect repo, auto-deploy
- **Digital Ocean**: App Platform

## Next Steps

**MVP Enhancements:**
- [ ] Add webhook support for real-time updates
- [ ] Implement pagination for large datasets
- [ ] Add more HubSpot objects (tasks, notes)
- [ ] Improve entity resolution across sources
- [ ] Add user authentication
- [ ] Deploy backend to production

## License

MIT

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend/frontend logs
3. Open an issue on GitHub
