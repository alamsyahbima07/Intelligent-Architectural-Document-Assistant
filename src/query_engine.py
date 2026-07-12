import os
import json
from dotenv import load_dotenv
from src.database import get_db
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

db = get_db()
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
llm = ChatGroq(model_name="openai/gpt-oss-20b") 

def query_material_fix(pertanyaan):
    # Setup Vector Store
    vector_store = MongoDBAtlasVectorSearch(
        collection=db["schedule_items"],
        embedding=embeddings,
        index_name="schedule_index"
    )
    
    # Ambil data relevan
    docs = vector_store.similarity_search(pertanyaan, k=3)
    context_text = "\n\n".join([d.page_content for d in docs])
    
    # Prompt - Diubah untuk membuat output JSON
    prompt = ChatPromptTemplate.from_template("""
    Jawab pertanyaan berdasarkan konteks berikut dalam format JSON.
    
    Konteks:
    {context}
    
    Pertanyaan: {input}
    
    Format JSON:
    {{
        "kode": "WE-01",
        "material": "...",
        "status": "...",
        "deskripsi": "..."
    }}
    """)
    
    # Eksekusi
    formatted_prompt = prompt.format(context=context_text, input=pertanyaan)
    response = llm.invoke(formatted_prompt)
    
    # Parsing JSON dari string
    try:
        # Menghapus markdown jika ada (```json ... ```)
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except:
        return {"error": "Gagal parse JSON", "raw": response.content}

if __name__ == "__main__":
    print(json.dumps(query_material_fix("untuk material WF ada apa saja?"), indent=4))