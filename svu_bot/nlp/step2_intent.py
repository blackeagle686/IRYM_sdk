class IntentDetector:
    """Step 2: Handled by Member 2 of the NLP team."""
    @staticmethod
    def process(text: str) -> str:
        text = text.lower()
        if any(w in text for w in ["hello", "hi", "hey"]):
            return "GREETING"
        if any(w in text for w in ["program", "degree", "master", "bait", "bsce"]):
            return "ACADEMIC_QUERY"
        if any(w in text for w in ["help", "support", "contact"]):
            return "SUPPORT_REQUEST"
        return "GENERAL_INQUIRY"
