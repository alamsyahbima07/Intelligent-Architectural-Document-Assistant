import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.database import get_db
from dotenv import load_dotenv

load_dotenv()

def ingest_regulation(file_path):
    print(f"Memproses regulasi: {file_path}...")
    
    # 1. Load PDF
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    
    # 2. Split teks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    
    # 3. Masukkan ke MongoDB (koleksi 'regulations')
    db = get_db()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=splits,
        embedding=embeddings,
        collection=db["regulations"],
        index_name="regulation_index"  # Sinkron dengan rag_core.py
    )
    print(f"Regulasi {file_path} berhasil di-index ke koleksi 'regulations'!")

if __name__ == "__main__":
    # Ganti dengan path file 
    ingest_regulation("data/Persyaratan-Teknis-Kemudahan-Bangunan-Gedung-Permen-PUPR-No.-14-Tahun-2017.pdf")