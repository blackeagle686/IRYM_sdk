import os
from typing import List, Optional
from IRYM_sdk.insight.engine import InsightEngine

class RAGPipeline:
    def __init__(self, vector_db, llm, cache=None):
        self.vector_db = vector_db
        self.llm = llm
        self.engine = InsightEngine(vector_db, llm, cache)

    async def ingest(self, path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        """
        Loads documents from path, chunks them, and stores in vector DB.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist.")

        documents = []
        if os.path.isfile(path):
            documents.append(path)
        else:
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith((".txt", ".md", ".pdf")):
                        documents.append(os.path.join(root, file))

        all_chunks = []
        all_metadatas = []

        for doc_path in documents:
            content = self._read_file(doc_path)
            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
            all_chunks.extend(chunks)
            all_metadatas.extend([{"source": doc_path} for _ in chunks])

        if all_chunks:
            await self.vector_db.add(texts=all_chunks, metadatas=all_metadatas)

    def _read_file(self, path: str) -> str:
        if path.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                print(f"[!] Warning: pypdf not installed. Cannot read PDF: {path}")
                return ""
            except Exception as e:
                print(f"[!] Error reading PDF {path}: {e}")
                return ""
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _chunk_text(self, text: str, size: int, overlap: int) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start = end - overlap
            if start >= len(text) - overlap:
                break
        return chunks

    async def query(self, question: str) -> str:
        """
        Queries the RAG pipeline using the InsightEngine.
        """
        return await self.engine.query(question)

    async def clear_data(self) -> None:
        """Clears all data from the vector database."""
        await self.vector_db.clear()
