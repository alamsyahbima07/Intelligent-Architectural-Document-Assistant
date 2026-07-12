import chainlit as cl
import pandas as pd
import os
from src.rag_core import query_hybrid_data
from src.vlm_analyzer import analyze_construction_photo
from src.database import get_db

# Fungsi pembantu ekspor ke Excel
async def send_excel_file(data, filename):
    try:
        df = pd.DataFrame(data)
        file_path = os.path.join(os.getcwd(), filename)
        df.to_excel(file_path, index=False)
        
        if os.path.exists(file_path):
            await cl.Message(
                content=f"✅ File {filename} berhasil dibuat.",
                elements=[cl.File(path=file_path, name=filename, display="inline")]
            ).send()
        else:
            await cl.Message(content="❌ Gagal menyimpan file Excel.").send()
    except Exception as e:
        await cl.Message(content=f"❌ Error saat membuat Excel: {str(e)}").send()

@cl.on_chat_start
async def start():
    await cl.Message(
        content="# Archi AI\nHalo! Saya asisten arsitek Anda. Saya siap membantu menganalisis regulasi, material, maupun progres konstruksi di lapangan."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # 1. Jika pengguna mengunggah gambar (Analisis Konstruksi)
    if message.elements:
        image = next((el for el in message.elements if "image" in el.mime), None)
        if image:
            msg = cl.Message(content="🔍 Sedang menganalisis foto konstruksi...")
            await msg.send()
            try:
                result = analyze_construction_photo(image.path)
                response_text = (
                    f"### ✅ Analisis Selesai\n"
                    f"- **Kategori**: {result.get('category')}\n"
                    f"- **Progress**: {result.get('progress_percentage')}%\n"
                    f"- **Catatan**: {result.get('notes')}"
                )
                msg.content = response_text
                await msg.update()
                await send_excel_file([result], "Analisis_Konstruksi.xlsx")
            except Exception as e:
                msg.content = f"❌ Terjadi kesalahan saat analisis foto: {str(e)}"
                await msg.update()
    
    # 2. Fitur Ekspor/Export Schedule (Mendeteksi perintah eksport dari struktur dokumen langsung)
    elif "ekspor" in message.content.lower() or "export" in message.content.lower():
        msg = cl.Message(content="⏳ Sedang mengambil data material...")
        await msg.send()
        try:
            db = get_db()
            # Mengambil data langsung dari level dokumen (mengecualikan _id, embedding, dan text)
            cursor = db["schedule_items"].find({}, {"_id": 0, "embedding": 0, "text": 0})
            data = list(cursor)
            
            user_input = message.content.lower()
            filtered_data = []
            
            # Cek kode material (WF, FF, PT, FL) di dalam pesan
            kode_tersedia = ["wf", "ff", "pt", "fl"]
            code_query = next((k for k in kode_tersedia if k in user_input), None)
            
            if code_query:
                for item in data:
                    # Menggabungkan semua nilai field menjadi string untuk pencarian
                    combined = " ".join([str(v) for v in item.values() if v is not None]).lower()
                    if code_query in combined:
                        filtered_data.append(item)
            else:
                filtered_data = data

            if filtered_data:
                await send_excel_file(filtered_data, "Material_Schedule.xlsx")
                msg.content = f"✅ Berhasil mengekspor {len(filtered_data)} item material."
            else:
                msg.content = f"❌ Data tidak ditemukan (Total item di DB: {len(data)})."
            await msg.update()
        except Exception as e:
            msg.content = f"❌ Error: {str(e)}"
            await msg.update()

    # 3. Jika pengguna mengirim teks (Query RAG)
    else:
        msg = cl.Message(content="⏳ Mencari jawaban di dokumen regulasi...")
        await msg.send()
        try:
            response = query_hybrid_data(message.content)
            msg.content = response
            await msg.update()
        except Exception as e:
            msg.content = f"❌ Terjadi kesalahan saat memproses pertanyaan: {str(e)}"
            await msg.update()