from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os
from pathlib import Path

from app.clients.pipedream import pipedream_client
from app.services.graphiti_service import graphiti_service
from app.services.agent_service import agent_service
from app.services.gmail_sync import sync_gmail_last_3_months
from app.services.hubspot_sync import sync_hubspot_all


# Initialize FastAPI app
app = FastAPI(title="AI Agent MVP API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel deployments
        "https://k-gmvp.vercel.app"  # Your Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to connected accounts storage
STORAGE_PATH = Path(__file__).parent / "storage" / "connected_accounts.json"


# Pydantic models
class ConnectTokenResponse(BaseModel):
    token: str
    connectLinkUrl: str  # PROVEN PATTERN: Return ready-to-use URL


class SaveAccountRequest(BaseModel):
    account_id: str


class SaveAccountResponse(BaseModel):
    status: str


class SyncResponse(BaseModel):
    synced: int
    status: str


class SyncStatusResponse(BaseModel):
    gmail: dict
    hubspot: dict


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


class IngestRequest(BaseModel):
    data: dict
    source: str  # "gmail", "hubspot", etc.


# Helper functions
def load_accounts() -> dict:
    """Load connected accounts from JSON file"""
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)
    return {
        "gmail_account_id": None,
        "hubspot_account_id": None,
        "last_sync": {"gmail": None, "hubspot": None}
    }


def save_accounts(data: dict):
    """Save connected accounts to JSON file"""
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize Graphiti on startup"""
    print("Initializing Graphiti knowledge graph...")
    await graphiti_service.initialize()
    print("✓ Graphiti initialized successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections"""
    await graphiti_service.close()
    await pipedream_client.close()


# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "AI Agent MVP API"}


@app.post("/api/v1/auth/connect-token", response_model=ConnectTokenResponse)
async def create_connect_token():
    """
    Generate a Pipedream Connect token and URL for OAuth flow
    PROVEN PATTERN: Returns connectLinkUrl ready for popup
    """
    try:
        result = await pipedream_client.create_connect_token()
        return ConnectTokenResponse(
            token=result["token"],
            connectLinkUrl=result["connectLinkUrl"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create connect token: {str(e)}")


@app.get("/api/v1/integrations/accounts")
async def list_connected_accounts():
    """
    PROVEN PATTERN: Check what apps user has connected
    Returns list of connected accounts from Pipedream
    """
    try:
        accounts_list = await pipedream_client.list_accounts("user_main")

        # Auto-save any new accounts we find
        local_accounts = load_accounts()

        for account in accounts_list:
            app_slug = account.get("app", {}).get("name_slug")
            account_id = account.get("id")

            if app_slug == "gmail" and not local_accounts.get("gmail_account_id"):
                local_accounts["gmail_account_id"] = account_id
                save_accounts(local_accounts)
            elif app_slug == "hubspot" and not local_accounts.get("hubspot_account_id"):
                local_accounts["hubspot_account_id"] = account_id
                save_accounts(local_accounts)

        return {"accounts": accounts_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list accounts: {str(e)}")


@app.post("/api/v1/integrations/gmail/save", response_model=SaveAccountResponse)
async def save_gmail_account(request: SaveAccountRequest):
    """
    Save Gmail account ID after OAuth completion
    """
    try:
        accounts = load_accounts()
        accounts["gmail_account_id"] = request.account_id
        save_accounts(accounts)
        return SaveAccountResponse(status="saved")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save Gmail account: {str(e)}")


@app.post("/api/v1/integrations/hubspot/save", response_model=SaveAccountResponse)
async def save_hubspot_account(request: SaveAccountRequest):
    """
    Save HubSpot account ID after OAuth completion
    """
    try:
        accounts = load_accounts()
        accounts["hubspot_account_id"] = request.account_id
        save_accounts(accounts)
        return SaveAccountResponse(status="saved")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save HubSpot account: {str(e)}")


@app.post("/api/v1/sync/gmail", response_model=SyncResponse)
async def sync_gmail():
    """
    Sync Gmail emails from last 3 months into knowledge graph
    """
    try:
        accounts = load_accounts()
        gmail_account_id = accounts.get("gmail_account_id")

        if not gmail_account_id:
            raise HTTPException(status_code=400, detail="Gmail not connected")

        synced_count = await sync_gmail_last_3_months(gmail_account_id)

        # Update last sync timestamp
        accounts["last_sync"]["gmail"] = datetime.now().isoformat()
        save_accounts(accounts)

        return SyncResponse(synced=synced_count, status="complete")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/api/v1/sync/hubspot", response_model=SyncResponse)
async def sync_hubspot():
    """
    Sync HubSpot contacts, deals, and companies into knowledge graph
    """
    try:
        accounts = load_accounts()
        hubspot_account_id = accounts.get("hubspot_account_id")

        if not hubspot_account_id:
            raise HTTPException(status_code=400, detail="HubSpot not connected")

        result = await sync_hubspot_all(hubspot_account_id)
        total_synced = result["contacts"] + result["deals"] + result["companies"]

        # Update last sync timestamp
        accounts["last_sync"]["hubspot"] = datetime.now().isoformat()
        save_accounts(accounts)

        return SyncResponse(synced=total_synced, status="complete")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/api/v1/sync/status", response_model=SyncStatusResponse)
async def get_sync_status():
    """
    Get connection and sync status for all integrations
    PROVEN PATTERN: Check Pipedream for connected accounts
    """
    try:
        # Check Pipedream for connected accounts
        accounts_list = await pipedream_client.list_accounts("user_main")

        # Auto-save any new accounts we find
        local_accounts = load_accounts()
        gmail_connected = False
        hubspot_connected = False

        for account in accounts_list:
            app_slug = account.get("app", {}).get("name_slug")
            account_id = account.get("id")

            if app_slug == "gmail":
                gmail_connected = True
                if not local_accounts.get("gmail_account_id"):
                    local_accounts["gmail_account_id"] = account_id
                    save_accounts(local_accounts)
            elif app_slug == "hubspot":
                hubspot_connected = True
                if not local_accounts.get("hubspot_account_id"):
                    local_accounts["hubspot_account_id"] = account_id
                    save_accounts(local_accounts)

        return SyncStatusResponse(
            gmail={
                "connected": gmail_connected,
                "last_sync": local_accounts.get("last_sync", {}).get("gmail")
            },
            hubspot={
                "connected": hubspot_connected,
                "last_sync": local_accounts.get("last_sync", {}).get("hubspot")
            }
        )
    except Exception as e:
        # Fallback to local storage if Pipedream check fails
        accounts = load_accounts()
        return SyncStatusResponse(
            gmail={
                "connected": accounts.get("gmail_account_id") is not None,
                "last_sync": accounts.get("last_sync", {}).get("gmail")
            },
            hubspot={
                "connected": accounts.get("hubspot_account_id") is not None,
                "last_sync": accounts.get("last_sync", {}).get("hubspot")
            }
        )


@app.post("/api/v1/agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AI agent - searches knowledge graph and returns response
    """
    try:
        result = await agent_service.chat(request.message)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/api/v1/ingest")
async def ingest_data(request: IngestRequest):
    """
    MAIN INGESTION ENDPOINT
    Receive data from Pipedream workflows and process into knowledge graph
    """
    try:
        data = request.data
        source = request.source

        # Transform data based on source
        if source == "gmail":
            # Gmail email data
            episode_content = f"""From: {data.get('from', 'Unknown')}
To: {data.get('to', 'Unknown')}
Subject: {data.get('subject', 'No Subject')}
Date: {data.get('date', '')}

{data.get('body', '')}"""

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"Gmail - {data.get('subject', 'Email')}",
                name=f"email_{data.get('id', 'unknown')}",
                reference_time=datetime.fromisoformat(data.get('date', datetime.now().isoformat())),
                uuid=f"gmail_{data.get('id', 'unknown')}"
            )

        elif source == "hubspot_contact":
            # HubSpot contact data
            props = data.get('properties', {})
            episode_content = f"""Contact Information:
Name: {props.get('firstname', '')} {props.get('lastname', '')}
Email: {props.get('email', 'N/A')}
Company: {props.get('company', 'N/A')}
Phone: {props.get('phone', 'N/A')}
Job Title: {props.get('jobtitle', 'N/A')}"""

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"HubSpot Contact - {props.get('email', data.get('id'))}",
                name=f"contact_{data.get('id')}",
                reference_time=datetime.now(),
                uuid=f"hubspot_contact_{data.get('id')}"
            )

        elif source == "hubspot_deal":
            # HubSpot deal data
            props = data.get('properties', {})
            episode_content = f"""Deal Information:
Deal Name: {props.get('dealname', 'Untitled')}
Amount: ${props.get('amount', '0')}
Stage: {props.get('dealstage', 'N/A')}
Close Date: {props.get('closedate', 'N/A')}"""

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"HubSpot Deal - {props.get('dealname', data.get('id'))}",
                name=f"deal_{data.get('id')}",
                reference_time=datetime.now(),
                uuid=f"hubspot_deal_{data.get('id')}"
            )

        return {"status": "success", "message": f"Processed {source} data"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
