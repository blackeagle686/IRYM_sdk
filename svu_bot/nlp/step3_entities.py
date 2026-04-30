from typing import List

"""
SVU BOT - NLP PIPELINE STEP 3: ENTITY EXTRACTOR
===============================================
Purpose:
    This module performs "Named Entity Recognition" (NER) focused on SVU's domain.
    It extracts specific, actionable nouns (like program names) to aid in search.

Responsibilities (Member 3):
    1. Scan text for SVU Academic Program codes (BAIT, BSCE, etc.).
    2. Maintain the list of valid programs for recognition.
    3. Provide the orchestrator with a list of found tags for targeted RAG retrieval.

Returns:
    A list of strings representing found entities (e.g., ["BAIT", "BSCE"]).
"""

class EntityExtractor:
    """Handled by Member 3 of the NLP team."""
    @staticmethod
    def process(text: str) -> List[str]:
        entities = []
        programs = ["BAIT", "BSCE", "MIQ", "MWT", "TIC", "BIT"]
        for prog in programs:
            if prog.lower() in text.lower():
                entities.append(prog)
        return entities
