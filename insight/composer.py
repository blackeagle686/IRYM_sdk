class PromptComposer:
    """Builds structured prompts systematically."""
    def build_prompt(self, question: str, docs: list) -> str:
        formatted_docs = []
        for i, doc in enumerate(docs):
            content = doc.get("content", str(doc)) if isinstance(doc, dict) else str(doc)
            source = doc.get("metadata", {}).get("source", "Unknown") if isinstance(doc, dict) else "Unknown"
            formatted_docs.append(f"[Document {i+1}] (Source: {source})\n{content}")
            
        context = "\n\n".join(formatted_docs)
        
        return f"""You are an AI assistant with access to context from multiple resources.
Your task is to answer the question using the provided context.
IMPORTANT: Always cite your sources in your answer using [Source: file_name] or [Source: URL].

Context:
{context}

Question:
{question}

Answer in a precise and helpful way, including citations.
"""
