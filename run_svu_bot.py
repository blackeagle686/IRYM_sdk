import asyncio
from svu_bot.backend import start_backend

if __name__ == "__main__":
    print("Launching SVU Bot Team Environment...")
    print("- NLP Pipeline: Ready (5 Steps)")
    print("- Backend: FastAPI (uvicorn)")
    print("- Frontend: Static Web (v0.1)")
    print("- Audit Logging: Enabled (svu_bot/data/audit_logs.jsonl)")
    
    start_backend()
