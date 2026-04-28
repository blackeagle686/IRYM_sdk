from typing import List

class ReflectionMemory:
    """Stores lessons learned and past mistakes/successes to improve future planning."""
    def __init__(self):
        self.reflections: List[str] = []

    def add_reflection(self, reflection: str):
        self.reflections.append(reflection)

    def get_reflections(self) -> str:
        if not self.reflections:
            return ""
        return "Lessons Learned:\n" + "\n".join([f"- {r}" for r in self.reflections])

    def clear(self):
        self.reflections.clear()
