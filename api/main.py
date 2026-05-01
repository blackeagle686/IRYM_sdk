import os
import shutil
import tempfile
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from phoenix import ChatBot, Agent, init_phoenix_full
from phoenix.services.observability.logger import get_logger

logger = get_logger("Phoenix AI.API")

# --- Global State ---
# In a real production app, you might use a dependency injection system 
# or a pool of workers. For this SDK exposure, we'll use singletons.
class AIState:
    def __init__(self):
        self.bot = None
        self.agent = None

state = AIState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the SDK
    logger.info("Initializing Phoenix AI SDK for API...")
    
    # 1. Initialize ChatBot (Local or OpenAI based on env)
    state.bot = (ChatBot(local=False) # Default to remote for API stability
                .with_memory()
                .with_rag("./data") # Pre-point to a data folder
                .build())
    
    # 2. Initialize Agent
    state.agent = Agent()
    
    logger.info("Phoenix AI Services ready.")
    yield
    # Shutdown logic if needed
    logger.info("Shutting down API...")

app = FastAPI(
    title="Phoenix AI Service API",
    description="HTTP Interface for Phoenix AI ChatBot and Autonomous Agent",
    version="0.2.1",
    lifespan=lifespan
)

# Enable CORS for cross-framework compatibility (Flutter, Node.js, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---

class ChatResponse(BaseModel):
    response: str
    session_id: str
    source: str = "chatbot"

class AgentRequest(BaseModel):
    prompt: str
    mode: str = "auto" # auto, plan, fast_ans
    session_id: str = "default_session"

class AgentResponse(BaseModel):
    result: str
    mode: str
    session_id: str
    source: str = "agent"

# --- Endpoints ---

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    text: str = Form(...),
    session_id: str = Form("default_session"),
    image: Optional[UploadFile] = File(None)
):
    """
    Interact with the ChatBot.
    Supports multi-modal input (text + optional image).
    """
    try:
        temp_image_path = None
        if image:
            # Save uploaded image to a temporary file
            suffix = os.path.splitext(image.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(image.file, tmp)
                temp_image_path = tmp.name

        # Set session and execute chat
        response = await state.bot.set_session(session_id).chat(
            text=text, 
            image_path=temp_image_path
        )

        # Cleanup temp file
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        return ChatResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Interact with the Autonomous Agent.
    Supports 'auto', 'plan', and 'fast_ans' modes.
    """
    try:
        # Run the agent with the specified mode
        result = await state.agent.run(
            prompt=request.prompt,
            mode=request.mode
            # Note: Session handling in Agent can be expanded here
        )

        return AgentResponse(
            result=result,
            mode=request.mode,
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Agent Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.2.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
