from typing import List, Dict, Any

class ShortTermMemory:
    """Manages immediate context window memory."""
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> str:
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.messages])

    def clear(self):
        self.messages.clear()
