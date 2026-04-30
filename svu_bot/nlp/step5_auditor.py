import json
from datetime import datetime

class InteractionAuditor:
    """Step 5: Handled by Member 5 of the NLP team."""
    @staticmethod
    def process(session_id: str, prompt: str, response: str, intent: str):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "prompt": prompt,
            "intent": intent,
            "response_preview": response[:50] + "...",
            "audited": False
        }
        try:
            with open("svu_bot/data/audit_logs.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Logging error: {e}")
