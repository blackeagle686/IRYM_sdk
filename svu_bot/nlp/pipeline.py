import re
import json
from datetime import datetime
from typing import List, Dict, Any

class SVUNLPProcessor:
    """
    Dedicated NLP Pipeline for SVU Bot Team Collaboration.
    Includes 5 modular steps for processing user input and agent output.
    """

    # Step 1: Text Cleaning
    @staticmethod
    def clean_text(text: str) -> str:
        """Removes extra whitespace, special characters, and normalizes text."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        # Add SVU specific cleaning logic here (e.g. normalizing program codes)
        return text

    # Step 2: Intent Classification (Lightweight)
    @staticmethod
    def detect_intent(text: str) -> str:
        """Determines the primary goal of the user query."""
        text = text.lower()
        if any(w in text for w in ["hello", "hi", "hey"]):
            return "GREETING"
        if any(w in text for w in ["program", "degree", "master", "bait", "bsce"]):
            return "ACADEMIC_QUERY"
        if any(w in text for w in ["help", "support", "contact"]):
            return "SUPPORT_REQUEST"
        return "GENERAL_INQUIRY"

    # Step 3: Entity Extraction
    @staticmethod
    def extract_entities(text: str) -> List[str]:
        """Extracts SVU-specific entities like program names or administrative keywords."""
        entities = []
        programs = ["BAIT", "BSCE", "MIQ", "MWT", "TIC", "BIT"]
        for prog in programs:
            if prog.lower() in text.lower():
                entities.append(prog)
        return entities

    # Step 4: Output Adaptation
    @staticmethod
    def adapt_output(llm_output: str) -> str:
        """Formats and enriches the LLM response for the SVU context."""
        # Add helpful links or standard SVU footers
        if "program" in llm_output.lower():
            llm_output += "\n\n[Official Link]: https://www.svuonline.org/en/programs"
        return llm_output

    # Step 5: Team Audit Logging
    @staticmethod
    def log_interaction(session_id: str, prompt: str, response: str, intent: str):
        """Saves interaction data for the 8-member team to review/audit."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "prompt": prompt,
            "intent": intent,
            "response_preview": response[:50] + "...",
            "audited": False
        }
        # Append to a local file for team collaboration
        try:
            with open("svu_bot/data/audit_logs.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def process_input(self, text: str) -> Dict[str, Any]:
        """Runs the inbound pipeline."""
        cleaned = self.clean_text(text)
        return {
            "text": cleaned,
            "intent": self.detect_intent(cleaned),
            "entities": self.extract_entities(cleaned)
        }
