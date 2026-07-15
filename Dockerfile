FROM python:3.9

WORKDIR /app
COPY . .

# Menginstal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Menjalankan Chainlit
EXPOSE 7860
CMD ["chainlit", "run", "app_chain.py", "--host", "0.0.0.0", "--port", "7860"]