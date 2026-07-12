import os
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.database import get_db

# 1. Setup Komponen
db = get_db()
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
llm = ChatGroq(model="openai/gpt-oss-20b")

# 2. Retriever untuk Regulasi
reg_retriever = MongoDBAtlasVectorSearch(
    collection=db["regulations"], 
    embedding=embeddings, 
    index_name="regulation_index",
    text_key="text"
)

# 3. Retriever untuk Material Schedule
schedule_retriever = MongoDBAtlasVectorSearch(
    collection=db["schedule_items"], 
    embedding=embeddings, 
    index_name="schedule_index",
    text_key="text"
)

def get_context(query):
    try:
        docs = reg_retriever.similarity_search(query, k=3)
        return "\n".join([d.page_content for d in docs])
    except Exception as e:
        return ""

def get_schedule_context(query):
    try:
        docs = schedule_retriever.similarity_search(query, k=3)
        return "\n".join([d.page_content for d in docs])
    except Exception as e:
        return ""

# 4. Fungsi Utama untuk Hybrid RAG
def query_hybrid_data(user_question):
    # Mengambil konteks dari KEDUA sumber
    reg_context = get_context(user_question)
    sch_context = get_schedule_context(user_question)
    
    combined_context = f"""
    --- DATA REGULASI ---
    {reg_context}

    --- DATA MATERIAL SCHEDULE ---
    {sch_context}
    """
    
    # Prompt memaksa AI untuk stick pada konteks yang diberikan
    prompt_template = """
    Anda adalah asisten arsitek BIM. Gunakan informasi dari DATA REGULASI dan DATA MATERIAL SCHEDULE di bawah ini untuk menjawab pertanyaan.
    
    Konteks:
    {context}

    Pertanyaan:
    {question}
    
    Jika informasi tidak ditemukan di kedua sumber tersebut, katakan dengan jujur: "Informasi tidak tersedia dalam dokumen".
    Jangan gunakan pengetahuan eksternal di luar konteks ini.
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    response = chain.invoke({"context": combined_context, "question": user_question})
    return response.content