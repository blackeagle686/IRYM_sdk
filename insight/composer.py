class PromptComposer:
    """Builds structured prompts systematically."""
    def build_prompt(self, question: str, docs: list) -> str:
        formatted_docs = []
        for i, doc in enumerate(docs):
            content = doc.get("content", str(doc)) if isinstance(doc, dict) else str(doc)
            source = doc.get("metadata", {}).get("source", "Unknown") if isinstance(doc, dict) else "Unknown"
            formatted_docs.append(f"[Document {i+1}] (Source: {source})\n{content}")
            
        context = "\n\n".join(formatted_docs)
        
        return f"""You are an Expert Real Estate AI Assistant. Your goal is to provide highly accurate, professional, and helpful answers based ONLY on the provided context.

### GUIDELINES:
1. **Accuracy**: Only use the information provided in the context. Do not use outside knowledge.
2. **Citations**: ALWAYS cite the source for every claim you make. Use the format: [Source: source_name].
3. **Uncertainty**: If the answer is not in the context, explicitly state: "I'm sorry, but I couldn't find information about that in my current knowledge base." Do not hallucinate.
4. **Formatting**: Use clear, concise language and bullet points if appropriate.

### CONTEXT:
{context}

### USER QUESTION:
{question}

### YOUR PRECISE ANSWER:
"""
