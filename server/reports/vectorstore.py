import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document 

from ..config.db import reports_collection
from typing import List
from fastapi import UploadFile

# OCR Imports 
import pytesseract
from pdf2image import convert_from_path

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medragnosis-index")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_reports")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(name=PINECONE_INDEX_NAME, dimension=1536, metric="dotproduct", spec=spec)
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)

def extract_text_with_ocr(pdf_path: str) -> List[Document]:
    """Fallback function to extract text from scanned PDFs using OCR."""
    images = convert_from_path(pdf_path)
    docs = []
    
    for i, image in enumerate(images):
        page_content = pytesseract.image_to_string(image)
        if page_content.strip():
            docs.append(Document(
                page_content=page_content,
                metadata={"page": i + 1, "source": Path(pdf_path).name}
            ))
    return docs

async def load_vectorstore(uploaded_files: List[UploadFile], uploaded: str, doc_id: str):
    embed_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

    for file in uploaded_files:
        filename = Path(file.filename).name
        save_path = Path(UPLOAD_DIR) / f"{doc_id}_{filename}"
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        # 1. Try standard text extraction
        try:
            loader = PyPDFLoader(str(save_path))
            documents = loader.load()
        except Exception as e:
            print(f"Standard load failed for {filename}: {e}")
            documents = []

        # 2. Check if text extraction worked; if not, use OCR
        total_text_length = sum(len(doc.page_content.strip()) for doc in documents)
        
        if total_text_length < 50:
            print(f"Detected scanned PDF for {filename}. Switching to OCR...")
            try:
                documents = await asyncio.to_thread(extract_text_with_ocr, str(save_path))
            except Exception as e:
                print(f"OCR failed for {filename}: {e}")
                continue

        if not documents:
            continue

        # 3. Chunk and Embed
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        if not chunks:
            continue

        texts = [chunk.page_content for chunk in chunks]
        ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": filename,
                "doc_id": doc_id,
                "uploader": uploaded,
                "page": chunk.metadata.get("page", None),
                "text": chunk.page_content[:2000]
            }
            for chunk in chunks
        ]

        embeddings = await asyncio.to_thread(embed_model.embed_documents, texts)

        def upsert():
            index.upsert(vectors=list(zip(ids, embeddings, metadatas)))

        await asyncio.to_thread(upsert)

        reports_collection.insert_one({
            "doc_id": doc_id,
            "filename": filename,
            "uploader": uploaded,
            "num_chunks": len(chunks),
            "uploaded_at": time.time()
        })