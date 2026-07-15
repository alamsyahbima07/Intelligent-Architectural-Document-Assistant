import streamlit as st
import pandas as pd
import os
from src.rag_core import query_hybrid_data
from src.vlm_analyzer import analyze_construction_photo
from src.database import get_db

# Konfigurasi Page
st.set_page_config(page_title="Archi AI", layout="centered")
st.title("Archi AI")
st.subheader("Asisten Arsitek Anda")

# Inisialisasi Session State untuk chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya siap membantu menganalisis regulasi, material, maupun progres konstruksi."}
    ]

# Tampilkan chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FUNGSI PEMBANTU ---
def save_and_provide_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    with open(filename, "rb") as f:
        st.download_button(
            label=f"📥 Download {filename}",
            data=f,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- INPUT USER ---
# Upload File (Foto)
uploaded_file = st.file_uploader("Unggah foto konstruksi...", type=["jpg", "jpeg", "png"])

# Input Teks Chat
if prompt := st.chat_input("Tanya sesuatu atau ketik 'ekspor' untuk data material..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. LOGIKA ANALISIS FOTO (Jika ada file di-upload)
    if uploaded_file:
        with st.chat_message("assistant"):
            msg_placeholder = st.empty()
            msg_placeholder.markdown("🔍 Sedang menganalisis foto...")
            try:
                # Simpan sementara untuk diproses
                with open("temp_img.jpg", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                result = analyze_construction_photo("temp_img.jpg")
                response_text = f"### ✅ Analisis Selesai\n- **Kategori**: {result.get('category')}\n- **Progress**: {result.get('progress_percentage')}%\n- **Catatan**: {result.get('notes')}"
                msg_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                save_and_provide_excel([result], "Analisis_Konstruksi.xlsx")
            except Exception as e:
                st.error(f"Error: {e}")

    # 2. LOGIKA EKSPOR DATA (Jika teks mengandung 'ekspor')
    elif "ekspor" in prompt.lower() or "export" in prompt.lower():
        with st.chat_message("assistant"):
            st.write("⏳ Mengambil data material...")
            try:
                db = get_db()
                cursor = db["schedule_items"].find({}, {"_id": 0, "embedding": 0, "text": 0})
                data = list(cursor)
                
                # Filter sederhana
                filtered_data = [item for item in data if any(k in prompt.lower() for k in ["wf", "ff", "pt", "fl"])] if any(k in prompt.lower() for k in ["wf", "ff", "pt", "fl"]) else data
                
                if filtered_data:
                    st.success(f"Berhasil menemukan {len(filtered_data)} item.")
                    save_and_provide_excel(filtered_data, "Material_Schedule.xlsx")
                else:
                    st.warning("Data tidak ditemukan.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 3. LOGIKA QUERY RAG (Default)
    else:
        with st.chat_message("assistant"):
            msg_placeholder = st.empty()
            msg_placeholder.markdown("⏳ Mencari jawaban di dokumen regulasi...")
            try:
                response = query_hybrid_data(prompt)
                msg_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")