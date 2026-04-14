class Optimizer:
    """Handles query manipulation, semantic cache hits, and reranking (future)."""
    
    def rerank(self, docs, query: str):
        # Placeholder for future reranking logic
        # For now, we just ensure they are sorted by distance if present
        if docs and isinstance(docs[0], dict) and "distance" in docs[0]:
            return sorted(docs, key=lambda x: x.get("distance", 0))
        return docs

    def rewrite_query(self, query: str) -> str:
        # Basic query cleaning
        if not query:
            return ""
        
        # Strip whitespace and normalize
        query = query.strip()
        
        # Lowercase for better cache hits
        # (Optional: can be made configurable)
        query = query.lower()
        
        return query
