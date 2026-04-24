from IRYM_sdk.core.config import config

class VectorRetriever:
    """Handles vector DB abstractions for the Insight layer."""
    def __init__(self, vector_db):
        self.vector_db = vector_db

    async def retrieve(self, question: str):
        # 1. Search for small chunks (children)
        # If Parent Retrieval is enabled, we filter to is_parent=False
        where = {"is_parent": False} if config.RAG_PARENT_RETRIEVAL else None
        children = await self.vector_db.search(question, where=where)
        
        if not config.RAG_PARENT_RETRIEVAL or not children:
            return children
            
        # 2. Map children to parents
        parent_ids = list(set([c["metadata"].get("parent_id") for c in children if c["metadata"].get("parent_id")]))
        
        if not parent_ids:
            return children
            
        # 3. Retrieve unique parents
        # Chroma supports $in operator
        parents = await self.vector_db.get_by_metadata(where={"doc_id": {"$in": parent_ids}})
        return parents
