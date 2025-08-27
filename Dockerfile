# --- Stage 1: base ---
FROM python:3.10-slim
# Setta la working directory
WORKDIR /app
# Copia i file principali del progetto
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Crea la cartella /data dove sarà montato il volume persistente
# Comando per avviare il bot
CMD ["python", "main.py"]
