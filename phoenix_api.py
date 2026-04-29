from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import os
import shutil
from phoenix import ChatBot, init_phoenix_full

app = FastAPI(title="Phoenix AI API", version="1.0.0")

# Enable CORS for Flutter, .NET, and Web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global ChatBot instance
bot = None

@app.on_event("startup")
async def startup_event():
    global bot
    print("🐦‍🔥 Initializing Phoenix AI Services...")
    await init_phoenix_full()
    
    # Initialize the high-level ChatBot
    bot = (ChatBot(local=False, vlm=True) # local=False assumes OpenAI by default
           .with_memory()
           .build())
    print("🐦‍🔥 Phoenix AI API is ready.")

@app.post("/chat")
async def chat(
    prompt: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    """
    Unified /chat endpoint for Text, Vision, and Audio interactions.
    Compatible with Flutter, .NET, and any HTTP client.
    """
    try:
        image_path = None
        audio_path = None
        
        # Handle Image Upload
        if image:
            os.makedirs("./temp_uploads", exist_ok=True)
            image_path = f"./temp_uploads/{image.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        
        # Handle Audio Upload
        if audio:
            os.makedirs("./temp_uploads", exist_ok=True)
            audio_path = f"./temp_uploads/{audio.filename}"
            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)

        # Set session if provided
        if session_id:
            bot.set_session(session_id)
            
        # Execute chat
        response = await bot.chat(
            prompt=prompt,
            image_path=image_path,
            audio_path=audio_path
        )
        
        # Cleanup temp files
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            
        return {
            "status": "success",
            "reply": response,
            "session_id": session_id or "new_session"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "alive", "service": "Phoenix AI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
