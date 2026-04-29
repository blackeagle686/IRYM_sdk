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

    async def consolidate(self, llm) -> None:
        """Consolidates multiple reflections into a single, concise 'Lessons Learned' summary."""
        if len(self.reflections) < 3:
            return

        reflections_text = "\n".join([f"- {r}" for r in self.reflections])
        prompt = (
            "You are the 'Reflection Manager'. Consolidate the following list of lessons learned "
            "into a concise, bulleted list of high-level insights. Remove redundancies and focus on "
            "actionable takeaways.\n\n"
            f"Current Reflections:\n{reflections_text}\n\n"
            "Consolidated Insights (bullets only):"
        )
        
        consolidated = await llm.generate(prompt, session_id=None)
        self.reflections = [consolidated.strip()]

    def clear(self):
        self.reflections.clear()
