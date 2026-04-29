#!/bin/bash
echo "🐦🔥 Initializing Phoenix AI Installation..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# System Dependencies (Redis)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔍 Checking for Redis..."
    if ! command -v redis-server &> /dev/null; then
        echo "📥 Installing Redis Server..."
        sudo apt update && sudo apt install redis-server -y
    fi
    
    echo "⚙️ Starting Redis in daemon mode..."
    sudo redis-server --daemonize yes
    
    # Verify Redis is running
    REDIS_STATUS=$(redis-cli ping)
    if [ "$REDIS_STATUS" == "PONG" ]; then
        echo "✅ Redis is active (PONG)."
    else
        echo "⚠️ Redis installation finished but server failed to start. Please check logs."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🔍 Checking for Redis (macOS)..."
    if ! command -v redis-server &> /dev/null; then
        echo "📥 Installing Redis via Homebrew..."
        brew install redis
    fi
    echo "⚙️ Starting Redis service..."
    brew services start redis
fi

echo "✅ Phoenix AI Installation Complete!"
