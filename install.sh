#!/bin/bash

# Phoenix AI SDK Installer Script
# This script automates the setup of a virtual environment and installs all dependencies.

set -e

echo "------------------------------------------------"
echo "🧠 Phoenix AI SDK - Automated Installer"
echo "------------------------------------------------"

# 1. Check Python version
python3 --version || { echo "Error: Python 3 is required."; exit 1; }

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "[*] Virtual environment already exists."
fi

# 3. Activate venv
echo "[*] Activating virtual environment..."
source venv/bin/activate

# 4. Upgrade pip
echo "[*] Upgrading pip..."
pip install --upgrade pip

# 5. Install SDK with all extras
echo "[*] Installing Phoenix AI SDK with full dependencies..."
pip install -e ".[full]"

# 6. Check for Redis (System Dependency)
if ! command -v redis-server &> /dev/null; then
    echo "[!] Warning: redis-server not found. Redis is required for persistent history/caching."
    echo "    On Ubuntu/Debian: sudo apt install redis-server"
    echo "    On macOS: brew install redis"
fi

# 7. Initialize .env if missing
if [ ! -f .env ]; then
    echo "[*] Initializing .env configuration..."
    echo "OPENAI_API_KEY=" > .env
    echo "VECTOR_DB_TYPE=chroma" >> .env
    echo "CHROMA_PERSIST_DIR=./chroma_db" >> .env
    echo "REDIS_URL=redis://localhost:6379/0" >> .env
    echo ".env created. Please add your credentials."
fi

echo "------------------------------------------------"
echo "✅ Installation Complete!"
echo "To start using the SDK:"
echo "1. source venv/bin/activate"
echo "2. Edit your .env file"
echo "3. Run 'python3 verify_memory.py' to test."
echo "------------------------------------------------"
