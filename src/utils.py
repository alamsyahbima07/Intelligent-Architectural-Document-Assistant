# src/utils.py
import pandas as pd
import pypdf

def extract_text_from_file(file):
    """Fungsi untuk membaca konten dari PDF atau Excel"""
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
            return df.to_string()
        elif file.name.endswith('.pdf'):
            reader = pypdf.PdfReader(file)
            # Mengambil teks dari semua halaman
            return "\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        return f"Gagal membaca file: {str(e)}"
    return ""