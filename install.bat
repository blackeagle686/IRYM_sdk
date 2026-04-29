@echo off
echo 🐦🔥 Initializing Phoenix AI Installation (Windows)...

:: Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo.
echo ⚠️  Note: Redis is required for stateful memory and caching.
echo.
echo On Windows, we recommend one of the following:
echo 1. Install Redis via WSL (Windows Subsystem for Linux).
echo 2. Use Memurai (Redis-compatible for Windows).
echo 3. Use Docker: 'docker run --name phx-redis -p 6379:6379 -d redis'
echo.
echo Once Redis is running, ensure REDIS_URL is set in your .env file.
echo.
echo ✅ Phoenix AI Installation Complete!
pause
