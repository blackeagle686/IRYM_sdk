import os
import subprocess
import time
import sys

def install_dependencies():
    print("Installing required dependencies...")
    # Install Redis server for caching
    subprocess.check_call(["apt-get", "update"])
    subprocess.check_call(["apt-get", "install", "-y", "redis-server"])
    subprocess.check_call(["service", "redis-server", "start"])
    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "uvicorn", "fastapi", "python-multipart", "redis"])

def setup_ngrok(auth_token):
    from pyngrok import ngrok
    print("Setting up ngrok tunnel...")
    ngrok.set_auth_token(auth_token)
    public_url = ngrok.connect(8000).public_url
    print(f"\n{'='*50}")
    print(f"SVU Bot is now LIVE at: {public_url}")
    print(f"{'='*50}\n")
    return public_url

def run_server():
    print("Starting FastAPI server...")
    # Using subprocess to run the main bot script in the background or backgrounded thread
    # In Colab, we usually run this in a separate cell, but here we can use uvicorn directly
    import uvicorn
    from svu_bot.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    NGROK_TOKEN = "36jW6kAV8Inp5SHYiuIicuuRols_7NkiWdLme3iULLJx3gMS5"
    
    try:
        install_dependencies()
        public_url = setup_ngrok(NGROK_TOKEN)
        run_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
