"""
Chat API router that proxies to ADK Agent endpoints.

This router creates sessions and proxies chat requests to the
ADK's native /run_sse endpoint which properly invokes the agent.
"""

import asyncio
import json
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

router = APIRouter()

# ADK backend URL (same server)
ADK_BASE_URL = "http://localhost:8080"

# Track created sessions
created_sessions = set()


# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class StreamChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    app_name: str = "techai_agent"


# ============ Helper Functions ============

async def ensure_adk_session(user_id: str, session_id: str, app_name: str = "techai_agent"):
    """Create a session in ADK if it doesn't exist."""
    session_key = f"{app_name}:{user_id}:{session_id}"
    if session_key in created_sessions:
        return True
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{ADK_BASE_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
            response = await client.post(url, json={})
            if response.status_code in [200, 201, 409]:  # 409 = already exists
                created_sessions.add(session_key)
                return True
            else:
                print(f"Session creation: {response.status_code}")
                return False
    except Exception as e:
        print(f"Session error: {e}")
        return False


async def call_adk_run_sse(message: str, user_id: str, session_id: str, app_name: str = "techai_agent"):
    """Call ADK's /run_sse endpoint and yield response chunks."""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{ADK_BASE_URL}/run_sse"
            payload = {
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": message}]
                }
            }
            
            async with client.stream("POST", url, json=payload, timeout=120.0) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield line[6:]
                        
    except Exception as e:
        print(f"ADK call error: {e}")
        yield json.dumps({"error": str(e)})


# ============ Endpoints ============

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response."""
    session_id = request.session_id or str(uuid.uuid4())
    user_id = "default_user"
    
    await ensure_adk_session(user_id, session_id)
    
    try:
        full_response = ""
        
        async for chunk in call_adk_run_sse(request.message, user_id, session_id):
            try:
                data = json.loads(chunk)
                if "content" in data and "parts" in data["content"]:
                    for part in data["content"]["parts"]:
                        if "text" in part:
                            full_response += part["text"]
            except json.JSONDecodeError:
                continue
        
        return ChatResponse(
            response=full_response or "I'm here to help! What would you like to know?",
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: StreamChatRequest):
    """Stream chat response using Server-Sent Events (SSE)."""
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "guest"
    
    async def generate():
        session_created = await ensure_adk_session(user_id, session_id, request.app_name)
        
        if not session_created:
            yield f"data: {json.dumps({'content': 'Connecting to AI...', 'done': False})}\n\n"
        
        try:
            collected_text = ""
            
            async for chunk in call_adk_run_sse(request.message, user_id, session_id, request.app_name):
                try:
                    data = json.loads(chunk)
                    
                    if "content" in data and "parts" in data["content"]:
                        for part in data["content"]["parts"]:
                            if "text" in part:
                                text = part["text"]
                                collected_text += text
                                yield f"data: {json.dumps({'content': text, 'done': False})}\n\n"
                                await asyncio.sleep(0.01)
                                
                except json.JSONDecodeError:
                    continue
            
            if not collected_text:
                fallback = "I'm here to help! What would you like to know about our products?"
                yield f"data: {json.dumps({'content': fallback, 'done': False})}\n\n"
            
            yield f"data: {json.dumps({'content': '', 'done': True, 'session_id': session_id})}\n\n"
            
        except Exception as e:
            print(f"Stream error: {e}")
            yield f"data: {json.dumps({'content': 'Sorry, please try again.', 'done': False})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session."""
    to_remove = [k for k in created_sessions if session_id in k]
    for key in to_remove:
        created_sessions.discard(key)
    return {"message": "Session cleared", "session_id": session_id}


@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    return {
        "status": "healthy",
        "service": "chat",
        "adk_backend": ADK_BASE_URL,
        "active_sessions": len(created_sessions)
    }
