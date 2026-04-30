import re

class TextCleaner:
    """Step 1: Handled by Member 1 of the NLP team. Focused on input hygiene."""
    @staticmethod
    def process(text: str) -> str:
        # 1. Strip and normalize whitespace
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        # 2. Remove HTML tags (security and noise reduction)
        text = re.sub(r'<[^>]*>', '', text)
        
        # 3. Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 4. Normalize punctuation (remove duplicate symbols)
        text = re.sub(r'([!?.])\1+', r'\1', text)
        
        # 5. Remove special characters (keep letters, numbers, and basic punctuation)
        text = re.sub(r'[^a-zA-Z0-9\s!?.@#$%-]', '', text)
        
        return text
