from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from svu_bot.bot import SVUBot
from contextlib import asynccontextmanager

# Global bot instance
bot = SVUBot()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # The framework handles initialization lazily, 
    # but we can optionally pre-prime it here if desired.
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="svu_bot/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("svu_bot/static/index.html")

@app.post("/chat")
async def chat_endpoint(
    message: str = Body(..., embed=True),
    session_id: str = Body("web_session", embed=True)
):
    """API endpoint to chat with SVU Bot."""
    response = await bot.chat(message, session_id=session_id)
    return {"reply": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
