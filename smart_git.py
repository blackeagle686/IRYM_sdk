import os
import time
import subprocess
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Configuration
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o")
INTERVAL = 5  # Seconds

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=20.0)

def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        # Use UTF-8 with replacement to avoid UnicodeDecodeError on Windows/different locales
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            encoding='utf-8', 
            errors='replace'
        )
        return (result.stdout or "").strip()
    except Exception as e:
        stderr = getattr(e, 'stderr', str(e))
        print(f"Error running command {' '.join(command)}: {stderr}")
        return "" # Return empty string to prevent .strip() crashes in callers
    

def get_current_branch():
    return run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])

def has_changes():
    status = run_command(["git", "status", "--porcelain"])
    return bool(status)

def get_diff():
    # We use --cached because we run 'git add .' before this
    return run_command(["git", "diff", "--cached"])
# fix the long cat model
def generate_commit_message(diff):
    if not diff:
        return None
    
    try:
        # Optimized for speed: Short system prompt, truncated diff, low max_tokens, temperature 0
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Write a concise Git commit message. 1st line < 50 chars. Use bullets if needed."},
                {"role": "user", "content": f"Diff:\n{diff[:3000]}"}
            ],
            max_tokens=100,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def smart_sync():
    print(f"[*] Checking for changes at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    
    if not has_changes():
        print("[ ] No changes detected.")
        return

    print("[+] Changes detected. Staging files...")
    run_command(["git", "add", "."])
    
    diff = get_diff()
    print("[*] Generating commit message...")
    message = generate_commit_message(diff)
    
    if not message:
        message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"[!] LLM failed or no message generated. Using fallback: {message}")
    else:
        print(f"[v] Generated message: {message.splitlines()[0]}")

    print("[*] Committing...")
    run_command(["git", "commit", "-m", message])
    
    branch = get_current_branch()
    if branch:
        print(f"[*] Pushing to origin {branch}...")
        run_command(["git", "push", "origin", branch])
        print("[v] Done.")
    else:
        print("[!] Could not determine current branch. Skipping push.")

def main():
    print("=== Smart Git Automator Started ===")
    print(f"Interval: {INTERVAL} seconds")
    print(f"Target: {os.getcwd()}")
    
    # Check if this is a git repo
    if not os.path.exists(".git"):
        print("[!] Error: Not a Git repository. Please run in a git project root.")
        return

    try:
        while True:
            smart_sync()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")

if __name__ == "__main__":
    main()
