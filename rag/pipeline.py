import os
from typing import List, Optional
from IRYM_sdk.insight.engine import InsightEngine

class RAGPipeline:
    def __init__(self, vector_db, primary, fallback=None, cache=None):
        self.vector_db = vector_db
        self.primary = primary
        self.fallback = fallback or primary
        self.engine = InsightEngine(vector_db, self.primary, self.fallback, cache)

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
                    if file.endswith((".txt", ".md", ".pdf", ".docx", ".csv", ".json")):
                        documents.append(os.path.join(root, file))

        all_chunks = []
        all_metadatas = []

        for doc_path in documents:
            print(f"[*] Reading {doc_path}...")
            content = self._read_file(doc_path)
            if not content:
                print(f"[!] Warning: No content extracted from {doc_path}")
                continue
                
            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
            print(f"[+] Split into {len(chunks)} chunks.")
            all_chunks.extend(chunks)
            all_metadatas.extend([{"source": os.path.basename(doc_path)} for _ in chunks])

        if all_chunks:
            print(f"[*] Indexing {len(all_chunks)} chunks into Vector DB (this may take a moment)...")
            await self.vector_db.add(texts=all_chunks, metadatas=all_metadatas)
            print("[+] Indexing complete.")

    async def ingest_url(self, url: str, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        """
        Scrapes a URL, chunks the content, and stores in vector DB.
        """
        print(f"[*] Scraping URL: {url}...")
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            content = soup.get_text(separator=' ')
            content = " ".join(content.split())
            
            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
            print(f"[+] Scraped and split into {len(chunks)} chunks.")
            
            if chunks:
                await self.vector_db.add(
                    texts=chunks, 
                    metadatas=[{"source": url} for _ in chunks]
                )
                print(f"[+] Indexed {url} successfully.")
        except Exception as e:
            print(f"[!] Error scraping {url}: {e}")

    async def ingest_sql(self, connection_string: str, query: str, text_column: str, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        """
        Ingests data from a SQL database.
        """
        print(f"[*] Ingesting from SQL: {connection_string}...")
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.mappings().all()
            
            all_chunks = []
            all_metadatas = []
            
            for row in rows:
                content = str(row.get(text_column, ""))
                if not content: continue
                
                chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                all_chunks.extend(chunks)
                metadata = {k: v for k, v in row.items() if k != text_column}
                metadata["source"] = "sql_query"
                all_metadatas.extend([metadata for _ in chunks])
            
            if all_chunks:
                await self.vector_db.add(texts=all_chunks, metadatas=all_metadatas)
                print(f"[+] Indexed {len(rows)} SQL rows successfully.")
        except Exception as e:
            print(f"[!] SQL Ingestion Error: {e}")

    async def ingest_api(self, url: str, method: str = "GET", headers: dict = None, data_path: str = None, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        """
        Ingests data from an external JSON API.
        """
        print(f"[*] Ingesting from API: {url}...")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    resp = await client.get(url, headers=headers)
                else:
                    resp = await client.post(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            # If a data_path is provided (e.g., "results.items"), drill down
            items = data
            if data_path:
                for part in data_path.split('.'):
                    items = items.get(part, [])
            
            if not isinstance(items, list):
                items = [items]

            all_chunks = []
            all_metadatas = []
            for item in items:
                content = str(item) # Simplified: index the whole item as string if not specified better
                chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                all_chunks.extend(chunks)
                all_metadatas.extend([{"source": url} for _ in chunks])

            if all_chunks:
                await self.vector_db.add(texts=all_chunks, metadatas=all_metadatas)
                print(f"[+] Indexed API response successfully.")
        except Exception as e:
            print(f"[!] API Ingestion Error: {e}")

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
        
        elif path.endswith(".docx"):
            try:
                import docx
                doc = docx.Document(path)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                print(f"[!] Warning: python-docx not installed. Cannot read DOCX: {path}")
                return ""
        
        elif path.endswith((".xlsx", ".xls")):
            try:
                import pandas as pd
                df = pd.read_excel(path)
                return df.to_string()
            except ImportError:
                print(f"[!] Warning: pandas/openpyxl not installed. Cannot read Excel: {path}")
                return ""
            except Exception as e:
                print(f"[!] Error reading Excel {path}: {e}")
                return ""

        elif path.endswith(".csv"):
            try:
                import csv
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    return "\n".join([",".join(row) for row in reader])
            except Exception as e:
                print(f"[!] Error reading CSV {path}: {e}")
                return ""
        
        elif path.endswith(".json"):
            try:
                import json
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            except Exception as e:
                print(f"[!] Error reading JSON {path}: {e}")
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
