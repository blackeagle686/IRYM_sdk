import json
from datetime import datetime

"""
SVU BOT - NLP PIPELINE STEP 5: INTERACTION AUDITOR
=================================================
Purpose:
    This module handles persistent logging for the 8-member team to review.
    It captures the "context" of the conversation to allow for future tuning.

Responsibilities (Member 5):
    1. Log the exact prompt used (after cleaning).
    2. Log the detected intent to verify classifier accuracy.
    3. Save a preview of the response to monitor quality.
    4. Store timestamps and session IDs for analytical tracking.

Storage:
    Appends to 'svu_bot/data/audit_logs.jsonl' in JSON Lines format.
"""

class InteractionAuditor:
    """Handled by Member 5 of the NLP team."""
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
