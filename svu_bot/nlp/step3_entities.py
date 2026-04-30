from typing import List

class EntityExtractor:
    """Step 3: Handled by Member 3 of the NLP team."""
    @staticmethod
    def process(text: str) -> List[str]:
        entities = []
        programs = ["BAIT", "BSCE", "MIQ", "MWT", "TIC", "BIT"]
        for prog in programs:
            if prog.lower() in text.lower():
                entities.append(prog)
        return entities
