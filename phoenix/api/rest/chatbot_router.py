
"""
Ready-to-use FastAPI router for Phoenix ChatBot.
Mount this in any FastAPI app with: app.include_router(chatbot_router)
"""
try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
except ImportError:
    raise ImportError("Install fastapi and pydantic: pip install fastapi pydantic")

router = APIRouter(prefix="/chat", tags=["ChatBot"])

class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str

_bot_instance = None

def init_router(bot_instance):
    """Call this with your ChatBotInstance before mounting."""
    global _bot_instance
    _bot_instance = bot_instance

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not _bot_instance:
        raise HTTPException(status_code=503, detail="ChatBot not initialized. Call init_router() first.")
    _bot_instance.set_session(req.session_id)
    reply = await _bot_instance.chat(text=req.message)
    return ChatResponse(session_id=req.session_id, reply=reply)
