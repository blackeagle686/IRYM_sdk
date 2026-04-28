import os
import time
import subprocess
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Configuration
DEFAULT_API_KEY = "ak_2yp3Xw1Ny7ky2pF7er9x93ZO9jj6G"
BASE_URL = "https://api.longcat.chat/openai"
INTERVAL = 10  # Seconds

load_dotenv()

api_key = os.getenv("LONGCAT_API_KEY", DEFAULT_API_KEY)
client = OpenAI(api_key=api_key, base_url=BASE_URL, timeout=20.0)

def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e.stderr}")
        return None

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
            model="LongCat-Flash-Chat",
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
