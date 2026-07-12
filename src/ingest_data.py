import pdfplumber
import pandas as pd
import os
from src.database import get_db
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document

db = get_db()
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

def ingest_schedule(file_path):
    all_docs = []
    
    print(f"Memproses file: {file_path}...")
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # table_settings untuk membantu mendeteksi struktur dengan akurat
                table = page.extract_table(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
                
                if table:
                    # Cari baris mana yang berisi header "Tag"
                    header_index = -1
                    for i, row in enumerate(table):
                        if row and "Tag" in [str(x) for x in row if x]:
                            header_index = i
                            break
                    
                    if header_index != -1:
                        headers = table[header_index]
                        # Bersihkan header dari None dan spasi
                        clean_headers = [str(h).strip() for h in headers if h is not None]
                        
                        # Proses baris data setelah header
                        for row in table[header_index + 1:]:
                            # Ambil data yang sesuai dengan jumlah header
                            row_data = [x for x in row if x is not None]
                            if len(row_data) >= len(clean_headers):
                                item = dict(zip(clean_headers, row_data[:len(clean_headers)]))
                                
                                # Filter baris kosong/tidak valid
                                clean_item = {k: v for k, v in item.items() if v and str(v).strip()}
                                if clean_item:
                                    content = ", ".join([f"{k}: {v}" for k, v in clean_item.items()])
                                    doc = Document(page_content=content, metadata=clean_item)
                                    all_docs.append(doc)

        # Ingest ke MongoDB
        if all_docs:
            vector_store = MongoDBAtlasVectorSearch(
                collection=db["schedule_items"],
                embedding=embeddings,
                index_name="schedule_index" 
            )
            vector_store.add_documents(all_docs)
            print(f"Sukses! {len(all_docs)} item material telah di-index.")
        else:
            print("Tidak ditemukan data tabel yang valid.")
            
    except Exception as e:
        print(f"Error pada proses ekstraksi: {e}")

if __name__ == "__main__":
    ingest_schedule("schedule/Finishes Schedule.pdf")