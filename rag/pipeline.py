class RAGPipeline:
    def __init__(self, vector_db, llm):
        self.vector_db = vector_db
        self.llm = llm

    async def query(self, question: str) -> str:
        docs = await self.vector_db.search(question)
        return await self.llm.generate(str(docs) + question)
