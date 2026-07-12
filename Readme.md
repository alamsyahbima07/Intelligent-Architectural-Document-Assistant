# Archi AI: Asisten Arsitek Pintar

Archi AI adalah asisten berbasis AI yang dirancang untuk membantu arsitek dalam mengelola dokumen regulasi, material bangunan, serta memantau progres konstruksi di lapangan secara cerdas dan efisien.

## Fitur Utama

*   **Analisis Konstruksi (VLM):** Mengunggah foto proyek untuk mendapatkan estimasi progres dan catatan evaluasi secara otomatis.
*   **Pencarian Material (RAG):** Menjawab pertanyaan teknis mengenai spesifikasi material berdasarkan dokumen referensi.
*   **Manajemen Schedule:** Mengekspor data material (*Wall Finish*, *Floor Finish*, dll.) dari database langsung ke format Excel.
*   **Integrasi Database:** Menggunakan MongoDB Atlas untuk penyimpanan data material yang tersruktur.

## Struktur Proyek

```text
arch-assistant-ai/
├── src/                # Kode sumber utama
│   ├── database.py     # Koneksi ke MongoDB
│   ├── rag_core.py     # Logika RAG untuk dokumen regulasi
│   ├── vlm_analyzer.py # Analisis foto konstruksi
│   └── ...
├── data/               # (Diabaikan dari Git) Data lokal
├── schedule/           # Dokumen referensi (PDF)
├── app_chain.py        # Logika alur utama aplikasi (Chainlit)
├── .env                # Variabel lingkungan (API Keys)
├── .gitignore          # Konfigurasi file yang diabaikan
└── requirements.txt    # Daftar dependensi proyek


## Buat Virtual Environment
python -m venv .venv
# Aktifkan venv (Windows):
.venv\Scripts\activate


## Install Dependensi
pip install -r requirements.txt


## API Key
MONGODB_URI=your_mongodb_connection_string
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key


## Run aplikasi
chainlit run app_chain.py