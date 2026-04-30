import re

class TextCleaner:
    """Step 1: Handled by Member 1 of the NLP team."""
    @staticmethod
    def process(text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
