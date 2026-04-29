#!/bin/bash

# Phoenix AI SDK Installer Script
# This script automates the setup of a virtual environment and installs all dependencies.

set -e

echo "------------------------------------------------"
echo "🐦🔥  Phoenix AI SDK - Automated Installer"
echo "------------------------------------------------"

# 1. Check Python version
python3 --version || { echo "Error: Python 3 is required."; exit 1; }

# 2. Hardware Pre-Check (Warning Only)
echo "[*] Verifying hardware resources..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM" -lt 8 ]; then
        echo "------------------------------------------------"
        echo "⚠️  WARNING: Low RAM detected (${TOTAL_RAM}GB)"
        echo "Local LLM/VLM models require at least 8GB RAM (16GB+ recommended)."
        echo "The SDK will install, but local execution might be unstable."
        echo "Consider using remote providers (OpenAI/LongCat) instead."
        echo "------------------------------------------------"
        sleep 3
    fi
fi


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

# 6. Install and Start Redis (System Dependency)
echo "[*] Setting up Redis server..."
if ! command -v redis-server &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        echo "[*] Installing redis-server via apt..."
        apt-get update && apt-get install -y redis-server
    elif command -v brew &> /dev/null; then
        echo "[*] Installing redis via brew..."
        brew install redis
    else
        echo "[!] Warning: redis-server not found and no known package manager detected."
    fi
else
    echo "[*] redis-server already installed."
fi

# Ensure Redis is running
if command -v redis-server &> /dev/null; then
    echo "[*] Starting Redis server in daemon mode..."
    redis-server --daemonize yes || echo "[!] Redis might already be running."
    redis-cli ping || echo "[!] Redis-cli ping failed. Check redis status."
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
