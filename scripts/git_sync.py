import os
import time
import subprocess

def git_sync():
    print("[*] Starting Git Auto-Sync (Every 10 seconds)...")
    while True:
        try:
            # Check for changes
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
            
            if status:
                print(f"[*] Changes detected. Syncing...")
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Auto-sync update from assistant"], check=True)
                
                # Try master then main
                result = subprocess.run(["git", "push", "origin", "master"], capture_output=True, text=True)
                if result.returncode != 0:
                    print("[!] Push to master failed, trying main...")
                    subprocess.run(["git", "push", "origin", "main"], check=True)
                
                print("[+] Sync complete.")
            else:
                # No changes, just sleep
                pass
                
        except Exception as e:
            print(f"[!] Git Sync Error: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    git_sync()
