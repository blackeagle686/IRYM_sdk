import re

"""
SVU BOT - NLP PIPELINE STEP 1: TEXT CLEANER
===========================================
Purpose:
    This module is the first gate for user input. It focuses on "Input Hygiene" by
    removing noise, technical artifacts (HTML/URLs), and normalizing the text structure.

Responsibilities (Member 1):
    1. Strip leading/trailing whitespace and normalize internal spacing.
    2. Remove HTML tags to prevent cross-site scripting (XSS) and data noise.
    3. Remove URLs to keep the LLM focused on conversational text.
    4. Normalize punctuation to prevent emotional "spam" (e.g., redundant exclamation marks).
    5. Filter out non-standard special characters that might confuse the tokenizer.

Returns:
    A cleaned, standardized string ready for intent analysis.
"""

class TextCleaner:
    """Handled by Member 1 of the NLP team. Focused on input hygiene."""
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
