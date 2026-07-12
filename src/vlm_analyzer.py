import os
import json
import base64
import piexif
from PIL import Image
from datetime import datetime
from groq import Groq
from src.database import get_db

# 1. Inisialisasi Client & Database
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
db = get_db()

def get_date_from_exif(image_path):
    """Mengekstrak tanggal dari metadata foto"""
    try:
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info['exif'])
        date_str = exif_dict['0th'][piexif.ImageIFD.DateTime].decode('utf-8')
        return date_str.split(' ')[0].replace(':', '-')
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")

def encode_image(image_path):
    """Mengonversi file gambar ke base64 string untuk API Groq."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_file):
    """Fungsi jembatan untuk antarmuka Streamlit."""
    temp_path = f"temp_{image_file.name}"
    with open(temp_path, "wb") as f:
        f.write(image_file.getbuffer())
    
    try:
        result = analyze_construction_photo(temp_path)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def analyze_construction_photo(image_path):
    """Menganalisis foto konstruksi menggunakan Llama 4 Scout."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Foto tidak ditemukan: {image_path}")

    date = get_date_from_exif(image_path)
    base64_image = encode_image(image_path)
    
    prompt = f"""
    Analisis foto konstruksi ini secara teknis. Berikan output dalam format JSON MURNI (tanpa teks tambahan):
    {{
        "category": "Struktur atau Arsitektur",
        "sub_category": "Contoh: Pondasi, Jendela, Finishing Dinding",
        "progress_percentage": 0,
        "notes": "Deskripsi singkat hasil pengamatan teknis"
    }}
    Tanggal foto diambil: {date}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        response_format={"type": "json_object"}
    )
    
    result_text = chat_completion.choices[0].message.content
    data = json.loads(result_text)
    
    data["file_name"] = os.path.basename(image_path)
    data["date"] = date
    
    save_analysis_to_db(data)
    return data

def save_analysis_to_db(analysis_data):
    """Menyimpan hasil analisis ke MongoDB."""
    try:
        db.construction_logs.insert_one(analysis_data)
    except Exception as e:
        print(f"Gagal menyimpan ke database: {e}")

if __name__ == "__main__":
    try:
        image_file = "foto/20241128_150834.jpg" 
        result = analyze_construction_photo(image_file)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error pada proses VLM: {e}")