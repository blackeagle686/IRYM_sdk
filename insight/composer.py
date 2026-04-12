class PromptComposer:
    """Builds structured prompts systematically."""
    def build_prompt(self, question: str, docs: list) -> str:
        context = "\n".join([str(d) for d in docs])
        return f"""You are an AI assistant with access to context.

Context:
{context}

Question:
{question}

Answer in a precise and helpful way.
"""
